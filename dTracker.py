import requests
import os
import operator
import datetime
import time

os.system("clear")


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def dtrack(ans, mykey):
    # Sets API key variable
    APIKEY = mykey

    # Searches theough 4 matches to determine decay since the MAX you can have banked is 4 matches played immediately after one another to a cap of 28 days so no point searching past 4 matches
    matchCount = 4

    # Gets PUUID from Summoner Name
    sumByName = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ans.replace(' ','%20')}?api_key={APIKEY}").json()
    # Converts response to JSON

    matches = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{sumByName['puuid']}/ids?queue=420&start=0&count={matchCount}&api_key={APIKEY}")

    print(f"Player User ID: \t\t{sumByName['puuid']}")
    
    # Gets return as a json/list, Splits it into list of dictionaries
    sepList = str(matches.json()).split(",")

    matchList = []      # Appends to a new list with proper formatting
    for i in sepList:   # Cuts random useless characters in match list
        matchList.append(i.replace(" ","").replace("'", "").replace("[", "").replace("]", ""))
    matchData = []
    
    
    for i in matchList:
        #print(f"Game ID: \t\t\t{i}")
        matchData.append(requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/{i}?api_key={APIKEY}").json())
    
    # Sets times and diffs variables
    times = []
    diffs = []

    # Loops through match data and grabs the game creation times and appends them to the times list
    for i in matchData:
        gameDate = i['info']['gameCreation']
        times.append(gameDate)

    # Prints Game IDs that are getting scanned
    print("")
    for i in matchList:
        print(f"Game ID: \t\t\t{i}")

    # Gets the current time in unix epoch time
    ms = datetime.datetime.now()
    times.append(int(time.mktime(ms.timetuple()) * 1000))

    times.sort(reverse=True)
    # Calculates time differences and appends them to diffs
    for index, i in enumerate(times):
        try:
            diffs.append(times[index] - times[index + 1])
        except IndexError:
            continue

    #print(f"Diffs: {diffs}")
    print("")
    for i in diffs: print(f"Game Time differentials: \t{i}")

    banked = 0
    hoursdiff = []

    # Diffs conversion
    for i in diffs:
        # 3600 seconds in an hour and 3600000 is milliseconds in an hour. Multiplying it by 24 divides unix epoch timestamp in milliseconds by milliseconds in the day
        # Basically converts the millisecond epoch times into days to a decimal
        hoursdiff.append(i/(3600000 * 24)) 
    
    for i in hoursdiff:
        newTime =  7 - i
        banked = banked + newTime
        if banked < 0: banked = 0
        if banked > 28: banked = 28
    
    banked = round(banked, 2)
    banked = banked

    print(f"\nBanked: {banked}")

    if banked == 0.0:
        print("PLAY MORE GAMES")
        return "PLAY GAME NOW BITCH (stream that shit)"
    else:
        print(bcolors.OKCYAN + f"{banked:.2f} days until decay..." + bcolors.ENDC)
        return f"{banked:.2f} days until decay..."

summoners = requests.get(f"http://10.0.0.150:5000/getsummoners")

# Spits out a list of summoners that are comma delimeted
# Format: brian,sawa,bob,james,time,iraqiteemo
list_of_summoners = summoners.text.split(',')

for i in list_of_summoners: 
    try:
        print("\n---------------------------------------------------------------------------------------------------------------")
        print(bcolors.OKBLUE + f"Searching data for summoner: \t{i}" + bcolors.ENDC)
        dtrack(i,"RGAPI-e66e887e-ea2f-4070-9d4e-9f46280e65b6")
    except KeyError:
        print(bcolors.FAIL + "\n###################################################" + bcolors.ENDC)
        print(f"SUMMONER DOESNT EXIST: \t\t{i}")
        print(bcolors.FAIL + "###################################################" + bcolors.ENDC)
#dtrack("Haidder","RGAPI-e66e887e-ea2f-4070-9d4e-9f46280e65b6")