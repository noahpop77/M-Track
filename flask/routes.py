from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import logging
from configparser import ConfigParser
import json
from os.path import abspath, dirname

sys.path.append(dirname(dirname(abspath(__file__))))
from mTrack.decayTracker import *
from mTrack.update import *
from mTrack.fetch import *
from flask import request


# Config file initiators for use in getting API key from config.ini
# in the sanity check for the /addSummoner API endpoint
file = "../config.ini"
config = ConfigParser()
config.read(file)
RIOTAPIKEY = config['KEYS']['riotapi']

# init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

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







# TODO: Need to decide what I am going to do with the home page.
@app.route('/', methods=['GET'])
def homePage():
    #logging.info(f"Connection incoming from - {request.remote_addr} to Homepage")
    #return render_template('mtrack.html')
    return render_template('mtrack.html')




# Main search function associated with the websites searchbar.
@app.route('/showMore', methods=['POST'])
def showMore():
    # Takes input name from request body
    # Splits riotID and loads it into variables for use later
    ingres = request.data.decode("utf8")
    showMoreDict = json.loads(ingres)

    summonerSearchDict = json.loads(ingres)
    regionSelect = summonerSearchDict['regionSelect']

    riotGameName, riotTagLine = riotSplitID(showMoreDict['searchedUser'])
    riotID = f"{riotGameName}#{riotTagLine}"
    

    gameIDs = showMoreDict['excludeGameIDs']
    

    # This try except clause will take the riotID gamename and tagline
    # and get the summoner name and PUUID associated with it for use in
    # future functions
    # The ordering of this block matters to save time execution on the 2 API requests
    try:
        riotIDPuuid = fetchFromRiotIDDB(riotID)
    except TypeError:
        riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, regionSelect, RIOTAPIKEY)
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
    ingres = request.data.decode("utf8")
    summonerSearchDict = json.loads(ingres)
    regionSelect = summonerSearchDict['regionSelect']

    riotGameName, riotTagLine = riotSplitID(summonerSearchDict['summonerName'])
    riotID = f"{riotGameName}#{riotTagLine}"
    
    # This try except clause will take the riotID gamename and tagline
    # and get the summoner name and PUUID associated with it for use in
    # future functions
    # The ordering of this block matters to save time execution on the 2 API requests
    riotIDPuuid = fetchFromRiotIDDB(riotID)
    if riotIDPuuid == None:
        riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, regionSelect, RIOTAPIKEY)
        insertDatabaseRiotID(riotID, riotIDPuuid)
        
    # Gets gamedata from the DB associated with the summonerName to look for pre-existing data
    gameData = fetchFromMatchHistoryDB(riotID, 20)

    # If there is no pre-existing data it will run mtrack(get new data) and then pull it from the database
    try:
        if len(gameData) < 1:
            mtrack(riotID, riotIDPuuid, regionSelect, RIOTAPIKEY, 20)
            gameData = fetchFromMatchHistoryDB(riotID, 20)
    except TypeError:
        mtrack(riotID, riotIDPuuid, regionSelect, RIOTAPIKEY, 20)
        gameData = fetchFromMatchHistoryDB(riotID, 20)

    matchData = []
    
    
    for i in gameData:
        matchData.append(i['matchData'])
    queryRankedInfo(riotIDPuuid, regionSelect, riotID, RIOTAPIKEY)
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
    ingres = request.data.decode("utf8")
    getHistoryDict = json.loads(ingres)

    riotID = getHistoryDict['riotID']
    regionSelect = getHistoryDict['regionSelect']

    riotGameName, riotTagLine = riotSplitID(riotID)


    # This try except clause will take the riotID gamename and tagline
    # and get the summoner name and PUUID associated with it for use in
    # future functions
    # The ordering of this block matters to save time execution on the 2 API requests
    try:
        riotIDPuuid = fetchFromRiotIDDB(riotID)
    except TypeError:
        riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, regionSelect, RIOTAPIKEY)
        insertDatabaseRiotID(riotID, riotIDPuuid)
    
    # When the update button is pressed it will requery the ranked data associated with the account to update the database
    queryRankedInfo(riotIDPuuid, regionSelect, riotID, RIOTAPIKEY)
    
    mtrack(riotID, riotIDPuuid, regionSelect, RIOTAPIKEY, 20)
    gameData = fetchFromMatchHistoryDB(riotID, 20)
    
    if len(gameData) < 1:
        # Searches the new summoner and adds their information to the DB
        mtrack(riotID, riotIDPuuid, regionSelect, RIOTAPIKEY, 20)
        # After the information was just retrieved from the riot API and saved to the DB we fetch it from that DB
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
            
    return jsonify({ 
        'gameData': gameData,
        'playerStats': playerStats,
        'matchData': matchData,
        'riotID': riotID
    })





@app.route('/getRank', methods=['POST'])
def getRank():
    ingres = request.data.decode("utf8")
    summonerSearchDict = json.loads(ingres)

    riotID = summonerSearchDict['riotID']
    regionSelect = summonerSearchDict['regionSelect']

    riotGameName, riotTagLine = riotSplitID(riotID)
    riotID = f"{riotGameName}#{riotTagLine}"

    try:
        riotIDPuuid = fetchFromRiotIDDB(riotID)
        
    except TypeError:
        riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, regionSelect, RIOTAPIKEY)
        insertDatabaseRiotID(riotID, riotIDPuuid)
    
    summonerRankDict = fetchFromSummonerRankedInfoDB(riotIDPuuid)
    try:
        if len(summonerRankDict) > 1:
            queryRankedInfo(riotIDPuuid, regionSelect, riotID, RIOTAPIKEY)
            summonerRankDict = fetchFromSummonerRankedInfoDB(riotIDPuuid)
    except TypeError:
        return jsonify({"error": "No user found, sorry bud"}), 200
    
    return summonerRankDict



@app.route('/updateRank', methods=['POST'])
def updateRank():
    ingres = request.data.decode("utf8")
    
    summonerSearchDict = json.loads(ingres)
    regionSelect = summonerSearchDict['regionSelect']

    riotGameName, riotTagLine = riotSplitID(summonerSearchDict['riotID'])
    riotID = f"{riotGameName}#{riotTagLine}"

    riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, regionSelect, RIOTAPIKEY)
    insertDatabaseRiotID(riotID, riotIDPuuid)
    riotIDPuuid = fetchFromRiotIDDB(riotID)

    summonerRankDict = fetchFromSummonerRankedInfoDB(riotIDPuuid)
    
    if summonerRankDict == None:
        return jsonify({"error": "No user found, sorry bud"}), 200
    
    return summonerRankDict


@app.route('/getItemIcons/<path:filename>', methods=['GET'])
def getItemIcons(filename):
    # Specify the path to the folder containing PNGs
    icons_folder = './static/img/itemIcons'
    # Check if the file with the given name exists
    file_path = os.path.join(icons_folder, filename)
    if os.path.exists(file_path):
        # Return the PNG file as a response
        return send_file(file_path, mimetype='image/png')
    else:
        # If the file doesn't exist, return an error response
        return "Error: The images sprite is not in the correct location"

@app.route('/getChampIcons/<path:filename>', methods=['GET'])
def getChampIcons(filename):
    # Specify the path to the folder containing PNGs
    icons_folder = './static/img/champIcons'
    # Check if the file with the given name exists
    file_path = os.path.join(icons_folder, filename)
    if os.path.exists(file_path):
        # Return the PNG file as a response
        return send_file(file_path, mimetype='image/png')
    else:
        # If the file doesn't exist, return an error response
        return "Error: The images sprite is not in the correct location"

@app.route('/getSummonerIcons/<path:filename>', methods=['GET'])
def getSummonerIcons(filename):
    # Specify the path to the folder containing PNGs
    icons_folder = './static/img/summonerIcons'
    # Check if the file with the given name exists
    file_path = os.path.join(icons_folder, filename)
    if os.path.exists(file_path):
        # Return the PNG file as a response
        return send_file(file_path, mimetype='image/png')
    else:
        # If the file doesn't exist, return an error response
        return "Error: The images sprite is not in the correct location"

@app.route('/getRuneIcons/<path:filename>', methods=['GET'])
def getRuneIcons(filename):
    # Specify the path to the folder containing PNGs
    icons_folder = './static/img/runeIcons'
    # Check if the file with the given name exists
    file_path = os.path.join(icons_folder, filename)
    if os.path.exists(file_path):
        # Return the PNG file as a response
        return send_file(file_path, mimetype='image/png')
    else:
        # If the file doesn't exist, return an error response
        return "Error: The images sprite is not in the correct location"














# ==================================================================
# STRICTLY FOR TESTING
# TEST API ENDPOINT ONLY USED IN CONJUNCTION WITH noahpop77/Papy
@app.route('/addMatch', methods=['POST'])
def addMatch():
    ingres = request.data.decode("utf8")
    matchData = json.loads(ingres)

    injectMatchJsonIntoDatabase(json.loads(matchData))
    return jsonify({
        'statusCode': "200",
        'body': "Request received and pritned"
    })


@app.route('/printJson', methods=['POST'])
def print_json():
    ingres = request.data.decode("utf8")
    #jsonBody = json.loads(ingres)
    print(json.loads(ingres))
    return jsonify({
        'statusCode': "200",
        'body': "Request received and pritned"
    })

# ==================================================================






# Run Server
if __name__ == '__main__':
    try:
        print(f"Running app at - {config['SITE']['address']}:{config['SITE']['port']}")
        app.run(debug=True, host=config['SITE']['address'], port=config['SITE']['port'])

    except KeyboardInterrupt:
        sys.exit(0)