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
        userName = message.author.name


        if len(messageContent) == 1:
            return
        command = messageContent[1]
        
        match command:
            case "weather":
                weatherResponse = await weather(messageContent, userId)
                await message.channel.send(weatherResponse)
            case "defaultLocation":
                locationResponse = await addDefaultCity(messageContent, userId, userName)
                await message.channel.send(locationResponse)

async def weather(messageContent, userId):
    # Get default city from database depending on the user, otherwise set to Sydney
    cur.execute(f"""SELECT defaultCity
                      FROM DefaultCity
                     WHERE userID = {userId}""")
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
            
async def addDefaultCity(messageContent, userId, userName):
    if not len(messageContent) > 2:
        return "No city was selected"

    city = " ".join(messageContent[2:])

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weatherAPIKey}&units=metric"
    async with aiohttp.ClientSession() as session:  # Creates asynchronous HTTP session
        async with session.get(url) as response: # Sends a get request to the URL
            if response.status != 200:  # Code 200 is returned for successful processing
                return "City was not found"

    cur.execute(f"""SELECT defaultCity
                      FROM DefaultCity
                     WHERE userID = {userId}""")
    result = cur.fetchone()
    if result != None:
        cur.execute(f"""UPDATE DefaultCity
                           SET defaultCity = '{city}'
                        WHERE userID = {userId}""")
    else:
        cur.execute(f"""INSERT INTO DefaultCity (userID, defaultCity)
                         VALUES ({userId}, '{city}');""")
    
    return f"Default city for {userName} updated to {city}"

client.run(token)