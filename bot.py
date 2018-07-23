import discord
from discord.ext import commands
import giphypop
from giphypop import translate
import requests
import json
import aiohttp
import pytz
from icalendar import Calendar, Event
from datetime import datetime

from config import TOKEN, giphyKey

from utils import isPlayer, nameCheck

#TO DO LIST
#!addme - add list of people to be notified for game - DONE
#!removeme - removes from notification list - DONE
#!next - shows when next game is
#!gameday - shows games and times of the day
#!player - gets general player info - DONE
#!playerstats - gets player stats for a certain year. May need to adjust for position

#!teamstats(maybe) - shows stats for a certain team

#Description
description = 'Bot for Los Angeles Rams discord server'

#Sets up bot
#print("Starting up bot")
bot = commands.Bot(command_prefix = '!', description = description, pm_help=True)

#Remove the help command
bot.remove_command('help')

#Giphy object
g = giphypop.Giphy(api_key=giphyKey)

#List for the !addme command
userList = []

#Logs in
@bot.event
async def on_ready():
    """ Logs in """ 
    print('Logged in')
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(game=discord.Game(name='bradykedge.com', type=0))
    print('--------')

#Help Comman
@bot.event
async def on_message(message):
    """Gives help with bot"""
    #!help Command
    if message.content.startswith('!help'):
        helpString = "Below is a list of commands for the bot. [required input] (optional input). Contact wh33lybrdy with questions or concerns.\n--------------\n**!help:** Get list of commands\n**!gif [search terms]:** Searches for gif of given terms\n**!player [name]:** Gets general information of a player"
        await bot.send_message(message.author, helpString)
    await bot.process_commands(message)

#Basic hello command for testing
@bot.command()
async def hello():
    """ Says world """
    await bot.say("world")

#Gets gif and says URL thereby posting the gif
@bot.command()
async def gif(*, message: str):
    """ Fetches gif """
    img = translate(message, api_key=giphyKey)
    url = img.url
    await bot.say(url)

#NFL Commands

#Gets general player info
@bot.command()
async def player(*,  message: str):
    """Gets general player info"""
    try:
        name = message.split(" ")
        if nameCheck(name) == 1:
            print("Last name")
            async with aiohttp.get('http://api.suredbits.com/nfl/v0/players/{}'.format(name[0])) as r:
                pName = await r.text()
        elif nameCheck(name) == 2:
            print("Full name")
            async with aiohttp.get('http://api.suredbits.com/nfl/v0/players/{}/{}'.format(name[1], name[0])) as r:
                pName = await r.text()
        else:
            print("Too many")
            
        player_json = json.loads(pName)
            
        if isPlayer(player_json):
            player = player_json[0]
            print(player)
            botString = "```Name: {}\nNumber: {}\nTeam: {}\nPosition: {}\nStatus: {}\nYears Pro: {}\nCollege: {}\nHeight (in.): {}\nWeight: {}\nBorn: {}\n```NFL Profile: {}".format(player['fullName'], player['uniformNumber'], player['team'], player['position'], player['status'], player['yearsPro'], player['college'], player['height'], player['weight'], player['birthDate'], player['profileUrl'])
            await bot.say(botString)
        else:
            print("In error")
            await bot.say("No player found")
    except:
        await bot.say("An error happened please try again")
    
    
    

#Adds user to list of Rams game reminders
@bot.command(pass_context = True)
async def addme(ctx):
    #!addme command
    user = ctx.message.author.id
    pm = await bot.get_user_info(user)

    try:
        with open('userList.json') as userFile:
            data = json.load(userFile)
            
            if user in data:
                #If user in file already, tell them and return
                await bot.send_message(pm, "It seems you are already in the list. Could this be an error? PM wh33lybrdy if so")
                return
                
            data.append(user)
        
        await bot.send_message(pm, "You've been added to the game reminder list. To remove yourself do `!removeme`")
        
        with open('userList.json', 'w') as outfile:
            json.dump(data, outfile)
    except:
        await bot.say('An error happened, please try again or contact @wh33lybrdy')
    

#Removes users from list of Rams game reminders
@bot.command(pass_context = True)
async def removeme(ctx):
    user = ctx.message.author.id

    try:
        pm = await bot.get_user_info(user)
        
        with open('userList.json') as userFile:
            data = json.load(userFile)
            print(data)
            print(type(data))

            if user in data:
                data.remove(user)
            else:
                #If user not found then tell them and return
                await bot.send_message(pm, "Could not find you in UserList. If you think this is an error message wh33lybrdy")
                return

        with open('userList.json', 'w') as outfile:
            json.dump(data, outfile)
        
        await bot.send_message(pm, "You have been removed from game reminders")
    except:
        await bot.say('An error happened, please try again or contact @wh33lybrdy')
    

    

@bot.command(pass_context = True)
async def next(ctx):
    #Calendar stuff
    g = open('rams.ics', 'rb')
    sched = Calendar.from_ical(g.read())
    for component in sched.walk():
        if component.name == "VEVENT":
            print(component.get('summary'))

#Runs the bot 
bot.run(TOKEN) 
