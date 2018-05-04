import discord
from discord.ext import commands
import giphypop
from giphypop import translate
import requests
import json
import aiohttp
from config import TOKEN

#TO DO LIST
#!addme - add list of people to be notified for game
#!removeme - removes from notification list
#!next - shows when next game is
#!gameday - shows games and times of the day
#!player - gets general player info - DONE
#!playerstats - gets player stats for a certain year. May need to adjust for position

#!teamstats(maybe) - shows stats for a certain team

#Description
description = 'Bot for Los Angeles Rams discord server'

#Sets up bot
bot = commands.Bot(command_prefix = '!', description = description, pm_help=True)

#Remove the help command
bot.remove_command('help')

#Giphy object
g = giphypop.Giphy()

#Logs in
@bot.event
async def on_ready():
    """ Logs in """ 
    print('Logged in')
    print(bot.user.name)
    print(bot.user.id)
    print('--------')

@bot.event
async def on_message(message):
    """Gives help with bot"""
    if message.content.startswith('!help'):
        await bot.send_message(message.author, "I can help you")
    await bot.process_commands(message)

#Basic hello command
@bot.command()
async def hello():
    """ Says world """
    await bot.say("world")

#Gets gif and pastes url
@bot.command()
async def gif(*, message: str):
    """ Fetches gif """
    img = translate(message)
    url = img.url
    await bot.say(url)

#NFL Commands

#Gets general player info
@bot.command()
async def player(*,  message: str):
    """Gets general player info"""
    #await bot.say("Getting player info")
    #print(message)
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
        #print(player_json[0]['weight'])
        player = player_json[0]
        print(player)
        botString = "```Name: {}\nNumber: {}\nTeam: {}\nPosition: {}\nStatus: {}\nYears Pro: {}\nCollege: {}\nHeight (inches): {}\nWeight: {}\nBorn: {}\n```NFL Profile: {}".format(player['fullName'], player['uniformNumber'], player['team'], player['position'], player['status'], player['yearsPro'], player['college'], player['height'], player['weight'], player['birthDate'], player['profileUrl'])
        await bot.say(botString)
    else:
        print("In error")
        await bot.say("No player found")


#Functions

def isPlayer(playerFile):
    if len(playerFile) == 0:
        return False
    else:
        return True

#Checks if just first or last name entered by counting
def nameCheck(nameInput):
    number_of_names = len(nameInput)
    #print(number_of_names)
    return number_of_names
    

#Runs the bot 
bot.run(TOKEN) 
