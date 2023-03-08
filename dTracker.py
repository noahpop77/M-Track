import requests
import os
import operator
import datetime
import time

os.system("clear")

def dtrack(ans, mykey):
    APIKEY = mykey
    matchCount = 4

    #Gets PUUID from Summoner Name
    sumByName = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ans.replace(' ','%20')}?api_key={APIKEY}")
    myID = sumByName.json()

    matches = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{myID['puuid']}/ids?queue=420&start=0&count={matchCount}&api_key={APIKEY}")

    print(f"myID['puuid']: {myID['puuid']}")
    
    # Gets return as a json/list, Splits it into list of dictionaries
    sepList = str(matches.json()).split(",")

    matchList = []      # Appends to a new list with proper formatting
    for i in sepList:   # Cuts random useless characters in match list
        matchList.append(i.replace(" ","").replace("'", "").replace("[", "").replace("]", ""))
    matchData = []
    
    for i in matchList:
        print(i)
        matchData.append(requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/{i}?api_key={APIKEY}").json())
    
    times = []
    diffs = []

    for i in matchData:
        gameDate = i['info']['gameCreation']
        print(f"gameDate: {gameDate}")
        times.append(gameDate)

    # Gets the current time in unix epoch time
    ms = datetime.datetime.now()
    times.append(int(time.mktime(ms.timetuple()) * 1000))

    times.sort(reverse=True)
    print(times)
    # Calculates time differences and appends them to diffs
    for index, i in enumerate(times):
        print(f"{index}:{i}")
        try:
            diffs.append(times[index] - times[index + 1])
        except IndexError:
            continue

    print(f"Diffs: {diffs}")

    banked = 0
    hoursdiff = []

    # Diffs conversion
    for i in diffs:
        # 3600 seconds in an hour and 3600000 is milliseconds in an hour. Multiplying it by 24 divides unix epoch timestamp in milliseconds by milliseconds in the day
        # Basically converts the millisecond epoch times into days to a decimal
        hoursdiff.append(i/(3600000 * 24)) 
    
    for i in hoursdiff:
        print(i)
        newTime =  7 - i
        banked = banked + newTime
        if banked < 0: banked = 0
        if banked > 28: banked = 28
    
    print(banked)
    banked = round(banked, 2)
    print(banked)
    banked = banked

    print(f"Banked: {banked}")

    if banked == 0.0:
        print("PLAY MORE GAMES")
        return "PLAY GAME NOW BITCH (stream that shit)"
    else:
        print(f"{banked:.2f} days until decay...")
        return f"{banked:.2f} days until decay..."


dtrack("Haidder","RGAPI-e66e887e-ea2f-4070-9d4e-9f46280e65b6")