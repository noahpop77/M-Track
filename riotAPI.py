import requests
import os
from prettytable import PrettyTable
import operator

os.system("clear")

#ans = input("What summoner name do you want to scan for matches: ")
ans = "CEOofChallenger"
APIKEY = "RGAPI-00b8bc6f-a68f-44ff-8e99-b48c3cbcde08"
matchCount = 100

#Gets PUUID from Summoner Name
print("Making API call...")
sumByName = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ans.replace(' ','%20')}?api_key={APIKEY}")
print(f"Querying summoner name for PUUID: {sumByName}")
myID = sumByName.json()
matches = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{myID['puuid']}/ids?queue=420&start=0&count={matchCount}&api_key={APIKEY}")
print(f"Querying PUUID for Match IDs: {matches}")

# Gets return as a json/list, Splits it into list of dictionaries
sepList = str(matches.json()).split(",")

matchList = []      # Appends to a new list with proper formatting       
for i in sepList:   # Cuts random useless characters in match list
    matchList.append(i.replace(" ","").replace("'", "").replace("[", "").replace("]", ""))

# Itterates through Match ID list and gets match data
# Appends it to a new dictionary
matchData = []
for i in matchList:
    tempMatch = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/{i}?api_key={APIKEY}").json()
    matchData.append(tempMatch)

duoTracker = []

timedead = 0
gameCounter = 0
count = 0

f = open('matchHistory.txt', 'w')

# Itterates through matchdata to clean it up
# print(matchData) would print all of the data obtained from query
print("Querying participants games...")
for i in matchData:
    try:
        gameVer = i['info']['gameVersion']
        f.write("""
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        \n""")
        gameCounter += 1
        f.write(f"GameCounter = {gameCounter}\n")
        f.write(f"Game Version: {gameVer}\n")
        f.write(f"Game: {i['metadata']['matchId']}\n")
        #print(f"Queried game {gameCounter}")
    except KeyError:
        print("Done getting match data!")
        exit()

    statpergame = PrettyTable([f'{ans} Stat', 'Value'])
    timeInMins = (i['info']['gameDuration'] / 1000) / 60
    roundToMin = round(timeInMins, 1)

    f.write(f"Game Duration: {roundToMin} mins\n")

    # Tables used for formatting
    tableOne = PrettyTable(['Sum Name', 'Champ', 'K', 'D', 'A', 'LvL', '$ Earned', 'TimeDead'])
    tableTwo = PrettyTable(['Sum Name', 'Champ', 'K', 'D', 'A', 'LvL', '$ Earned', 'TimeDead'])
    # Loops through each participant in each game and gets the info we want
    for x in i['info']['participants']:
        if x['teamId'] == 100:      # Team One
            tableOne.add_row([x['summonerName'], x['championName'], x['kills'], x['deaths'], x['assists'], x['champLevel'], x['goldEarned'], x['totalTimeSpentDead']])
        elif x['teamId'] == 200:    # Team Two
            tableTwo.add_row([x['summonerName'], x['championName'], x['kills'], x['deaths'], x['assists'], x['champLevel'], x['goldEarned'], x['totalTimeSpentDead']])
        
        ############################ QUERIED PLAYER STATS PER GAME
        if x['summonerName'] == ans:
            #
            # Real game time is total time minus 2 minutes
            realGameTime = timeInMins - 2
            #
            timedead += x['totalTimeSpentDead']
            #
            xpPerMin = x['champExperience'] / realGameTime
            #
            assistPerMin = x['assists'] / realGameTime
            #
            structureDamagePerMin = x['damageDealtToBuildings'] / realGameTime
            #
            objDamage = x['damageDealtToObjectives']
            #
            objDamagePerMin = x['damageDealtToObjectives'] / realGameTime
            #
            neutralDamage = x['damageDealtToObjectives'] - x['damageDealtToBuildings']
            #
            neutralDamagePerMin = (x['damageDealtToObjectives'] - x['damageDealtToBuildings']) / realGameTime
            #
            goldPerMin = x['goldEarned'] / timeInMins
            #
            ccReceived = x['totalTimeCCDealt']
            #
            ccDealt = x['timeCCingOthers']
            #
            healingDone = x['totalHeal']
            #
            statpergame.add_row([f"XP/min (level {x['champLevel']})", round(xpPerMin, 2)])
            statpergame.add_row(['Assist/m', round(assistPerMin, 2)])
            statpergame.add_row(['Structure Damage', x['damageDealtToBuildings']])
            statpergame.add_row(['Structure Damage/min', round(structureDamagePerMin, 2)])
            statpergame.add_row(['Objective Damage', objDamage])
            statpergame.add_row(['Objective Damage/min', round(objDamagePerMin, 2)])
            statpergame.add_row(['Neutral Monster Damage', neutralDamage])
            statpergame.add_row(['Neutral Monster Damage/min', round(neutralDamagePerMin, 2)])
            statpergame.add_row(['Gold/min', round(goldPerMin, 2)])
            statpergame.add_row(['Total Time CC Dealt', ccReceived])
            statpergame.add_row(['Time CCing others(s)', ccDealt])
            statpergame.add_row(['Total Healing Done', healingDone])
            #statpergame.add_row([])


        # First blood checker
        if x['firstBloodKill'] == True:
            f.write(f"{x['summonerName']} ({x['championName']}) got First blood\n")

        duoTracker.append(x['summonerName'])
    
    #i['info']['gameDuration']
    # divided by 1000/60

    avgDead = timedead / gameCounter

    f.write("+--------+\n")
    f.write("| Team 1 |\n")
    f.write(f"{str(tableOne)}\n")

    f.write("+--------+\n")
    f.write("| Team 2 |\n")
    f.write(f"{str(tableTwo)}\n")

    f.write(f"{str(statpergame)}")


# Converts items in list of names to counts of occurences
dict_of_counts = {item:duoTracker.count(item) for item in duoTracker}

# Sorts the dict by values and outputs it as a list
sortedDuo = sorted(dict_of_counts.items(), key=operator.itemgetter(1), reverse=True)

filteredDict = {}
for i in sortedDuo:
    if i[1] > 1:
        filteredDict[i[0]] = i[1]
del filteredDict[ans]

f.write("\n--------------------------\n")

f.write(f"Average seconds {ans} has spent dead per game in the last {gameCounter} ranked games: {avgDead}\n")

f.write("--------------------------\n\n Duo Game Tracker\n")


duoTable = PrettyTable(['Sum Name', 'Duo Game Number'])
for key, value in filteredDict.items():
    duoTable.add_row([key, value])
    #f.write(f"{key} has {value} games with {ans}\n")
f.write("\n")
f.write(str(duoTable))
f.close()

