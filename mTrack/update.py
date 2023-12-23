import requests
import os
import operator
import csv
import mysql.connector
import json
from datetime import datetime
from configparser import ConfigParser

# Config file initiators for use in getting API key from config.ini
# in the sanity check for the /addSummoner API endpoint
file = "../config.ini"
config = ConfigParser()
config.read(file)

host = config['DATABASE']['host']
user = config['DATABASE']['user']
password = config['DATABASE']['password']
database = config['DATABASE']['database']



def getGameTime(durationInSeconds):

    # Convert seconds to minutes and round using modulo
    minutes = durationInSeconds // 60
    rounded_minutes = minutes % 60
    rounded_seconds = durationInSeconds % 60

    # Format the output as "mm:ss"
    formatted_time = f"{rounded_minutes:02d}:{rounded_seconds:02d}"
    return formatted_time




def convert_unix_to_date(unix_timestamp):
    
    dt = datetime.fromtimestamp(unix_timestamp/100)

    # Format the datetime object to include only day, month, and year
    formatted_date = dt.strftime('%Y-%m-%d')

    return formatted_date



def databaseInsert(matchHistoryGames, table):

    try:
        # Establish a connection to the MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            #print(f"Connected to MySQL Server: {host} | Database: {database}")

            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            try:
                for game in matchHistoryGames:
                    
                    #print(f"Adding game with ID: \t{game['gamedata']['gameid']}")

                    participantList = json.dumps(game['gamedata']['participants'])
                    matchDataList = json.dumps(game['matchdata'])
                    

                    query = (
                        "INSERT INTO matchHistory "
                        "(gameID, gameVer, userSummoner, gameDurationMinutes, gameCreationTimestamp, gameEndTimestamp, queueType, gameDate, participants, matchdata) "
                        "VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    )

                    data = (
                        game['gamedata']['gameid'],
                        game['gamedata']['gamever'],
                        game['gamedata']['userSummoner'],
                        game['gamedata']['gameDurationMinutes'],
                        game['gamedata']['gameCreationTimestamp'],
                        game['gamedata']['gameEndTimestamp'],
                        game['gamedata']['queueType'],
                        game['gamedata']['gameDate'],
                        participantList,
                        matchDataList
                    )
                    #print(f"Adding game with ID: \t{game['gamedata']['gameid']}")
                    #print("pre send")
                    cursor.execute(query, data)
                    #print("post send")

            except mysql.connector.Error as e:
                if e.errno == 1062:
                    
                    pass
                else:
                    print(e)

            # Commit the changes
            connection.commit()

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL Server: {e}")

    finally:
        # Close the cursor and connection when done
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            #print("MySQL connection closed.")






def mtrack(ans, APIKEY):
    matchCount = 20

    #Gets PUUID from Summoner Name
    print("Making API call...")
    sumByName = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ans.replace(' ','%20')}?api_key={APIKEY}")
    
    #print(f"Querying summoner name for PUUID: {sumByName}")
    myID = sumByName.json()
    matches = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{myID['puuid']}/ids?queue=420&start=0&count={matchCount}&api_key={APIKEY}")
    
    #print(f"Querying PUUID for Match IDs: {matches}")

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

    history = {}
    gameData = []
   

    for i in matchData:
        
        queueType = "Not Ranked"
        if i['info']['queueId'] == 420:
            queueType = "Ranked Solo/Duo"
        
        date = convert_unix_to_date(i['info']['gameCreation'])


        try:
            history = {
                    'gamedata': {
                        'gameid': i['metadata']['matchId'], 
                        'gamever': i['info']['gameVersion'],
                        'userSummoner': ans,
                        'gameDurationMinutes': getGameTime(i['info']['gameDuration']),
                        'gameCreationTimestamp': i['info']['gameCreation'],
                        'gameEndTimestamp': i['info']['gameEndTimestamp'],
                        'queueType': queueType,
                        'gameDate': date,
                        'participants': i['metadata']['participants']                        
                    },
                    'matchdata' : []
            }
            for participant in i['info']['participants']:
                newEntry = {
                    "sumName": participant['summonerName'],
                    "playerTeamID": participant['teamId'],
                    "Champ": participant['championName'],
                    "kills": participant['kills'],
                    "deaths": participant['deaths'],
                    "assists": participant['assists'],
                    "champLevel": participant['champLevel'],
                    "goldEarned": participant['goldEarned']
                }
                history['matchdata'].append(newEntry)
        
        except KeyError:
            exit()
        
        gameData.append(history)
    
    databaseInsert(gameData, "mtrack.matchHistory")
    return 200
