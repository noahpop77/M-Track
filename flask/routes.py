from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
import sys
import logging
from configparser import ConfigParser
from os.path import abspath, dirname

sys.path.append(dirname(dirname(abspath(__file__))))
from mTrack.update import *
from mTrack.fetch import *


# Config file initiators for use in getting API key from config.ini
file = "../config.ini"
config = ConfigParser()
config.read(file)
# Prefer the environment variable so the key does not have to live in a file.
RIOTAPIKEY = os.environ.get("RIOT_API_KEY") or config.get('KEYS', 'riotapi', fallback='')

# init app
app = Flask(__name__)

STATIC_DIR = os.path.join(dirname(abspath(__file__)), 'static')

# Bump the query string on CSS/JS links whenever one of those files changes so
# browsers pick up the new version even though /static/ is cached for a day.
def staticAssetVersion():
    latest = 0
    for root, _, filenames in os.walk(STATIC_DIR):
        for filename in filenames:
            if not filename.endswith(('.css', '.js')):
                continue
            try:
                latest = max(latest, os.path.getmtime(os.path.join(root, filename)))
            except OSError:
                pass
    return str(int(latest))

@app.context_processor
def injectStaticAssetVersion():
    return {'static_version': staticAssetVersion()}

ALLOWED_REGIONS = {"na1", "euw1", "eun1"}

# Shared request validation so a malformed body returns 400 instead of a 500.
def getRequestJSON(requiredKeys):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, (jsonify({"error": "Request body must be JSON."}), 400)

    for key in requiredKeys:
        if key not in payload:
            return None, (jsonify({"error": f"Missing field: {key}"}), 400)

        value = payload[key]
        if key == "excludeGameIDs":
            if not isinstance(value, list):
                return None, (jsonify({"error": "excludeGameIDs must be a list."}), 400)
        elif not isinstance(value, str):
            return None, (jsonify({"error": f"{key} must be a string."}), 400)

    if "regionSelect" in payload and payload["regionSelect"] not in ALLOWED_REGIONS:
        return None, (jsonify({"error": "Unsupported region."}), 400)

    return payload, None

def testEndpointsEnabled():
    return os.environ.get("MTRACK_ENABLE_TEST_ENDPOINTS") == "1"


def safeInt(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def clientRankFromRow(rankRow):
    """Trim a stored rank row down to the fields the scoreboard needs."""
    if not isinstance(rankRow, dict):
        return None

    tier = str(rankRow.get("tier") or "").upper()
    if not tier:
        return None
    if tier == "UNRANKED":
        return {"tier": "UNRANKED"}

    return {
        "tier": tier,
        "rank": str(rankRow.get("rank") or "").upper(),
        "leaguePoints": safeInt(rankRow.get("leaguePoints")),
        "wins": safeInt(rankRow.get("wins")),
        "losses": safeInt(rankRow.get("losses")),
    }


def enrichGameData(gameData):
    """Attach PUUIDs (for older stored matches) and cached ranks in one pass."""
    if not isinstance(gameData, list):
        return gameData

    puuids = []
    for game in gameData:
        if not isinstance(game, dict):
            continue

        participants = game.get("participants")
        if isinstance(participants, str):
            try:
                participants = json.loads(participants)
            except ValueError:
                participants = []
        if not isinstance(participants, list):
            participants = []

        matchData = game.get("matchData")
        if not isinstance(matchData, list):
            continue

        for index, participant in enumerate(matchData):
            if not isinstance(participant, dict):
                continue
            puuid = participant.get("puuid")
            if not puuid and index < len(participants):
                entry = participants[index]
                if isinstance(entry, dict):
                    entry = entry.get("puuid")
                if isinstance(entry, str):
                    puuid = entry
            if puuid:
                participant["puuid"] = puuid
                puuids.append(puuid)

    ranks = fetchRanksByPuuids(list(set(puuids))) if puuids else {}

    for game in gameData:
        if not isinstance(game, dict) or not isinstance(game.get("matchData"), list):
            continue
        for participant in game["matchData"]:
            if not isinstance(participant, dict):
                continue
            participant["rank"] = clientRankFromRow(ranks.get(participant.get("puuid")))

    return gameData

# Static files are fingerprinted by content in practice (sprites/CSS change
# rarely); let browsers cache them for a day while still honouring ETags.
@app.after_request
def addStaticCacheHeaders(response):
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=86400'
    elif response.mimetype == 'text/html':
        # Always revalidate pages so they pick up the current asset versions.
        response.headers['Cache-Control'] = 'no-cache'
    return response

# Initializes logger for fask routes

# Sets the log level of the default flask logger to ERROR so the log file doesnt get spammed
errorlog = logging.getLogger('werkzeug')
errorlog.setLevel(logging.ERROR)

# Ensure the directory exists
logDirectory = "../Logs"
logFile = "routes.log"
logPath = os.path.join(logDirectory, logFile)

# Check if the directory exists, if not, create it
if not os.path.exists(logDirectory):
    os.makedirs(logDirectory)

# Check if the file exists, if not, create it
if not os.path.exists(logPath):
    open(logPath, 'w').close()

# Set up logging
logging.basicConfig(level=logging.INFO, filename=logPath, encoding='utf-8')







@app.route('/', methods=['GET'])
def homePage():
    return render_template('mtrack.html')


@app.route('/classic', methods=['GET'])
def classicPage():
    return render_template('mtrack-classic.html')




# Main search function associated with the websites searchbar.
@app.route('/showMore', methods=['POST'])
def showMore():
    # Takes input name from request body
    # Splits riotID and loads it into variables for use later
    payload, error = getRequestJSON(["searchedUser", "excludeGameIDs", "regionSelect"])
    if error:
        return error

    regionSelect = payload["regionSelect"]
    riotGameName, riotTagLine = riotSplitID(payload["searchedUser"])
    if not riotTagLine:
        return jsonify({"error": "Riot ID must include a #tagline."}), 400
    riotID = f"{riotGameName}#{riotTagLine}"


    gameIDs = payload["excludeGameIDs"]

    # Resolve the PUUID explicitly: fetchFromRiotIDDB returns None for an
    # unknown Riot ID, it does not raise TypeError.
    riotIDPuuid = fetchFromRiotIDDB(riotID)
    if not riotIDPuuid:
        riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, regionSelect, RIOTAPIKEY)
        if not riotIDPuuid:
            return jsonify({"error": "Summoner not found."}), 404
        insertDatabaseRiotID(riotID, riotIDPuuid)

    startPosition = len(gameIDs)

    # Gets gamedata from the DB associated with the summonerName to look for pre-existing data
    gameData = fetchFromMatchHistoryDB(riotID, 20, startPosition)
    # If there is no pre-existing data it will run mtrack(get new data) and then pull it from the database
    
    
    if len(gameData) < 1:
        mtrack(riotID, riotIDPuuid, regionSelect, RIOTAPIKEY, 20, startPosition)
        gameData = fetchFromMatchHistoryDB(riotID, 20, startPosition)

    matchData = []
    for i in gameData:
        matchData.append(i['matchData'])
    
    # Player card data
    playerStats = []
    # Loops through match data, gets player card data and 
    for i in matchData:
        try:
            for player in i:
                
                if player['riotID'].lower() == riotID.lower():
                    playerStats.append(player)
                    break
        except IndexError:
            break
        except Exception as e:
            print(e)
    
    enrichGameData(gameData)

    return jsonify({ 
        'gameData': gameData,
        'playerStats': playerStats,
        'matchData': matchData,
        'riotID': riotID
    })










# Main search function associated with the websites searchbar.
@app.route('/summonerSearch', methods=['POST'])
def summonerSearch():
    #logging.info(f"Connection incoming from - {request.remote_addr} to /matchHistory")

    # Takes input name from request body
    # Splits riotID and loads it into variables for use later
    payload, error = getRequestJSON(["summonerName", "regionSelect"])
    if error:
        return error

    regionSelect = payload["regionSelect"]
    riotGameName, riotTagLine = riotSplitID(payload["summonerName"])
    if not riotTagLine:
        return jsonify({"error": "Riot ID must include a #tagline."}), 400
    riotID = f"{riotGameName}#{riotTagLine}"
    
    riotIDPuuid = fetchFromRiotIDDB(riotID)
    if not riotIDPuuid:
        riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, regionSelect, RIOTAPIKEY)
        if not riotIDPuuid:
            return jsonify({"error": "Summoner not found."}), 404
        insertDatabaseRiotID(riotID, riotIDPuuid)
    
    #print(riotIDPuuid)
    # Gets gamedata from the DB associated with the summonerName to look for pre-existing data
    gameData = fetchFromMatchHistoryDB(riotID, 20)

    # If there is no pre-existing data it will run mtrack(get new data) and then pull it from the database
    if len(gameData) < 1:
        mtrack(riotID, riotIDPuuid, regionSelect, RIOTAPIKEY, 20)
        gameData = fetchFromMatchHistoryDB(riotID, 20)

    matchData = []
    
    
    for i in gameData:
        matchData.append(i['matchData'])
    
    # Player card data
    playerStats = []
    # Loops through match data, gets player card data and 
    for i in matchData:
        try:
            for player in i:
                if player['riotID'].lower() == riotID.lower():
                    playerStats.append(player)
                    break
        except IndexError:
            break
        except Exception as e:
            print(e)

    enrichGameData(gameData)

    return jsonify({ 
        'gameData': gameData,
        'playerStats': playerStats,
        'matchData': matchData,
        'riotID': riotID
    })





# /getHistory is different from summonerSearch in that it will ALWAYS get new info rather than displaying existing data and only getting new data if there is no gamedata on the searched user like summonerSearch

# Endpoint hit when the update button is hit on the match history page
@app.route('/getHistory', methods=['POST'])
def getHistory():
    
    # Takes input name from request body
    # Splits riotID and loads it into variables for use later
    payload, error = getRequestJSON(["riotID", "regionSelect"])
    if error:
        return error

    riotID = payload["riotID"]
    regionSelect = payload["regionSelect"]

    riotGameName, riotTagLine = riotSplitID(riotID)
    if not riotTagLine:
        return jsonify({"error": "Riot ID must include a #tagline."}), 400
    riotID = f"{riotGameName}#{riotTagLine}"

    riotIDPuuid = fetchFromRiotIDDB(riotID)
    if not riotIDPuuid:
        riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, regionSelect, RIOTAPIKEY)
        if not riotIDPuuid:
            return jsonify({"error": "Summoner not found."}), 404
        insertDatabaseRiotID(riotID, riotIDPuuid)
    
    # When the update button is pressed it will requery the ranked data associated with the account to update the database
    queryRankedInfo(riotIDPuuid, regionSelect, riotID, RIOTAPIKEY)
    
    mtrack(riotID, riotIDPuuid, regionSelect, RIOTAPIKEY, 20)
    gameData = fetchFromMatchHistoryDB(riotID, 20)

    matchData = []
    for i in gameData:
        matchData.append(i['matchData'])

    playerStats = []
    # Loops through match data, gets player card data and 
    for i in matchData:
        try:
            for player in i:
                # lower() is mandatory
                # If user inputs a username with incorrect cases it will
                # force it to match the case of the check condition
                if player['riotID'].lower() == riotID.lower():
                    playerStats.append(player)
                    break
        except IndexError:
            break
        except Exception as e:
            print(e)
            
    enrichGameData(gameData)

    return jsonify({ 
        'gameData': gameData,
        'playerStats': playerStats,
        'matchData': matchData,
        'riotID': riotID
    })





@app.route('/getRank', methods=['POST'])
def getRank():
    payload, error = getRequestJSON(["riotID", "regionSelect"])
    if error:
        return error

    riotID = payload["riotID"]
    regionSelect = payload["regionSelect"]

    riotGameName, riotTagLine = riotSplitID(riotID)
    if not riotTagLine:
        return jsonify({"error": "Riot ID must include a #tagline."}), 400
    riotID = f"{riotGameName}#{riotTagLine}"

    riotIDPuuid = fetchFromRiotIDDB(riotID)
    if not riotIDPuuid:
        riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, regionSelect, RIOTAPIKEY)
        if not riotIDPuuid:
            return jsonify({"error": "Summoner not found."}), 404
        insertDatabaseRiotID(riotID, riotIDPuuid)

    # Always refresh before returning so the rank card is never stale.
    queryRankedInfo(riotIDPuuid, regionSelect, riotID, RIOTAPIKEY)
    summonerRankDict = fetchFromSummonerRankedInfoDB(riotIDPuuid)

    if not summonerRankDict or rankIsUnranked(summonerRankDict):
        return jsonify({"error": "No Ranked Solo/Duo data for this player."}), 404

    return jsonify(summonerRankDict)



@app.route('/updateRank', methods=['POST'])
def updateRank():
    payload, error = getRequestJSON(["riotID", "regionSelect"])
    if error:
        return error

    regionSelect = payload["regionSelect"]
    riotGameName, riotTagLine = riotSplitID(payload["riotID"])
    if not riotTagLine:
        return jsonify({"error": "Riot ID must include a #tagline."}), 400
    riotID = f"{riotGameName}#{riotTagLine}"

    riotIDPuuid = fetchFromRiotIDDB(riotID)
    if not riotIDPuuid:
        riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, regionSelect, RIOTAPIKEY)
        if not riotIDPuuid:
            return jsonify({"error": "Summoner not found."}), 404
        insertDatabaseRiotID(riotID, riotIDPuuid)

    queryRankedInfo(riotIDPuuid, regionSelect, riotID, RIOTAPIKEY)
    summonerRankDict = fetchFromSummonerRankedInfoDB(riotIDPuuid)
    
    if not summonerRankDict or rankIsUnranked(summonerRankDict):
        return jsonify({"error": "No Ranked Solo/Duo data for this player."}), 404
    
    return jsonify(summonerRankDict)


@app.route('/getLobbyRanks', methods=['POST'])
def getLobbyRanks():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be JSON."}), 400

    regionSelect = payload.get("regionSelect")
    if regionSelect not in ALLOWED_REGIONS:
        return jsonify({"error": "Unsupported region."}), 400

    players = payload.get("players")
    if not isinstance(players, list) or len(players) > 10:
        return jsonify({"error": "players must be a list of at most 10 players."}), 400

    fetchMissing = payload.get("fetchMissing") is True

    prepared = []
    puuids = []
    for player in players:
        if not isinstance(player, dict):
            return jsonify({"error": "Each player must be an object."}), 400

        riotID = player.get("riotID") if isinstance(player.get("riotID"), str) else ""
        puuid = player.get("puuid") if isinstance(player.get("puuid"), str) else ""
        if not puuid and riotID:
            puuid = fetchFromRiotIDDB(riotID) or ""
        if puuid:
            puuids.append(puuid)
        prepared.append({"riotID": riotID, "puuid": puuid})

    cached = fetchRanksByPuuids(list(set(puuids))) if puuids else {}
    ranks = {}
    missing = []

    for player in prepared:
        puuid = player["puuid"]
        if puuid and puuid in cached:
            ranks[puuid] = clientRankFromRow(cached[puuid])
        elif puuid or player["riotID"]:
            missing.append(player)

    rateLimited = False
    if fetchMissing:
        for player in missing:
            puuid = player["puuid"]
            riotID = player["riotID"]

            if not puuid:
                riotGameName, riotTagLine = riotSplitID(riotID)
                if not riotTagLine:
                    continue
                puuid = queryRiotIDInfo(riotGameName, riotTagLine, regionSelect, RIOTAPIKEY)
                if not puuid:
                    continue
                insertDatabaseRiotID(riotID, puuid)
                player["puuid"] = puuid

            result = queryRankedInfoByPuuid(puuid, regionSelect, riotID, RIOTAPIKEY)
            if isinstance(result, dict):
                if result.get("rateLimited"):
                    rateLimited = True
                    break
                ranks[puuid] = clientRankFromRow(result)
            elif result == "UNRANKED":
                ranks[puuid] = {"tier": "UNRANKED"}

    return jsonify({"ranks": ranks, "rateLimited": rateLimited})


@app.route('/getMatchRunes', methods=['POST'])
def getMatchRunes():
    payload, error = getRequestJSON(["gameID", "regionSelect"])
    if error:
        return error

    gameID = payload["gameID"].strip()
    if not gameID or len(gameID) > 32:
        return jsonify({"error": "Invalid game ID."}), 400

    match = fetchMatchById(gameID, payload["regionSelect"], RIOTAPIKEY)
    if not match:
        return jsonify({"error": "Could not load rune pages for this match."}), 404

    runeMap = loadRunePageMap()
    runePages = {}
    for participant in (match.get("info") or {}).get("participants") or []:
        if not isinstance(participant, dict):
            continue
        puuid = participant.get("puuid")
        page = buildRunePage(participant.get("perks"), runeMap)
        if puuid and page:
            runePages[puuid] = page

    if not runePages:
        return jsonify({"error": "No rune page data was found for this match."}), 404

    updateMatchRunePages(gameID, runePages)
    return jsonify({"runePages": runePages})


@app.route('/getItemIcons/<path:filename>', methods=['GET'])
def getItemIcons(filename):
    # send_from_directory safely rejects path traversal and missing files.
    return send_from_directory('./static/img/itemIcons', filename, max_age=86400)

@app.route('/getChampIcons/<path:filename>', methods=['GET'])
def getChampIcons(filename):
    return send_from_directory('./static/img/champIcons', filename, max_age=86400)

@app.route('/getSummonerIcons/<path:filename>', methods=['GET'])
def getSummonerIcons(filename):
    return send_from_directory('./static/img/summonerIcons', filename, max_age=86400)

@app.route('/getRuneIcons/<path:filename>', methods=['GET'])
def getRuneIcons(filename):
    return send_from_directory('./static/img/runeIcons', filename, max_age=86400)














# ==================================================================
# STRICTLY FOR TESTING
# TEST API ENDPOINT ONLY USED IN CONJUNCTION WITH noahpop77/Papy
# Disabled unless MTRACK_ENABLE_TEST_ENDPOINTS=1.
@app.route('/addMatch', methods=['POST'])
def addMatch():
    if not testEndpointsEnabled():
        return jsonify({"error": "Not found."}), 404

    matchData = request.get_json(silent=True)
    if not isinstance(matchData, dict):
        return jsonify({"error": "Request body must be JSON."}), 400

    injectMatchJsonIntoDatabase(matchData)
    return jsonify({
        'statusCode': "200",
        'body': "Request received and printed"
    })


@app.route('/printJson', methods=['POST'])
def print_json():
    if not testEndpointsEnabled():
        return jsonify({"error": "Not found."}), 404

    print(request.get_json(silent=True))
    return jsonify({
        'statusCode': "200",
        'body': "Request received and printed"
    })

# ==================================================================






# Run Server
if __name__ == '__main__':
    try:
        print(f"Running app at - {config['SITE']['address']}:{config['SITE']['port']}")
        app.run(
            debug=os.environ.get("FLASK_DEBUG") == "1",
            host=config['SITE']['address'],
            port=config['SITE']['port'],
        )

    except KeyboardInterrupt:
        sys.exit(0)