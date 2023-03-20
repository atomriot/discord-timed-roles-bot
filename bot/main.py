import asyncio
import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime, timedelta, time
import pytz

load_dotenv()
DEBUG = os.getenv('DEBUG')
TOKEN = os.getenv('DISCORD_TOKEN')
DAYS_WINDOW = os.getenv('DAYS_WINDOW')
TRIGGER_HOUR = os.getenv('TRIGGER_HOUR')

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

def add_user_to_db(user_id, join_date, has_established_role):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.callproc('add_user', (user_id, join_date, has_established_role))
    connection.commit()
    cursor.close()
    connection.close()

def update_user_in_db(user_id, has_established_role):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.callproc('update_user', (user_id, has_established_role))
    connection.commit()
    cursor.close()
    connection.close()

@bot.event
async def on_ready():
    if DEBUG == "1":
        print(f'{bot.user} has connected to Discord!')
    apply_established_role.start()

@bot.event
async def on_member_join(member):
    add_user_to_db(member.id, datetime.utcnow(), False)

@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        check_and_apply_established_role(after)

async def check_and_apply_established_role(member):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT join_date, has_established_role FROM users WHERE user_id = %s", (member.id,))
    result = cursor.fetchone()

    if result is not None:
        join_date, has_established_role = result
        if not has_established_role and datetime.utcnow() - join_date >= timedelta(days=int(DAYS_WINDOW)):
            established_role = discord.utils.get(member.guild.roles, name="Established User")
            if established_role not in member.roles:
                await member.add_roles(established_role)
                update_user_in_db(member.id, True)

    cursor.close()
    connection.close()

def next_run_time(hour, minute, timezone):
    now = datetime.now(timezone)
    next_run = datetime.combine(now.date(), time(hour, minute), tzinfo=timezone)
    if next_run <= now:
        next_run += timedelta(days=1)
    return next_run

async def wait_until_next_run_time(hour, minute, timezone):
    next_run = next_run_time(hour, minute, timezone)
    await asyncio.sleep((next_run - datetime.now(timezone)).total_seconds())

@tasks.loop(hours=1)
async def apply_established_role():
    cst = pytz.timezone('US/Central')
    if datetime.now(cst).hour == TRIGGER_HOUR:
        for guild in bot.guilds:
            for member in guild.members:
                await check_and_apply_established_role(member)

apply_established_role.before_loop
async def before_apply_established_role():
    await bot.wait_until_ready()
    cst = pytz.timezone('US/Central')
    await wait_until_next_run_time
