import discord
import json
import aiohttp
import sqlite3

with open('config.json', 'r') as config:
    configData = json.load(config)

# Configuration Data
botName = "placeholder" # Change this to change the command prefix for for the bot
token = configData["discordToken"]
weatherAPIKey = configData["weatherKey"]

# Create client instance
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents = intents)
conn = sqlite3.connect("userData.db")
cur = conn.cursor()


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
                pass

async def weather(messageContent, userID):
    # Get default city from database depending on the user, otherwise set to Sydney
    cur.execute(f"""SELECT defaultLocation
                      FROM DefaultLocation
                     WHERE userID = {userID}""")
    result = cur.fetchone()
    if result != None:
        defaultCity = result[0]
    else:
        defaultCity = "Sydney"

    city = " ".join(messageContent[2:]) if len(messageContent) > 2 else defaultCity
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weatherAPIKey}&units=metric"

    async with aiohttp.ClientSession() as session:  # Creates asynchronous HTTP session
        async with session.get(url) as response: # Sends a get request to the URL
            if response.status == 200:  # Code 200 is returned for successful processing
                data = await response.json() # Wait for conversion to a python dictionary
                weather_info = (
                    f"Weather in {data['name']}:\n"
                    f"Temperature: {data['main']['temp']}°C\n"
                    f"Description: {data['weather'][0]['description'].capitalize()}"
                )
                return weather_info
            else:
                return f"Could not fetch weather for {city}"
            
client.run(token)