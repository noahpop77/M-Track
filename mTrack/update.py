import requests
import mysql.connector
import json
import os
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
    
    dt = datetime.fromtimestamp(unix_timestamp/1000)

    # Format the datetime object to include only day, month, and year
    formatted_date = dt.strftime('%Y-%m-%d')

    return formatted_date



def databaseInsert(matchHistoryGames, table, summoner):

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
                    summonerWin = ""
                    #print(f"Adding game with ID: \t{game['gamedata']['gameid']}")

                    participantList = json.dumps(game['gamedata']['participants'])
                    matchDataList = json.dumps(game['matchdata'])
                    

                    query = (
                        f"INSERT INTO {table} "
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
            #print("MySQL connection closed.")









def fetchGameIDsFromDB(summonerName):

    try:
        # Establish a connection to the MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            #print(f"Query made to MySQL Server: {host} | Database: {database}")

            # Create a cursor object to interact with the database
            cursor = connection.cursor(dictionary=True)  # Set dictionary=True to fetch rows as dictionaries

            # Execute the SQL query to retrieve the last 20 rows from matchHistory
            
            query = (
                "SELECT "
                "gameID "
                "FROM matchHistory "
                f"WHERE userSummoner = '{summonerName}'"

            )

            # Runs query
            cursor.execute(query)

            # Fetch the results as a list of dictionaries
            querylistOfDict = cursor.fetchall()
            #queryListOfValues = [row[0] for row in cursor.fetchall()]
            gameIDList = []
            for i in querylistOfDict:
                gameIDList.append(i['gameID'])

            # Return the retrieved data
            return gameIDList

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL Server: {e}")

    finally:
        # Close the cursor and connection when done
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()




def findUniqueIDs(list1, list2):
    # Convert the lists to sets for efficient comparison
    set1 = set(list1)
    set2 = set(list2)

    # Find the unique IDs by taking the symmetric difference of the sets
    uniqueIDs = set1.symmetric_difference(set2)

    # Convert the result back to a list
    uniqueIDsList = list(uniqueIDs)

    return uniqueIDsList







def riotSplitID(fullRiotID):
    # Splitting the string at the '#' symbol
    name_parts = fullRiotID.split("#")

    # Extracting the parts
    gamename = name_parts[0]
    tag = name_parts[1] if len(name_parts) > 1 else None
    return gamename, tag



def mtrack(summonerName, puuid, APIKEY):
    matchCount = 20
    #riotGameName, riotTagLine = riotSplitID(summonerName)
    
    #Gets PUUID from riotID
    #sumByName = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riotGameName}/{riotTagLine}?api_key={APIKEY}")
    #sumByName = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ans.replace(' ','%20')}?api_key={APIKEY}")

    #profileData = sumByName.json()


    # Gets riotID Data
    #riotIDData = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{profileData['puuid']}?api_key={APIKEY}").json()

    #riotGameName = riotIDData['gameName']
    #riotTagLine = riotIDData['tagLine']

    #print(f"\n{riotGameName}#{riotTagLine}")
    #print(riotGameName)
    #print(riotTagLine)
    #print(f"{profileData}\n")
    
    
    try:
        matches = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start=0&count={matchCount}&api_key={APIKEY}")
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

        
    # Itterates through Match ID list and gets match data
    # Appends it to a new dictionary
    matchData = []

    for i in uniqueGameIDs:
        try:
            tempMatch = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/{i}?api_key={APIKEY}").json()
            matchData.append(tempMatch)
        except:
            pass
    
    # Open the file in write mode and write the content
    #with open("MatchData.json", 'w') as json_file:
    #    json.dump(matchData, json_file, indent=4)
    
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
    
    databaseInsert(gameData, "matchHistory", summonerName)
    return 200
