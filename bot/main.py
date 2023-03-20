import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import os
from dotenv import load_dotenv

async def send_it(message):
    print(f"sending message: {message}")
    await bot.get_channel(int(os.getenv('DISCORD_REPORTING_CHANNEL_ID'))).send(str(message))
    return True

load_dotenv()

intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(intents=intents)

# Replace with your bot token
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
# Replace with your "Established User" role ID
ESTABLISHED_USER_ROLE_ID = os.getenv('ESTABLISHED_USER_ROLE_ID')
# Debug mode check
DEBUG = os.getenv('DEBUG')
# name of discord bot
BOT_NAME = os.getenv('BOT_NAME') | bot.user.name

# Store a dictionary of users that are being checked
users_to_check = {}

@bot.event
async def on_ready():
    if(DEBUG is not None and DEBUG == "1"):
        await send_it("Discord Bot {BOT_NAME} initialized")

#global user object update
@bot.event
async def on_user_update(before, after):
    if (DEBUG == "1"):
        print("on_user_update")
    if before.name != after.name:
        await send_it(f"User [ {str(before.name)} ] changed their name to [{str(after.name)}].")

@bot.event
async def on_member_join(member):
    await check_member_roles(member)

#server member object update
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        await check_member_roles(after)

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:  # member connected
        await check_member_roles(member)

#get whats changed for user / members
def get_user_changes(before, after):
    changes = []
    before_attributes = vars(before)
    after_attributes = vars(after)

    for attribute, before_value in before_attributes.items():
        after_value = after_attributes.get(attribute, None)
        if before_value != after_value:
            changes.append((attribute, before_value, after_value))

    return changes

#actual check if this yuser has specific role
async def check_member_roles(member):
    established_role = discord.utils.get(member.roles, id=ESTABLISHED_USER_ROLE_ID)
    if established_role is None:
        users_to_check[member.id] = member.joined_at + datetime.timedelta(days=30)
    else:
        users_to_check.pop(member.id, None)


bot.run(TOKEN)
