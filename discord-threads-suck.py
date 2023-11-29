import discord
import asyncio
import json
from pathlib import Path
from discord.ext import commands

defaultInterval = 72.0 # 3 days
defaultMessage = "**Ding dong**! It's the bot.\nI have nothing interesting for you today.\nI'm posting this so Discord doesn't hide the thread from you, sorry.\n\nAnnoyed by this? So am I.\n[Tell Discord to fix this](<https://support.discord.com/hc/en-us/community/posts/19396627158423-Threads-forums-forcibly-auto-hiding-after-a-week-renders-the-feature-completely-useless-for-neurodivergents-with-ADHD-and-focus-issues>)"

active = False
active_tasks = {}

# store each channel we want to ping
targets = []

# Read state information from JSON
if Path("targets.json").exists():
    print("Reading targets from targets.json...")
    with open('targets.json', 'r') as json_file:
        data_from_file = json.load(json_file)

    for target_data in data_from_file:
        print(target_data)
        targets.append(target_data)

# Define intents
intents = discord.Intents.default()
intents.message_content = True  # Allow message events

# Create a bot instance with intents
bot = discord.Client(intents=intents)

# Post the update message
# This function runs asynchronously
async def post_message(interval, message, channel_id):
    while True:
        channel = bot.get_channel(channel_id)
        await channel.send(message)
        await asyncio.sleep(interval * 60 * 60)

# Save all state information to JSON
def saveTargetsToJson():
    with open('targets.json', 'w') as json_file:
        json.dump(targets, json_file, indent=2)

# Event to respond to on_ready event
@bot.event
async def on_ready():
    global active
    print(f'Logged in as {bot.user.name}')
    if not active:
        for target in targets:
            task = asyncio.create_task(post_message(target['interval'], target['message'], target['id']))
            active_tasks[target['id']] = task
        active = True

# Event to respond to on_message event
@bot.event
async def on_message(message):
    if(message.author.bot == False):
        # Check if the message is a ping
        if message.content.lower() == '!keepalive':
            # check if it already exists
            exists = False
            for x in targets:
                if(x['id'] == message.channel.id):
                    exists = True
                    print("Disabled keepalive in channel ID: " + str(x['id']))
                    await message.channel.send("Disabled keepalive in channel ID: " + str(x['id']))
                    task = active_tasks.get(x['id'])
                    if task:
                        task.cancel()
                        del active_tasks[x['id']]
                    targets.remove(x)
            
            if(exists == False):
                target = {
                    'interval': defaultInterval,
                    'message': defaultMessage,
                    'id': message.channel.id
                }
                targets.append(target)

                task = asyncio.create_task(post_message(target['interval'], target['message'], target['id']))
                active_tasks[target['id']] = task
                print("Now keeping this channel ID alive: " + str(target['id']) + "\nInterval (hours): " + str(target['interval']))
                await message.channel.send("Now keeping this channel ID alive: " + str(target['id']) + "\nInterval (hours): " + str(target['interval']))
            
            # Save to JSON
            saveTargetsToJson()

        if message.content.lower() == '!debug':
            output = "**Registered targets**:\n\n"
            for target in targets:
                output = output + "ID: " + str(target['id']) + "\n" + "Interval (hours): " + str(target['interval']) + "\n\n"
            output += "**Active tasks**:\n"
            for target in active_tasks:
                output = output + str(target) + "\n"
            print(output)
            await message.channel.send(output)

        # Change interval
        if message.content.lower().startswith('!interval '):
            interval = float(message.content.lower().split("!interval ",1)[1])
            task = active_tasks.get(message.channel.id)
            if task:
                task.cancel()
                del active_tasks[message.channel.id]
                for target in targets:
                    if target['id'] == message.channel.id:
                        target['interval'] = interval
                        task = asyncio.create_task(post_message(target['interval'], target['message'], target['id']))
                        active_tasks[target['id']] = task
                        print("New interval (hours) for ID "+str(target['id'])+": " + str(interval))
                        await message.channel.send("New interval (hours) for ID "+str(target['id'])+": " + str(interval))
                        saveTargetsToJson()
            else:
                await message.channel.send("You need to use !keepalive first!")

with open("token.txt", 'r') as file:
    token = file.read()
    print("Read token from token.txt: " + token)
    bot.run(token)
