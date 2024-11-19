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
def insertDatabaseRiotID(riotID, riotIDPuuid):
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
                    "(riotID, puuid) "
                    "VALUES "
                    "(%s, %s)"
                )
                data = (
                    riotID,
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




# TODO: THIS SHIT IS BROKEN AND I DONT KNOW WHY
# Use the riot account geeyokay#5964 to test
# MULTIPLE USERS CAN SEARCH UP THE SAME GAME ID AND IT BREAKS BECAUSE GAME ID IS UNIQUE
            
# Turning off the primary key flag on the gameID field in the database fixes this problem but I have not tested any other ramifications.

# TODO: Some users have games with no riot id and riot tags associated with it. 
# This means that you can only look up games up until they added riot IDs properly to the game.

# This is most likely due to viewing games that were from before riot added the riot game id tag system as a mandatory. It tries looking up the in game stats in the matchdata field then breaks there. 


# Takes in a list of dictionaries which is a list containing game data information per match. Also takes in a summoenr name associated as the "owner" of the games (the searcher).
# Those games are then uploaded to the database as a new entry. 
def insertDatabaseMatchHistory(matchHistoryGames):

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
                    
                    try:
                        participantList = json.dumps(game['gamedata']['participants'])
                        matchDataList = json.dumps(game['matchdata'])
                    except:
                        return None
                    query = (
                        f"INSERT INTO matchHistory "
                        "(gameID, gameVer, riotID, gameDurationMinutes, gameCreationTimestamp, gameEndTimestamp, queueType, gameDate, participants, matchdata) "
                        "VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    )

                    data = (
                        game['gamedata']['gameid'],
                        game['gamedata']['gamever'],
                        game['gamedata']['riotID'],
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
                    print(e)
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



def insertDatabaseRankedInfo(puuid, summonerID, riotID, tier, rank, leaguePoints, queueType, wins, losses):
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
                    "(encryptedPUUID, summonerID, riotID, tier, `rank`, leaguePoints, queueType, wins, losses) "
                    "VALUES "
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                )
                data = (
                    puuid, 
                    summonerID, 
                    riotID, 
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






def queryRankedInfo(encryptedSummonerPUUID, region, riotID, RIOTAPIKEY):
    try:
        summonerID = requests.get(f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{encryptedSummonerPUUID}?api_key={RIOTAPIKEY}").json()["id"]

        rankedInfo = requests.get(f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerID}?api_key={RIOTAPIKEY}").json()
    except Exception as e:
        return "No user/ranked data found..."
    
    # Check to only pull ranked information that is for Ranked Solo/Duo
    soloQueueRankInfo = ""
    for i in rankedInfo:
        if i["queueType"] == "RANKED_SOLO_5x5":
            soloQueueRankInfo = i
        else:
            continue
    try:
        insertDatabaseRankedInfo(
            encryptedSummonerPUUID, 
            soloQueueRankInfo["summonerId"], 
            riotID, 
            soloQueueRankInfo["tier"], 
            soloQueueRankInfo["rank"], 
            soloQueueRankInfo["leaguePoints"], 
            soloQueueRankInfo["queueType"], 
            soloQueueRankInfo["wins"], 
            soloQueueRankInfo["losses"], 
            )
    except Exception as e:
        return 500
    
    return 200






def queryRiotIDInfo(riotGameName, riotTagLine, region, RIOTAPIKEY):
    riotIDPuuid = ""
    try:
        if region == "na1":
            riotIDData = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riotGameName}/{riotTagLine}?api_key={RIOTAPIKEY}").json()
        elif region == "euw1":
            riotIDData = requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riotGameName}/{riotTagLine}?api_key={RIOTAPIKEY}").json()
        elif region == "eun1":
            riotIDData = requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riotGameName}/{riotTagLine}?api_key={RIOTAPIKEY}").json()
    except:
        riotIDPuuid = "No ranked data found..."

#    try:
#        riotIDData = requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riotGameName}/{riotTagLine}?api_key={RIOTAPIKEY}").json()
#    except:
#        riotIDPuuid = "No ranked data found..."
    try:
        riotIDPuuid = riotIDData['puuid']
    except KeyError:
        pass
    return riotIDPuuid



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






def mtrack(riotID, puuid, region, APIKEY, reqCount, startPosition=0):
    
    # Gets a list of the last 20(reqCount variable) matches associated with the specified puuid
    # start=10&count=20

    if region == "na1":
        try:
            
            matches = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start={startPosition}&count={reqCount}&api_key={APIKEY}")
            print(str(matches.json()).split(","))
        except:
            pass
    elif region == "euw1" or region == "eun1":
        try:
            matches = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start={startPosition}&count={reqCount}&api_key={APIKEY}")
        except:
            pass

    
    # Gets the mapping information for items and summoners to map their IDs to their Names
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        summonerPath = os.path.join(current_directory, 'summonerSpellMapping.json')
        itemPath = os.path.join(current_directory, 'items.json')
        runePath = os.path.join(current_directory, 'runes.json')
        
        # Opening mapping file for summoner spells
        with open(summonerPath, 'r') as file:
            summonerIcons = json.load(file)

        # Loads item id mappings
        with open(itemPath, 'r') as file:
            itemIcons = json.load(file)
        
        # Loads rune id mappings
        with open(runePath, 'r') as file:
            runeIcons = json.load(file)

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
    gameIDsFromDB = fetchGameIDsFromDB(riotID)
    # Gets the unique IDs between the past 20 matches in the request that was made and all all of the IDs that are associated with the summoner searched in the DB
    # This might prove to be a performance issue if the DB accumulates enough entries on a single user the search will take long?

    uniqueGameIDs = findUniqueIDs(gameIDsFromDB, matchList)

    # Itterates through Match ID list and gets match data
    # Appends it to a new dictionary
    matchData = []

    for i in uniqueGameIDs:
        if region == "na1":
            try:
                tempMatch = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/{i}?api_key={APIKEY}").json()
                matchData.append(tempMatch)
            except Exception as e:
                pass
        elif region == "euw1" or region == "eun1":
            try:
                tempMatch = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/{i}?api_key={APIKEY}").json()
                matchData.append(tempMatch)
            except Exception as e:
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
        
        try:
            date = convert_unix_to_date(i['info']['gameCreation'])
        except:
            continue

        try:
            history = {
                'gamedata': {
                    'gameid': i['metadata']['matchId'], 
                    'gamever': i['info']['gameVersion'],
                    #'userSummoner': profileData['name'],
                    'riotID': riotID,
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
                    "riotID": f'{participant["riotIdGameName"]}#{participant["riotIdTagline"]}',
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
                    "item0": translateItemCodesToNames(itemIcons, str(participant['item0'])),
                    "item1": translateItemCodesToNames(itemIcons, str(participant['item1'])),
                    "item2": translateItemCodesToNames(itemIcons, str(participant['item2'])),
                    "item3": translateItemCodesToNames(itemIcons, str(participant['item3'])),
                    "item4": translateItemCodesToNames(itemIcons, str(participant['item4'])),
                    "item5": translateItemCodesToNames(itemIcons, str(participant['item5'])),
                    "item6": translateItemCodesToNames(itemIcons, str(participant['item6'])),
                    "win": participant['win'],
                    "keystone": translateItemCodesToNames(runeIcons, str(participant['perks']['styles'][0]['selections'][0]['perk'])),
                    "secondaryRune": translateItemCodesToNames(runeIcons, str(participant['perks']['styles'][1]['style']))
                }
                
                history['matchdata'].append(newEntry)
        
        except KeyError:
            pass

        if len(history['matchdata']) > 1:
            gameData.append(history)

    insertDatabaseMatchHistory(gameData)

    return 200

def translateItemCodesToNames(itemIcons, itemId):
    try:
        return str(itemIcons[itemId])
    except:
        # Handle the error (e.g., return a default icon or log the issue)
        return "PlaceholderItem"

def injectMatchJsonIntoDatabase(matchData):
    history = {}
    gameData = []

    current_directory = os.path.dirname(os.path.abspath(__file__))
    summonerPath = os.path.join(current_directory, 'summonerSpellMapping.json')
    itemPath = os.path.join(current_directory, 'items.json')
    runePath = os.path.join(current_directory, 'runes.json')
    
    # Opening mapping file for summoner spells
    with open(summonerPath, 'r') as file:
        summonerIcons = json.load(file)
    # Loads item id mappings
    with open(itemPath, 'r') as file:
        itemIcons = json.load(file)
    
    # Loads rune id mappings
    with open(runePath, 'r') as file:
        runeIcons = json.load(file)

        
    queueType = "Not Ranked"
    try:
        if matchData['info']['queueId'] == 420:
            queueType = "Ranked Solo/Duo"
    except KeyError:
        pass
    
    try:
        date = convert_unix_to_date(matchData['info']['gameCreation'])
    except:
        pass

    try:
        history = {
            'gamedata': {
                'gameid': matchData['metadata']['matchId'], 
                'gamever': matchData['info']['gameVersion'],
                #'userSummoner': profileData['name'],
                'riotID': f"{matchData['info']['participants'][0]['riotIdGameName']}#{matchData['info']['participants'][0]['riotIdTagline']}",
                'gameDurationMinutes': getGameTime(int(matchData['info']['gameDuration'])),
                'gameCreationTimestamp': matchData['info']['gameCreation'],
                'gameEndTimestamp': matchData['info']['gameEndTimestamp'],
                'queueType': queueType,
                'gameDate': date,
                'participants': matchData['metadata']['participants']                        
            },
            'matchdata' : []
        }
        for participant in matchData['info']['participants']:
            newEntry = {
                "riotID": f'{participant["riotIdGameName"]}#{participant["riotIdTagline"]}',
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
                "item0": translateItemCodesToNames(itemIcons, str(participant['item0'])),
                "item1": translateItemCodesToNames(itemIcons, str(participant['item1'])),
                "item2": translateItemCodesToNames(itemIcons, str(participant['item2'])),
                "item3": translateItemCodesToNames(itemIcons, str(participant['item3'])),
                "item4": translateItemCodesToNames(itemIcons, str(participant['item4'])),
                "item5": translateItemCodesToNames(itemIcons, str(participant['item5'])),
                "item6": translateItemCodesToNames(itemIcons, str(participant['item6'])),
                "win": participant['win'],
                "keystone": translateItemCodesToNames(runeIcons, str(participant['perks']['styles'][0]['selections'][0]['perk'])),
                "secondaryRune": translateItemCodesToNames(runeIcons, str(participant['perks']['styles'][1]['style']))
            }
            
            history['matchdata'].append(newEntry)
    
    except KeyError:
        pass

    if len(history['matchdata']) > 1:
        gameData.append(history)

    insertDatabaseMatchHistory(gameData)