import discord
import json
import sqlite3

with open('config.json', 'r') as config:
    configData = json.load(config)
token = configData["discordToken"]

botName = "adb" # Change this to change the command prefix for for the bot

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents = intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content.startswith(f'${botName}'):
        messageContent = message.content.split(" ")
        userId = message.author.id

        if len(messageContent) == 1:
            return
        command = messageContent[1]
        
        match command:
            case "weather":
                weatherResponse = await weather(messageContent, userId)
                await message.channel.send(weatherResponse)
            case "defaultLocation":
                return
        await message.channel.send('Hello!')

@client
def weather(messageContent):
    pass

client.run(token)