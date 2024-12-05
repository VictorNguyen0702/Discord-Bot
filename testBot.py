import discord
import json

with open('config.json', 'r') as config:
    configData = json.load(config)
token = configData["token"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(token)