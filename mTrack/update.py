import requests
import mysql.connector
import json
import os
from datetime import datetime
from configparser import ConfigParser
from .fetch import *

# Config file initiators for use in getting API key from config.ini
# in the sanity check for the /addSummoner API endpoint
file = "../config.ini"
config = ConfigParser()
config.read(file)

host = config['DATABASE']['host']
user = config['DATABASE']['user']
password = config['DATABASE']['password']
database = config['DATABASE']['database']


# Takes in a total amount of seconds of game timer and converts it to minute and second format
# Ex: formatted_time = 30:12
def getGameTime(durationInSeconds):

    # Convert seconds to minutes and round using modulo
    minutes = durationInSeconds // 60
    rounded_minutes = minutes % 60
    rounded_seconds = durationInSeconds % 60

    # Format the output as "mm:ss"
    formatted_time = f"{rounded_minutes:02d}:{rounded_seconds:02d}"
    return formatted_time



# Riot API gives linux epoc time in milliseconds so you have to divide their time by 1000 and then convert THAT time with the fromtimestamp function which takes seconds.
def convert_unix_to_date(unix_timestamp):
    
    dt = datetime.fromtimestamp(unix_timestamp/1000)

    # Format the datetime object to include only day, month, and year
    formatted_date = dt.strftime('%Y-%m-%d')

    return formatted_date


# Uses riotID, summonerName and PUUID as required data fields for the db table of mtrack.riotIDData which contains riotID account information.
def insertDatabaseRiotID(riotID, summonerName, riotIDPuuid):
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
                query = (
                    f"INSERT INTO riotIDData "
                    "(riotID, summonerName, puuid) "
                    "VALUES "
                    "(%s, %s, %s)"
                )
                data = (
                    riotID,
                    summonerName,
                    riotIDPuuid
                )
                
                cursor.execute(query, data)

            except IndexError:
                pass

            except mysql.connector.Error as e:
                if e.errno == 1062:
                    pass
                else:
                    print(e)

            connection.commit()

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL Server: {e}")

    finally:
        # Close the cursor and connection when done
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()





# Takes in a list of dictionaries which is a list containing game data information per match. Also takes in a summoenr name associated as the "owner" of the games (the searcher).
# Those games are then uploaded to the database as a new entry. 
def insertDatabaseMatchHistory(matchHistoryGames, summoner):

    try:
        # Establish a connection to the MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            # Create a cursor object to interact with the database
            cursor = connection.cursor()
            
            try:
                for game in matchHistoryGames:
                    summonerWin = ""
                    participantList = json.dumps(game['gamedata']['participants'])
                    matchDataList = json.dumps(game['matchdata'])
                    

                    query = (
                        f"INSERT INTO matchHistory "
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
                    
                    cursor.execute(query, data)

            except IndexError:
                pass

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



def insertDatabaseRankedInfo(puuid, summonerID, summonerName, tier, rank, leaguePoints, queueType, wins, losses):
    try:
        # Establish a connection to the MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            # Create a cursor object to interact with the database
            cursor = connection.cursor()
            
            try:
                query = (
                    f"INSERT INTO summonerRankedInfo "
                    "(encryptedPUUID, summonerID, summonerName, tier, `rank`, leaguePoints, queueType, wins, losses) "
                    "VALUES "
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                )
                data = (
                    puuid, 
                    summonerID, 
                    summonerName, 
                    tier, 
                    rank, 
                    leaguePoints, 
                    queueType, 
                    wins, 
                    losses
                )
                
                cursor.execute(query, data)

            except IndexError:
                pass

            except mysql.connector.Error as e:
                if e.errno == 1062:
                    pass
                else:
                    print(e)

            connection.commit()

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL Server: {e}")

    finally:
        # Close the cursor and connection when done
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()






def queryRankedInfo(encryptedSummonerPUUID, RIOTAPIKEY):
    
    summonerID = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{encryptedSummonerPUUID}?api_key={RIOTAPIKEY}").json()["id"]

    try:
        rankedInfo = requests.get(f"https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}?api_key={RIOTAPIKEY}").json()[0]
    except:
        return "No ranked data found function"
    insertDatabaseRankedInfo(
        encryptedSummonerPUUID, 
        rankedInfo["summonerId"], 
        rankedInfo["summonerName"], 
        rankedInfo["tier"], 
        rankedInfo["rank"], 
        rankedInfo["leaguePoints"], 
        rankedInfo["queueType"], 
        rankedInfo["wins"], 
        rankedInfo["losses"], 
        )
    
    return 200







def queryRiotIDInfo(riotGameName, riotTagLine, RIOTAPIKEY):
    try:
        riotIDData = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riotGameName}/{riotTagLine}?api_key={RIOTAPIKEY}").json()
        
        sumNameData = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{riotIDData['puuid']}?api_key={RIOTAPIKEY}").json()
    except:
        return "No ranked data found..."

    summonerName = sumNameData['name']
    riotIDPuuid = riotIDData['puuid']
    return summonerName, riotIDPuuid



# It doesnt just do a unique id check both ways but it checks to see what elements from list 2 are NOT in list 1. This way it only checks to see what game IDs are not in the database and not what ids in the database are in the past 20 game IDs searched.
def findUniqueIDs(list1, list2):
    # Convert the lists to sets for efficient comparison
    set1 = set(list1)
    set2 = set(list2)
    # Find the elements in list2 that are not in list1
    uniqueIDs = set2 - set1
    # Convert the result back to a list
    uniqueIDsList = list(uniqueIDs)
    return uniqueIDsList

# Splits a full riotID into its components of a gameName and a tag
# Useful tool
def riotSplitID(fullRiotID):
    # Splitting the string at the '#' symbol
    name_parts = fullRiotID.split("#")

    # Extracting the parts
    gamename = name_parts[0]
    tag = name_parts[1] if len(name_parts) > 1 else None
    return gamename, tag






def mtrack(summonerName, puuid, APIKEY, reqCount, startPosition=0):
    
    # Gets a list of the last 20(reqCount variable) matches associated with the specified puuid
    # start=10&count=20
    try:
        matches = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start={startPosition}&count={reqCount}&api_key={APIKEY}")
    except KeyError:
        exit(1)
    
    # Gets the mapping information for items and summoners to map their IDs to their Names
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        summonerPath = os.path.join(current_directory, 'summonerSpellMapping.json')
        itemPath = os.path.join(current_directory, 'items.json')
        
        # Opening mapping file for summoner spells
        with open(summonerPath, 'r') as file:
            summonerIcons = json.load(file)

        # Loads item id mappings
        with open(itemPath, 'r') as file:
            itemIcons = json.load(file)

    except:
        print(
            '''
            Mapping File Not Found...
            Please put mapping file in the same directory as the update.py file so it can populat the database properly.
            '''
            )
        exit(1)

    # Gets return as a json/list, Splits it into list of dictionaries
    sepList = str(matches.json()).split(",")

    matchList = []      # Appends to a new list with proper formatting       
    for i in sepList:   # Cuts random useless characters in match list
        matchList.append(i.replace(" ","").replace("'", "").replace("[", "").replace("]", ""))
    
    # Gets the IDs for summonerName from the DB as a list of gameIDs
    gameIDsFromDB = fetchGameIDsFromDB(summonerName)

    # Gets the unique IDs between the past 20 matches in the request that was made and all all of the IDs that are associated with the summoner searched in the DB
    # This might prove to be a performance issue if the DB accumulates enough entries on a single user the search will take long?
    uniqueGameIDs = findUniqueIDs(gameIDsFromDB, matchList)
    # TODO: There seems to be some odd behavior where there is a delay in updating the games. It will show the unique game IDs but getting the game data takes longer than OP.GG. This happens when it has a set of data, the player plays some games to add to the new list of matches naturally but it doesnt show the new games until later. Whereas op.gg does it instantly almost.
    
    # Itterates through Match ID list and gets match data
    # Appends it to a new dictionary
    matchData = []

    for i in uniqueGameIDs:
        try:
            tempMatch = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/{i}?api_key={APIKEY}").json()
            matchData.append(tempMatch)
        except Exception as e:
            print(e)
            pass

    
    history = {}
    gameData = []
    for i in matchData:
        
        queueType = "Not Ranked"
        try:
            if i['info']['queueId'] == 420:
                queueType = "Ranked Solo/Duo"
        except KeyError:
            pass
        
        date = convert_unix_to_date(i['info']['gameCreation'])

        try:
            history = {
                'gamedata': {
                    'gameid': i['metadata']['matchId'], 
                    'gamever': i['info']['gameVersion'],
                    #'userSummoner': profileData['name'],
                    'userSummoner': summonerName,
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
                    "goldEarned": participant['goldEarned'],
                    "summonerSpell1": summonerIcons[str(participant['summoner1Id'])],
                    "summonerSpell2": summonerIcons[str(participant['summoner2Id'])],
                    "visionScore": participant['visionScore'],
                    "totalCS": int(participant['totalMinionsKilled'] + participant['neutralMinionsKilled']),
                    "item0": itemIcons[str(participant['item0'])],
                    "item1": itemIcons[str(participant['item1'])],
                    "item2": itemIcons[str(participant['item2'])],
                    "item3": itemIcons[str(participant['item3'])],
                    "item4": itemIcons[str(participant['item4'])],
                    "item5": itemIcons[str(participant['item5'])],
                    "item6": itemIcons[str(participant['item6'])],
                    "win": participant['win']
                }
                
                history['matchdata'].append(newEntry)
        
        except KeyError:
            pass
        
        gameData.append(history)
    
    insertDatabaseMatchHistory(gameData, summonerName)
    return 200
