import requests
import psycopg2
import json
import os
from datetime import datetime
from configparser import ConfigParser
from .fetch import *
from urllib.parse import quote
import sys

# Config file initiators for use in getting API key from config.ini
file = "../config.ini"
config = ConfigParser()
config.read(file)

host = config['DATABASE']['host']
user = config['DATABASE']['user']
password = config['DATABASE']['password']
database = config['DATABASE']['database']

# Rune metadata is generated from Riot Data Dragon. Keep it in memory because
# every participant in every fetched match needs the same lookup.
_RUNE_PAGE_MAP = None


def loadRunePageMap():
    global _RUNE_PAGE_MAP
    if _RUNE_PAGE_MAP is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'runePageMap.json')
        try:
            with open(path, 'r') as file:
                _RUNE_PAGE_MAP = json.load(file)
        except (OSError, ValueError):
            _RUNE_PAGE_MAP = {"trees": {}, "runes": {}, "shards": {}}
    return _RUNE_PAGE_MAP


def buildRunePage(perks, runeMap=None):
    """Turn Riot's raw perks object into a small, render-ready rune page."""
    if not isinstance(perks, dict):
        return None

    runeMap = runeMap or loadRunePageMap()
    styles = perks.get('styles')
    if not isinstance(styles, list) or not styles:
        return None

    def runeEntry(perkId):
        info = runeMap.get('runes', {}).get(str(perkId))
        if not info:
            return None
        return {"id": perkId, "name": info.get('name', ''), "icon": info.get('icon', '')}

    def buildStyle(style):
        if not isinstance(style, dict):
            return None
        treeId = style.get('style')
        tree = runeMap.get('trees', {}).get(str(treeId), {})
        runes = []
        for selection in style.get('selections') or []:
            if isinstance(selection, dict):
                rune = runeEntry(selection.get('perk'))
                if rune:
                    runes.append(rune)
        if not tree and not runes:
            return None
        return {
            "id": treeId,
            "name": tree.get('name', ''),
            "icon": tree.get('icon', ''),
            "runes": runes,
        }

    primary = buildStyle(styles[0])
    if not primary:
        return None
    secondary = buildStyle(styles[1]) if len(styles) > 1 else None

    statPerks = perks.get('statPerks') if isinstance(perks.get('statPerks'), dict) else {}
    shards = []
    for key in ('offense', 'flex', 'defense'):
        shardId = statPerks.get(key)
        info = runeMap.get('shards', {}).get(str(shardId))
        if info:
            shards.append({"id": shardId, "name": info.get('name', ''), "icon": info.get('icon', '')})

    return {"primary": primary, "secondary": secondary, "shards": shards}


def regionToPlatform(region):
    if region == "na1":
        return "americas"
    if region in ("euw1", "eun1"):
        return "europe"
    return None


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
    
    connection = None
    cursor = None

    try:
        # Establish a connection to the PostgreSQL server
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection:
            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            try:
                query = (
                    'INSERT INTO "riotIDData" '
                    '("riotID", "puuid") '
                    'VALUES '
                    '(%s, %s) '
                    'ON CONFLICT ("riotID") DO NOTHING;'
                )
                data = (riotID, riotIDPuuid)
                cursor.execute(query, data)

            except IndexError:
                pass

            except psycopg2.Error as e:
                if e.pgcode == '23505':  # Unique violation error code in PostgreSQL
                    pass
                else:
                    print(e)

            connection.commit()

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL Server: {e}")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

# Insert match history into PostgreSQL
def insertDatabaseMatchHistory(matchHistoryGames):
    try:
        # Establish a connection to the PostgreSQL server
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection:
            # Create a cursor object to interact with the database
            cursor = connection.cursor()
            try:
                for game in matchHistoryGames:
                    try:
                        participantList = json.dumps(game['gamedata']['participants'])
                        matchDataList = json.dumps(game['matchData'])
                    except:
                        return None
                    query = (
                        'INSERT INTO "matchHistory" '
                        '("gameID", "gameVer", "riotID", "gameDurationMinutes", "gameCreationTimestamp", "gameEndTimestamp", "queueType", "gameDate", "participants", "matchData") '
                        'VALUES '
                        '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
                        'ON CONFLICT ("gameID", "riotID") DO NOTHING'
                    )

                    data = (
                        game['gamedata']['gameID'],
                        game['gamedata']['gameVer'],
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

            except psycopg2.Error as e:
                if e.pgcode == '23505':  # Unique violation error code in PostgreSQL
                    print(e)
                    pass
                else:
                    print(e)

            # Commit the changes
            connection.commit()

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL Server: {e}")

    finally:
        # Close the cursor and connection when done
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

# Insert ranked info into PostgreSQL
def insertDatabaseRankedInfo(puuid, summonerID, riotID, tier, rank, leaguePoints, queueType, wins, losses):
    try:
        # Establish a connection to the PostgreSQL server
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection:
            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            try:
                query = (
                    'INSERT INTO "summonerRankedInfo" '
                    '("encryptedPUUID", "summonerID", "riotID", "tier", "rank", "leaguePoints", "queueType", "wins", "losses") '
                    'VALUES '
                    '(%s, %s, %s, %s, %s, %s, %s, %s, %s) '
                    'ON CONFLICT ("encryptedPUUID") DO UPDATE SET '
                    '"summonerID" = EXCLUDED."summonerID", '
                    '"riotID" = EXCLUDED."riotID", '
                    '"tier" = EXCLUDED."tier", '
                    '"rank" = EXCLUDED."rank", '
                    '"leaguePoints" = EXCLUDED."leaguePoints", '
                    '"queueType" = EXCLUDED."queueType", '
                    '"wins" = EXCLUDED."wins", '
                    '"losses" = EXCLUDED."losses";'
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

            except psycopg2.Error as e:
                if e.pgcode == '23505':  # Unique violation error code in PostgreSQL
                    pass
                else:
                    print(e)

            connection.commit()

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL Server: {e}")

    finally:
        # Close the cursor and connection when done
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

def rankIsUnranked(rankData):
    if not rankData:
        return True
    data = rankData[0] if isinstance(rankData, list) else rankData
    if not isinstance(data, dict):
        return True
    return str(data.get('tier', '')).upper() == 'UNRANKED'


# Refresh one participant's Ranked Solo/Duo entry. Returns a client-ready rank
# dict, "UNRANKED" when Riot has no solo queue entry, or None on a failed call.
# A 429 is reported separately so callers can stop instead of hammering Riot.
def queryRankedInfoByPuuid(encryptedSummonerPUUID, region, riotID, RIOTAPIKEY):
    if not encryptedSummonerPUUID:
        return None
    if region not in ("na1", "euw1", "eun1"):
        return None

    try:
        ranked_info_response = requests.get(
            f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/"
            f"{quote(encryptedSummonerPUUID, safe='')}?api_key={RIOTAPIKEY}",
            timeout=15,
        )
        if ranked_info_response.status_code == 429:
            return {"rateLimited": True}
        ranked_info_response.raise_for_status()
        rankedInfo = ranked_info_response.json()
    except (requests.exceptions.RequestException, ValueError):
        return None

    if not isinstance(rankedInfo, list):
        return None

    soloQueueRankInfo = None
    for entry in rankedInfo:
        if isinstance(entry, dict) and entry.get("queueType") == "RANKED_SOLO_5x5":
            soloQueueRankInfo = entry
            break

    if not soloQueueRankInfo:
        # Cache the negative result so an unranked player is not queried again
        # every time a scoreboard is expanded.
        insertDatabaseRankedInfo(
            encryptedSummonerPUUID,
            "",
            riotID,
            "UNRANKED",
            "",
            0,
            "RANKED_SOLO_5x5",
            0,
            0,
        )
        return "UNRANKED"

    rankData = {
        "encryptedPUUID": encryptedSummonerPUUID,
        "summonerID": soloQueueRankInfo.get("leagueId", ""),
        "riotID": riotID,
        "tier": soloQueueRankInfo.get("tier", ""),
        "rank": soloQueueRankInfo.get("rank", ""),
        "leaguePoints": soloQueueRankInfo.get("leaguePoints", 0),
        "queueType": soloQueueRankInfo.get("queueType", "RANKED_SOLO_5x5"),
        "wins": soloQueueRankInfo.get("wins", 0),
        "losses": soloQueueRankInfo.get("losses", 0),
    }

    insertDatabaseRankedInfo(
        rankData["encryptedPUUID"],
        rankData["summonerID"],
        rankData["riotID"],
        rankData["tier"],
        rankData["rank"],
        rankData["leaguePoints"],
        rankData["queueType"],
        rankData["wins"],
        rankData["losses"],
    )

    return rankData


def queryRankedInfo(encryptedSummonerPUUID, region, riotID, RIOTAPIKEY):
    result = queryRankedInfoByPuuid(encryptedSummonerPUUID, region, riotID, RIOTAPIKEY)
    if isinstance(result, dict):
        if result.get("rateLimited"):
            return "Riot rate limit reached."
        return "Ranked information inserted successfully."
    if result == "UNRANKED":
        return "No Ranked Solo/Duo data found for this summoner."
    return "Could not retrieve ranked information."

# Query riotID information from Riot API
def queryRiotIDInfo(riotGameName, riotTagLine, region, RIOTAPIKEY):
    if region == "na1":
        platform = "americas"
    elif region in ("euw1", "eun1"):
        platform = "europe"
    else:
        return None

    try:
        response = requests.get(
            f"https://{platform}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
            f"{quote(riotGameName, safe='')}/{quote(riotTagLine, safe='')}?api_key={RIOTAPIKEY}",
            timeout=15,
        )
        response.raise_for_status()
        riotIDData = response.json()
    except (requests.exceptions.RequestException, ValueError):
        return None

    return riotIDData.get('puuid')



def fetchMatchById(matchID, region, RIOTAPIKEY):
    """Fetch one match from Riot. Used to backfill full rune pages for older rows."""
    platform = regionToPlatform(region)
    if not platform or not matchID:
        return None

    try:
        response = requests.get(
            f"https://{platform}.api.riotgames.com/lol/match/v5/matches/{quote(matchID, safe='')}"
            f"?api_key={RIOTAPIKEY}",
            timeout=15,
        )
        response.raise_for_status()
        matchData = response.json()
    except (requests.exceptions.RequestException, ValueError):
        return None

    return matchData if isinstance(matchData, dict) else None


def updateMatchRunePages(gameID, runePagesByPuuid):
    """Persist backfilled rune pages so each match is only fetched once."""
    if not gameID or not runePagesByPuuid:
        return 0

    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        cursor = connection.cursor()
        cursor.execute(
            'SELECT "riotID", "matchData", "participants" FROM "matchHistory" WHERE "gameID" = %s',
            (gameID,),
        )
        rows = cursor.fetchall()
        updatedRows = 0

        for riotID, storedMatchData, storedParticipants in rows:
            matchData = storedMatchData
            participants = storedParticipants
            if isinstance(matchData, str):
                try:
                    matchData = json.loads(matchData)
                except ValueError:
                    continue
            if isinstance(participants, str):
                try:
                    participants = json.loads(participants)
                except ValueError:
                    participants = []
            if not isinstance(matchData, list):
                continue

            changed = False
            for index, participant in enumerate(matchData):
                if not isinstance(participant, dict):
                    continue
                puuid = participant.get('puuid')
                if not puuid and isinstance(participants, list) and index < len(participants):
                    puuid = participants[index]
                if puuid in runePagesByPuuid:
                    participant['puuid'] = puuid
                    participant['runePage'] = runePagesByPuuid[puuid]
                    changed = True

            if changed:
                cursor.execute(
                    'UPDATE "matchHistory" SET "matchData" = %s WHERE "gameID" = %s AND "riotID" = %s',
                    (json.dumps(matchData), gameID, riotID),
                )
                updatedRows += 1

        connection.commit()
        return updatedRows

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL Server: {e}")
        return 0

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# It doesnt just do a unique id check both ways but it checks to see what elements from list 2 are NOT in list 1. This way it only checks to see what game IDs are not in the database and not what ids in the database are in the past 20 game IDs searched.
# It doesnt just do a unique id check both ways but it checks to see what elements from list 2 are NOT in list 1.
def findUniqueIDs(list1, list2):
    if list1 is None:
        list1 = []  # Ensure list1 is an empty list if None
    
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
        platform = "americas"
    elif region in ("euw1", "eun1"):
        platform = "europe"
    else:
        return 0

    try:
        matches = requests.get(
            f"https://{platform}.api.riotgames.com/lol/match/v5/matches/by-puuid/{quote(puuid, safe='')}/ids"
            f"?queue=420&start={startPosition}&count={reqCount}&api_key={APIKEY}",
            timeout=15,
        )
        matches.raise_for_status()
        matchIDs = matches.json()
    except (requests.exceptions.RequestException, ValueError):
        return 0

    
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
    
    # Riot returns a list of match IDs directly.
    matchList = matchIDs if isinstance(matchIDs, list) else []

    # Gets the IDs for summonerName from the DB as a list of gameIDs
    gameIDsFromDB = fetchGameIDsFromDB(riotID)
    # Gets the unique IDs between the past 20 matches in the request that was made and all all of the IDs that are associated with the summoner searched in the DB
    # This might prove to be a performance issue if the DB accumulates enough entries on a single user the search will take long?

    uniqueGameIDs = findUniqueIDs(gameIDsFromDB, matchList)

    # Itterates through Match ID list and gets match data
    # Appends it to a new dictionary
    matchData = []

    for matchID in uniqueGameIDs:
        try:
            response = requests.get(
                f"https://{platform}.api.riotgames.com/lol/match/v5/matches/{quote(matchID, safe='')}?api_key={APIKEY}",
                timeout=15,
            )
            response.raise_for_status()
            matchData.append(response.json())
        except (requests.exceptions.RequestException, ValueError):
            continue

        
    
    history = {}
    gameData = []
    for i in matchData:
        history = {}
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
                    'gameID': i['metadata']['matchId'], 
                    'gameVer': i['info']['gameVersion'],
                    #'userSummoner': profileData['name'],
                    'riotID': riotID,
                    'gameDurationMinutes': getGameTime(i['info']['gameDuration']),
                    'gameCreationTimestamp': i['info']['gameCreation'],
                    'gameEndTimestamp': i['info']['gameEndTimestamp'],
                    'queueType': queueType,
                    'gameDate': date,
                    'participants': i['metadata']['participants']                        
                },
                'matchData' : []
            }
            for participant in i['info']['participants']:
                newEntry = {
                    "riotID": f'{participant["riotIdGameName"]}#{participant["riotIdTagline"]}',
                    "puuid": participant.get('puuid', ''),
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
                    "secondaryRune": translateItemCodesToNames(runeIcons, str(participant['perks']['styles'][1]['style'])),
                    "runePage": buildRunePage(participant.get('perks')),
                }
                
                history['matchData'].append(newEntry)
        
        except KeyError:
            pass

        if len(history.get('matchData', [])) > 1:
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
                'gameID': matchData['metadata']['matchId'], 
                'gameVer': matchData['info']['gameVersion'],
                #'userSummoner': profileData['name'],
                'riotID': f"{matchData['info']['participants'][0]['riotIdGameName']}#{matchData['info']['participants'][0]['riotIdTagline']}",
                'gameDurationMinutes': getGameTime(int(matchData['info']['gameDuration'])),
                'gameCreationTimestamp': matchData['info']['gameCreation'],
                'gameEndTimestamp': matchData['info']['gameEndTimestamp'],
                'queueType': queueType,
                'gameDate': date,
                'participants': matchData['metadata']['participants']                        
            },
            'matchData' : []
        }
        
        for participant in matchData['info']['participants']:
            newEntry = {
                "riotID": f'{participant["riotIdGameName"]}#{participant["riotIdTagline"]}',
                "puuid": participant.get('puuid', ''),
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
                "secondaryRune": translateItemCodesToNames(runeIcons, str(participant['perks']['styles'][1]['style'])),
                "runePage": buildRunePage(participant.get('perks')),
            }
            
            history['matchData'].append(newEntry)
    
    except KeyError:
        pass
    
    if len(history['matchData']) > 1:
        gameData.append(history)

    insertDatabaseMatchHistory(gameData)
