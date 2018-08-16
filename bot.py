import discord
from discord.ext import commands
import giphypop
from giphypop import translate
import requests
import base64
import json
import asyncio
import aiohttp
import pytz
import datetime
from icalendar import Calendar, Event
from datetime import date, timedelta

from config import TOKEN, giphyKey, API_Key

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
    helpString = "Below is a list of commands for the bot. [required input] (optional input). Contact wh33lybrdy with questions or concerns.\n--------------\n**!help:** Get list of commands\n**!gif [search terms]:** Searches for gif of given terms\n**!player [name]:** Gets general information of a player\n**!next:** Get day and time of next Rams game\n**!schedule (YYYYMMDD):** Gets list of games for given date. If no date given, bot will get games of current day\n**!addme:** Add yourself to list of users to be PM'd 30 minutes before the next Rams game starts\n**!removeme:** Remove yourself from reminder list"
    await bot.get_user(user).send(helpString)

#Provides info for the bot
@bot.command()
async def info(ctx):
    embed = discord.Embed(title="RamsBot", description="Bot for the /r/LosAngelesRams discord server. List of commands [required] (optional) are:", color=0xeee657)

    embed.add_field(name="!help", value="PM's a list of commands for the bot", inline=False)
    embed.add_field(name="!gif [search terms]", value="Searches for gif of given terms", inline=False)
    embed.add_field(name="!player [name]", value="Gets general information of a player", inline=False)
    embed.add_field(name="!next", value="Get day and time of next Rams game", inline=False)
    embed.add_field(name="!schedule (YYYYMMDD)", value="Gets list of games for given date. If no date given, bot will get games of current day", inline=False)
    embed.add_field(name="!addme", value="Add yourself to list of users to be PM'd 30 minutes before the next Rams game starts", inline=False)
    embed.add_field(name="!removeme", value="Remove yourself from reminder list", inline=False)

    await ctx.send(embed=embed)

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
    url = 'https://api.mysportsfeeds.com/v2.0/pull/nfl/players.json'
    headers = { "Authorization": "Basic " + base64.b64encode('{}:{}'.format(API_Key, 'MYSPORTSFEEDS').encode('utf-8')).decode('ascii')}
    params = { "player" : "key" }

    try:
        name = message.split(" ")
        if nameCheck(name) == 1:
            #print("Last name")
            name = "{}".format(name[0])
            params['player'] = name
            #print(params['player'])
            #print('Making request')
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, params=params) as r:
                    #print(r.status)
                    data = await r.text()
            
            pName = json.loads(data)
            botString = "```Name: {} {}\nNumber: {}\nTeam: {}\nPosition: {}\nHeight: {}\nWeight: {}\nBorn: {}\nAge: {}\nHome Town: {}\n```{}".format(pName['players'][0]['player']['firstName'], pName['players'][0]['player']['lastName'], pName['players'][0]['player']['jerseyNumber'], pName['references']['teamReferences'][0]['name'], pName['players'][0]['player']['position'], pName['players'][0]['player']['height'], pName['players'][0]['player']['weight'], pName['players'][0]['player']['birthDate'], pName['players'][0]['player']['age'], pName['players'][0]['player']['birthCity'], pName['players'][0]['player']['officialImageSrc'])
            #print(botString)
            await ctx.send(botString)
            
        elif nameCheck(name) == 2:
            #print("Full name")
            name = "{}-{}".format(name[0], name[1])
            #print(name)
            params['player'] = name
            #print('Making request')
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, params=params) as r:
                    #print(r.status)
                    data = await r.text()
            
            pName = json.loads(data)
            botString = "```Name: {} {}\nNumber: {}\nTeam: {}\nPosition: {}\nHeight: {}\nWeight: {}\nBorn: {}\nAge: {}\nHome Town: {}\n```{}".format(pName['players'][0]['player']['firstName'], pName['players'][0]['player']['lastName'], pName['players'][0]['player']['jerseyNumber'], pName['references']['teamReferences'][0]['name'], pName['players'][0]['player']['position'], pName['players'][0]['player']['height'], pName['players'][0]['player']['weight'], pName['players'][0]['player']['birthDate'], pName['players'][0]['player']['age'], pName['players'][0]['player']['birthCity'], pName['players'][0]['player']['officialImageSrc'])
            #print(botString)
            await ctx.send(botString)
    except Exception as ex:
        print("Something went wrong")
        print(ex)
    
#Adds user to list of Rams game reminders
@bot.command()
async def addme(ctx, member: discord.Member = None):
    #!addme command
    user = ctx.author.id

    try:
        with open('userList.json') as userFile:
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
            #user_date = datetime.strptime(message, '%Y%m%d').strftime('%m/%d/%Y'
            today = date.today()
            user_date = datetime.datetime.strptime(message, '%Y%m%d').date()
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
                gameday_str += '**{}**: {} CST\n'.format(component['SUMMARY'], component['DTSTART'].dt.strftime("%m/%d/%Y - %I:%M"))
            elif component['DTSTART'].dt.date() > user_date:
                break

        if not gameday_str:
            await ctx.send("No games today")
        else:
            await ctx.send(gameday_str)
        
    except:
        await ctx.send("An error happened. Please contact @wh33lybrdy")

@bot.command()
async def next(ctx):
    #Calendar stuff
    try:
        today = date.today()
        #print(today)
        g = open('rams.ics', 'rb')
        sched = Calendar.from_ical(g.read())
        for component in sched.walk('VEVENT'):
            print('Found: {}'.format(component['DTSTART'].dt.date()))
            if component['DTSTART'].dt.date() >= today:
                #print('Next game is: {}: {} CST'.format(component['SUMMARY'], component['DTSTART'].dt.strftime("%d/%m/%Y %I:%M")))
                await ctx.send('{}: {} CST'.format(component['SUMMARY'], component['DTSTART'].dt.strftime("%m/%d/%Y - %I:%M")))
                break
    except:
        await ctx.send('An error happened. Please contact @wh33lybrdy')
    

async def gameCheck():
    
    
    
    nextGame = True
    await asyncio.sleep(10)
    print("Running loop")
    #Always runs
    while True:
        #Get today
        today = datetime.datetime.now(tz=pytz.UTC)
        #print(today)
        #Get next game
        while nextGame == True:
            g = open('rams.ics', 'rb')
            sched = Calendar.from_ical(g.read())
            for component in sched.walk('VEVENT'):
                #print('Found: {}'.format(component['DTSTART'].dt))

                #Find closest game after today
                if component['DTSTART'].dt >= today:
                    print('Next game is: {}: {} CST'.format(component['SUMMARY'], component['DTSTART'].dt.strftime("%m/%d/%Y %I:%M")))
                    gameString = '{}: {} CST'.format(component['SUMMARY'], component['DTSTART'].dt.strftime("%m/%d/%Y %I:%M"))
                    game = component['DTSTART'].dt
                    #Set flag to false
                    nextGame = False
                    break

        #Get time till next game
        till_game = game - today
        #print(till_game.total_seconds())

        if till_game.total_seconds() <= 1800:
            print("TIME TO NOTIFY")
            with open('userList.json') as userFile:
                data = json.load(userFile)

            for user in data:
                await bot.get_user(user).send("{} is starting in 30 minutes".format(gameString))
            
            await asyncio.sleep(43200)
            nextGame = True
        
        await asyncio.sleep(30)
                
    
    

bot.loop.create_task(gameCheck())
        
#Runs the bot 
bot.run(TOKEN) 
