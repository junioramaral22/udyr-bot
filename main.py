from urllib import request
import discord
from discord.ext import commands
import os
from decouple import config

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

testing = False

client = commands.Bot(command_prefix = "$", case_insensitive = True, intents=intents)

client.remove_command('help')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')



@client.event
async def on_member_join(member):

    msg = f"Bem vindo {member.mention}! Faz o Uga e adore Udyr"

    await member.send(msg)


TOKEN = config("TOKEN_SECRETO")

client.run(TOKEN)
