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

logging.basicConfig(level=logging.INFO, filename="../Logs/routes.log", encoding='utf-8')

# TODO: Need to decide what I am going to do with the home page.
@app.route('/', methods=['GET'])
def homePage():
    logging.info(f"Connection incoming from - {request.remote_addr} to Homepage")
    return render_template('mtrack.html')


# Actual webpage for the match history of a person
@app.route('/matchHistory', methods=['GET'])
def matchHistory():
    logging.info(f"Connection incoming from - {request.remote_addr} to /matchHistory")
    return render_template('matchHistory.html')






# Main search function associated with the websites searchbar.
@app.route('/showMore', methods=['POST'])
def showMore():

    # Takes input name from request body
    # Splits riotID and loads it into variables for use later
    ingres = request.data.decode("utf8")
    showMoreDict = json.loads(ingres)
    #print(showMoreDict)
    #print(type(showMoreDict))

    riotGameName, riotTagLine = riotSplitID(showMoreDict['searchedUser'])
    riotID = f"{riotGameName}#{riotTagLine}"
    

    alreadyShownGameIDs = showMoreDict['excludeGameIDs']
    gameIDs = alreadyShownGameIDs.split(",")
    

    # This try except clause will take the riotID gamename and tagline
    # and get the summoner name and PUUID associated with it for use in
    # future functions
    # The ordering of this block matters to save time execution on the 2 API requests
    try:
        summonerName, riotIDPuuid = fetchFromRiotIDDB(riotID)
    except TypeError:
        summonerName, riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, RIOTAPIKEY)
        insertDatabaseRiotID(riotID, summonerName, riotIDPuuid)

    startPosition = len(gameIDs)
    # Gets gamedata from the DB associated with the summonerName to look for pre-existing data
    gameData = fetchFromMatchHistoryDB(summonerName, 10, startPosition)
    # If there is no pre-existing data it will run mtrack(get new data) and then pull it from the database
    
    
    if len(gameData) < 1:
        mtrack(summonerName, riotIDPuuid, RIOTAPIKEY, 10, startPosition)
        gameData = fetchFromMatchHistoryDB(summonerName, 10, startPosition)

    matchData = []
    for i in gameData:
        matchData.append(json.loads(i['matchdata']))
    
    # Player card data
    playerStats = []
    # Loops through match data, gets player card data and 
    for i in matchData:
        try:
            for player in i:
                if player['sumName'].lower() == summonerName.lower():
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
        'summonerName': summonerName
    })









# TODO: What the fuck is wrong with item ID 3191?

# Main search function associated with the websites searchbar.
@app.route('/summonerSearch', methods=['POST'])
def summonerSearch():
    logging.info(f"Connection incoming from - {request.remote_addr} to /matchHistory")

    # Takes input name from request body
    # Splits riotID and loads it into variables for use later
    ingres = request.data.decode("utf8")
    riotGameName, riotTagLine = riotSplitID(ingres)
    riotID = f"{riotGameName}#{riotTagLine}"

    # This try except clause will take the riotID gamename and tagline
    # and get the summoner name and PUUID associated with it for use in
    # future functions
    # The ordering of this block matters to save time execution on the 2 API requests
    try:
        summonerName, riotIDPuuid = fetchFromRiotIDDB(riotID)
    except TypeError:
        summonerName, riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, RIOTAPIKEY)
        insertDatabaseRiotID(riotID, summonerName, riotIDPuuid)

    # Gets gamedata from the DB associated with the summonerName to look for pre-existing data
    gameData = fetchFromMatchHistoryDB(summonerName, 10)
    # If there is no pre-existing data it will run mtrack(get new data) and then pull it from the database
    if len(gameData) < 1:
        mtrack(summonerName, riotIDPuuid, RIOTAPIKEY, 10)
        gameData = fetchFromMatchHistoryDB(summonerName, 10)

    matchData = []
    for i in gameData:
        matchData.append(json.loads(i['matchdata']))
    #print(matchData)
    # Player card data
    playerStats = []
    # Loops through match data, gets player card data and 
    for i in matchData:
        try:
            for player in i:
                if player['sumName'].lower() == summonerName.lower():
                    playerStats.append(player)
                    break
        except IndexError:
            break
        except Exception as e:
            print(e)
    #print(matchData[0])
    return jsonify({ 
        'gameData': gameData,
        'playerStats': playerStats,
        'matchData': matchData,
        'summonerName': summonerName
    })



# /getHistory is different from summonerSearch in that it will ALWAYS get new info rather than displaying existing data and only getting new data if there is no gamedata on the searched user like summonerSearch

# Endpoint hit when the update button is hit on the match history page
@app.route('/getHistory', methods=['POST'])
def getHistory():
    
    # Takes input name from request body
    # Splits riotID and loads it into variables for use later
    ingres = request.data.decode("utf8")
    riotGameName, riotTagLine = riotSplitID(ingres)
    riotID = f"{riotGameName}#{riotTagLine}"


    # This try except clause will take the riotID gamename and tagline
    # and get the summoner name and PUUID associated with it for use in
    # future functions
    # The ordering of this block matters to save time execution on the 2 API requests
    try:
        summonerName, riotIDPuuid = fetchFromRiotIDDB(riotID)
    except TypeError:
        summonerName, riotIDPuuid = queryRiotIDInfo(riotGameName, riotTagLine, RIOTAPIKEY)
        insertDatabaseRiotID(riotID, summonerName, riotIDPuuid)


    mtrack(summonerName, riotIDPuuid, RIOTAPIKEY, 10)
    gameData = fetchFromMatchHistoryDB(summonerName, 10)
    
    if len(gameData) < 1:
        # Searches the new summoner and adds their information to the DB
        mtrack(summonerName, riotIDPuuid, RIOTAPIKEY, 10)
        # After the information was just retrieved from the riot API and saved to the DB we fetch it from that DB
        gameData = fetchFromMatchHistoryDB(summonerName, 10)

    matchData = []
    for i in gameData:
        matchData.append(json.loads(i['matchdata']))

    playerStats = []
    # Loops through match data, gets player card data and 
    for i in matchData:
        try:
            for player in i:
                # lower() is mandatory
                # If user inputs a username with incorrect cases it will
                # force it to match the case of the check condition
                if player['sumName'].lower() == summonerName.lower():
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
        'summonerName': summonerName
    })



# TODO: Need to edit the MySQL database to include a new column which will contain the rank data of the account that was searched such as Division and LP count. That information will get displayed in the div which has the ID of player-container. The ranked information will appear in a card above where the match history is displayed. 






# Get champ icons
@app.route('/getChampIcon', methods=['POST'])
def getChampIcon():
    ingres = request.data.decode("utf8")

    # Specify the path to the folder containing PNGs
    icons_folder = './static/img/champIcons'

    # Check if the file with the given name exists
    file_path = os.path.join(icons_folder, f'{ingres}.png')
    if os.path.exists(file_path):
        # Return the PNG file as a response
        return send_file(file_path, mimetype='image/png')
    else:
        # If the file doesn't exist, return an error response
        return "File not found", 404


# Get summoner spell icons
@app.route('/getSummoners', methods=['POST'])
def getSummoners():
    ingres = request.data.decode("utf8")

    # Specify the path to the folder containing PNGs
    icons_folder = './static/img/summonerIcons'

    # Check if the file with the given name exists
    file_path = os.path.join(icons_folder, f'{ingres}.png')
    if os.path.exists(file_path):
        # Return the PNG file as a response
        return send_file(file_path, mimetype='image/png')
    else:
        # If the file doesn't exist, return an error response
        return "File not found", 404


# Get summoner spell icons
@app.route('/getItemIcon', methods=['POST'])
def getItemIcon():
    ingres = request.data.decode("utf8")

    # Specify the path to the folder containing PNGs
    icons_folder = './static/img/itemIcons'

    # Check if the file with the given name exists
    file_path = os.path.join(icons_folder, f'{ingres}.png')
    if os.path.exists(file_path):
        # Return the PNG file as a response
        return send_file(file_path, mimetype='image/png')
    else:
        # If the file doesn't exist, return an error response
        #return "File not found", 404
        blank = os.path.join(icons_folder, f'NA.png')
        return send_file(blank, mimetype='image/png')

# TODO: Implement an endpoint that when queried will get the rank and LP amount of a player.
# To get this information you will need to leverage 2 APIs
# /lol/league/v4/entries/by-summoner/{encryptedSummonerId}
    # This will get the actual ranked data
# /lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}
# /lol/summoner/v4/summoners/by-name/{summonerName}
    # Both of these APIs work to get the ID field.
    # Plug the ID field into the first API to get the ranked data

#@app.route('/getItemIcons/<path:filename>', methods=['GET'])
#def getItemIcons(filename):
#    # Specify the path to the folder containing PNGs
#    icons_folder = './static/img/itemIcons'
#    print("SPRITE ENDPOINT HIT")
#    # Check if the file with the given name exists
#    file_path = os.path.join(icons_folder, filename)
#    if os.path.exists(file_path):
#        # Return the PNG file as a response
#        return send_file(file_path, mimetype='image/png')
#    else:
#        # If the file doesn't exist, return an error response
#        return "Error: The images sprite is not in the correct location"

# Run Server
if __name__ == '__main__':
    try:
        os.system("clear")

        print("Starting Flask app 'routes.py'")
        print(f"Running app at - {config['SITE']['address']}:{config['SITE']['port']}")

        app.run(debug=True, host=config['SITE']['address'], port=config['SITE']['port'])

    except KeyboardInterrupt:
        sys.exit(0)