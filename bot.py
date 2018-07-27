import discord
from discord.ext import commands
import giphypop
from giphypop import translate
import requests
import json
import asyncio
import aiohttp
import pytz
import datetime
from datetime import date
from icalendar import Calendar, Event
from datetime import datetime

from config import TOKEN, giphyKey

from utils import isPlayer, nameCheck

#TO DO LIST
#!addme - add list of people to be notified for game - DONE
#!removeme - removes from notification list - DONE
#!next - shows when next game is - DONE
#!schedule - shows games and times of the day - DONE
#!player - gets general player info - DONE
#!playerstats - gets player stats for a certain year. May need to adjust for position

#MAYBE
#!teamstats(maybe) - shows stats for a certain team
#!standings - shows standings for certain divison/conference

#Description
description = 'Bot for Los Angeles Rams discord server'

#Sets up bot
#print("Starting up bot")
bot = commands.Bot(command_prefix = '!', description = description, pm_help=True)

#Remove the help command
bot.remove_command('help')

#Giphy object
g = giphypop.Giphy(api_key=giphyKey)

#Logs in
@bot.event
async def on_ready():
    """ Logs in """ 
    print('Logged in')
    print(bot.user.name)
    print(bot.user.id)
    #await bot.change_presence(game=discord.Game(name='bradykedge.com', type=0))
    print('--------')

#Help Command
bot.remove_command('help')
@bot.command()
async def help(ctx, member: discord.Member = None):
    user = ctx.author.id
    helpString = "Below is a list of commands for the bot. [required input] (optional input). Contact wh33lybrdy with questions or concerns.\n--------------\n**!help:** Get list of commands\n**!gif [search terms]:** Searches for gif of given terms\n**!player [name]:** Gets general information of a player"
    await bot.get_user(user).send(helpString)

#Basic hello command for testing
@bot.command()
async def hello(ctx):
    """ Says world """
    await ctx.send("world")

#Gets gif and says URL thereby posting the gif
@bot.command()
async def gif(ctx, *, message: str):
    """ Fetches gif """
    img = translate(message, api_key=giphyKey)
    url = img.url
    await ctx.send(url)

#NFL Commands

#Gets general player info
@bot.command()
async def player(ctx, *, message: str):
    """Gets general player info"""
    try:
        name = message.split(" ")
        if nameCheck(name) == 1:
            print("Last name")
            async with aiohttp.ClientSession() as session:
                async with session.get('http://api.suredbits.com/nfl/v0/players/{}'.format(name[0])) as r:
                    pName = await r.text()
        elif nameCheck(name) == 2:
            print("Full name")
            async with aiohttp.ClientSession() as session:
                async with session.get('http://api.suredbits.com/nfl/v0/players/{}/{}'.format(name[1], name[0])) as r:
                    pName = await r.text()
        else:
            print("Too many")
            
        player_json = json.loads(pName)
            
        if isPlayer(player_json):
            player = player_json[0]
            print(player)
            botString = "```Name: {}\nNumber: {}\nTeam: {}\nPosition: {}\nStatus: {}\nYears Pro: {}\nCollege: {}\nHeight (in.): {}\nWeight: {}\nBorn: {}\n```NFL Profile: {}".format(player['fullName'], player['uniformNumber'], player['team'], player['position'], player['status'], player['yearsPro'], player['college'], player['height'], player['weight'], player['birthDate'], player['profileUrl'])
            await ctx.send(botString)
        else:
            print("In error")
            await ctx.send("No player found")
    except:
        await ctx.send("An error happened please try again")
    
#Adds user to list of Rams game reminders
@bot.command()
async def addme(ctx, member: discord.Member = None):
    #!addme command
    user = ctx.author.id

    try:
        with open('userList.json') as userFile:
            print('opened file')
            data = json.load(userFile)
            
            if user in data:
                #If user in file already, tell them and return
                print('Already in list')
                await bot.get_user(user).send("It seems you are already in the list. Could this be an error? PM wh33lybrdy if so")
                return
                
            data.append(user)
        print('Added')
        await bot.get_user(user).send("You've been added to the game reminder list. To remove yourself do `!removeme`")
        
        with open('userList.json', 'w') as outfile:
            json.dump(data, outfile)
    except:
        await ctx.send('An error happened, please try again or contact @wh33lybrdy')

#Removes users from list of Rams game reminders
@bot.command()
async def removeme(ctx, member: discord.Member = None):
    #!removeme command
    user = ctx.author.id

    try:
        with open('userList.json') as userFile:
            data = json.load(userFile)
            print(data)
            print(type(data))

            if user in data:
                data.remove(user)
            else:
                #If user not found then tell them and return
                await bot.get_user(user).send("Could not find you in UserList. If you think this is an error message wh33lybrdy")
                return

        with open('userList.json', 'w') as outfile:
            json.dump(data, outfile)
        
        await bot.get_user(user).send("You have been removed from game reminders")
    except:
        await ctx.send('An error happened, please try again or contact @wh33lybrdy')

@bot.command()
async def schedule(ctx, message: str = None):
    #ICS format is YYYYMMDD
    gameday_str = ""

    try:
        if message:
            #await ctx.send('We got the message: {}'.format(message))
            #user_date = datetime.strptime(message, '%Y%m%d').strftime('%m/%d/%Y')
            today = date.today()
            user_date = datetime.strptime(message, '%Y%m%d').date()
            #user_date = user_date.date()
            print(user_date)
        else:
            #await ctx.send("We got nothing")
            today = date.today()
            user_date = today
            print(today)
            #Calendar stuff

        g = open('nfl.ics', 'rb')
        sched = Calendar.from_ical(g.read())
        for component in sched.walk('VEVENT'):
            if component['DTSTART'].dt.date() == user_date:
                print('{}: {} CST'.format(component['SUMMARY'], component['DTSTART'].dt.strftime("%d/%m/%Y %I:%M")))
                gameday_str += '{}: {} CST\n'.format(component['SUMMARY'], component['DTSTART'].dt.strftime("%d/%m/%Y %I:%M"))
            elif component['DTSTART'].dt.date() > user_date:
                break

        if not gameday_str:
            await ctx.send("No games today")
        else:
            await ctx.send("```{}```".format(gameday_str))
        
    except:
        await ctx.send("An error happened. Please contact @wh33lybrdy")
        
    
    
        

@bot.command()
async def next(ctx):
    #Calendar stuff
    try:
        today = date.today()
        print(today)
        g = open('rams.ics', 'rb')
        sched = Calendar.from_ical(g.read())
        for component in sched.walk('VEVENT'):
            print('Found: {}'.format(component['DTSTART'].dt.date()))
            if component['DTSTART'].dt.date() >= today:
                print('Next game is: {}: {} CST'.format(component['SUMMARY'], component['DTSTART'].dt.strftime("%d/%m/%Y %I:%M")))
                await ctx.send('{}: {} CST'.format(component['SUMMARY'], component['DTSTART'].dt.strftime("%d/%m/%Y %I:%M")))
                break
    except:
        await ctx.send('An error happened. Please contact @wh33lybrdy')
    
        #if component.name == "VEVENT":
            #print(component['DTSTART'].dt)


#Runs the bot 
bot.run(TOKEN) 
