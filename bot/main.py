import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime, timedelta, time
import pytz

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
REQUIRED_DAYS = int(os.getenv('REQUIRED_DAYS'))
TASK_HOUR = int(os.getenv('TASK_HOUR'))
ROLE_ID = int(os.getenv('ROLE_ID_TO_APPLY'))
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    apply_established_role.start()

@bot.event
async def on_member_join(member):
    add_user_to_db(member.id, datetime.utcnow(), False)

@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        await check_and_apply_established_role(after)

def set_run_status(run_date, num_users_updated, status, error_message=None):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.callproc("add_run_status", (run_date, num_users_updated, status, error_message))
    
    connection.commit()
    cursor.close()
    connection.close()

def add_user_to_db(user_id, join_date, has_established_role):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.callproc("add_user", (user_id, join_date, has_established_role))
    
    connection.commit()
    cursor.close()
    connection.close()

def update_user_in_db(user_id, has_established_role):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.callproc("update_user", (user_id, has_established_role))
    
    connection.commit()
    cursor.close()
    connection.close()

def get_users_to_update(required_days):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.callproc("get_users_to_update", (required_days,))
    
    results = cursor.stored_results()
    user_ids_to_update = [row[0] for row in results.fetchone()]
    
    cursor.close()
    connection.close()
    
    return user_ids_to_update

async def check_and_apply_established_role(member):
    established_role = discord.utils.get(member.guild.roles, id=ROLE_ID)

    has_role = any(role == established_role for role in member.roles)
    join_date = member.joined_at
    days_since_join = (datetime.utcnow() - join_date).days

    if not has_role and days_since_join >= REQUIRED_DAYS:
        await member.add_roles(established_role)
        update_user_in_db(member.id, True)

async def apply_roles_from_db():
    user_ids_to_update = get_users_to_update(REQUIRED_DAYS)
    
    num_users_updated = 0

    for guild in bot.guilds:
        for user_id in user_ids_to_update:
            member = guild.get_member(user_id)
            if member is not None:
                await check_and_apply_established_role(member)
                num_users_updated += 1

    return num_users_updated

@tasks.loop(hours=1)
async def apply_established_role():
    cst = pytz.timezone('US/Central')
    if datetime.now(cst).hour == TASK_HOUR:
        try:
            num_users_updated = await apply_roles_from_db()
            set_run_status(datetime.utcnow(), num_users_updated, 'success')
        except Exception as e:
            set_run_status(datetime.utcnow(), 0, 'failure', str(e))

async def wait_until_next_run_time(hour, minute, tz):
    now = datetime.now(tz)
    next_run = datetime(now.year, now.month, now.day, hour, minute, tzinfo=tz)

    if now > next_run:
        next_run += timedelta(days=1)

    await discord.utils.sleep_until(next_run.astimezone(datetime.utcnow().tzinfo))

apply_established_role.before_loop
async def before_apply_established_role():
    await bot.wait_until_ready()
    cst = pytz.timezone('US/Central')
    await wait_until_next_run_time(TASK_HOUR, 0, cst)

bot.run(TOKEN)
