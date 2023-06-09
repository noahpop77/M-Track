import logging
import discord
from discord.ext import commands
import requests
from configparser import ConfigParser
from pyfiglet import figlet_format

from dtrack import dtrack

from dtrack import bcolors
# Sets up the config file for the tokens
# This way I can add the config.ini file to the git ignore listing and not show my tokens when working on this repository
# YOU WILL NEED TO MAKE YOUR OWN CONFIG.INI FILE OR HARD CODE IN YOUR OWN KEY VALUES WHERE RIOTAPIKEY AND DISCORDTOKEN ARE DECLARED
file = "config.ini"
config = ConfigParser()
config.read(file)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", filename="dTracker.log")
logging.info("STARTED - DTracker")

RIOTAPIKEY = config['KEYS']['riotapi']
DISCORDTOKEN = config['KEYS']['discordtoken']
APIADDRESS = config['KEYS']['apiaddress']
APIPORT = config['KEYS']['apiport']

# http://10.0.0.150:5000
# Main bot code
# Previous code was function definition
def run():
    # Context and declaring bot as well as its prefix for the commands in discord
    logging.info(f"Starting discord bot...")
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="`", intents=intents)

    # When the bot boots up it prints the data below
    @bot.event
    async def on_ready():
        logging.info("Bot started...")
        print(f"User: {bot.user} (ID: {bot.user.id})")

    # When someone types !hello in discord it will respond with the following
    @bot.command()
    async def word(ctx: commands.Context, message):
        logging.info("Word command sent/")
        mainout = figlet_format(message, font='starwars')
        await ctx.send("```" + mainout + "```")

    # The MAIN trigger for everything else. Calls the dtrack function with the riot api key specified in the config file and searches
    # all of the names that are obtained from the API call of http://10.0.0.150:5000/getsummoners which is a CSV file. The file is then
    # split because it is read as a string and split into a list. The return data and the prints do the rest of the work for you.
    @bot.command()
    async def decay(ctx: commands.Context):
        logging.info("Starting decay command...")
        await ctx.send("Checking decayers...")
        summoners = requests.get(f"{APIADDRESS}:{APIPORT}/getSummoners")

        # Spits out a list of summoners that are comma delimeted
        # Format: brian,sawa,bob,james,time,iraqiteemo
        list_of_summoners = summoners.text.split(',')

        dtrackResponse = ""
        embed=discord.Embed()
        for i in list_of_summoners: 
            try:
                print("\n---------------------------------------------------------------------------------------------------------------")
                print(bcolors.OKBLUE + f"Searching data for summoner: \t{i}" + bcolors.ENDC)
                print(f"-------------- {dtrackResponse} --------------")
                embed.add_field(name=i, value=dtrack(i, RIOTAPIKEY), inline=False)
            except KeyError:
                print(bcolors.FAIL + "\n###################################################" + bcolors.ENDC)
                print(f"SUMMONER DOESNT EXIST: \t\t{i}")
                print(bcolors.FAIL + "###################################################" + bcolors.ENDC)
        
        
        
        embed.set_footer(text="All hail Brian Sawa the one true leader")
        await ctx.send(embed=embed)
        #await ctx.send(f"```{dtrackResponse}```")
    # Init Bot
    bot.run(DISCORDTOKEN)

# Main code
if __name__ == "__main__":
    run()