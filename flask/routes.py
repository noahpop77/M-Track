from flask import Flask, render_template, request, jsonify
import os
import sys
import logging
from configparser import ConfigParser
import json

from os.path import abspath, dirname

from mTrack.fetch import fetchFromDB
from mTrack.update import mtrack
from mTrack.decayTracker import dtrack


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

@app.route('/getSummoner', methods=['POST', 'GET'])
def addSummoner():
    # Data sent to api decoded and ready to use as a string
    ingres = request.data.decode("utf8")
    
    # RETURN DATA FOR REQUEST (sent to user)
    #print(f"--------\nConnection from: {request.remote_addr}\nName Searched: {ingres}")
    decayTimer = dtrack(ingres, RIOTAPIKEY)
    return decayTimer

@app.route('/', methods=['GET'])
def homePage():
    logging.info(f"Connection incoming from - {request.remote_addr} to Homepage")
    return render_template('mtrack.html')

@app.route('/matchHistory', methods=['GET'])
def matchHistory():
    logging.info(f"Connection incoming from - {request.remote_addr} to /matchHistory")

    #ingres = request.data.decode("utf8")
    #print(ingres)

    gameData = fetchFromDB("chaddam", 15)
    
    matchData = []
    for i in gameData:
        matchData.append(json.loads(i['matchdata']))


    playerStats = []

    # Loops through match data, gets player card data and 
    for i in matchData:
        try:
            for player in i:
                if player['sumName'] == "Chaddam":
                    playerStats.append(player)
                    break
        except IndexError:
            break

    return render_template('matchHistory.html', gameData=gameData, playerStats=playerStats, zip=zip)

@app.route('/summonerSearch', methods=['POST'])
def summonerSearch():
    logging.info(f"Connection incoming from - {request.remote_addr} to /matchHistory")

    ingres = request.data.decode("utf8")
    print(f"ingres:{ingres}")
    print(f"ingres:{type(ingres)}")

    gameData = fetchFromDB(ingres, 20)
    
    #print(f"gameData:{gameData}")

    if len(gameData) < 1:
        print("Fetching new user data")
        mtrack(ingres, RIOTAPIKEY)
        gameData = fetchFromDB(ingres, 20)

    matchData = []
    for i in gameData:
        matchData.append(json.loads(i['matchdata']))
    #print(f"matchData:\n{matchData}")
    print(f"matchData:{len(matchData)}")

    playerStats = []
    # Loops through match data, gets player card data and 
    for i in matchData:
        try:
            for player in i:
                if player['sumName'] == ingres:
                    playerStats.append(player)
                    break
        except IndexError:
            break
        except Exception as e:
            print(e)

    print(f"playerStats:{len(playerStats)}")

    return jsonify({ 
        'gameData': gameData,
        'playerStats': playerStats
    })

    #return render_template('matchHistory.html', ingres=ingres, gameData=gameData, playerStats=playerStats, zip=zip)

@app.route('/getHistory', methods=['POST'])
def getHistory():
    print("\ngetHistory endpoint hit\n")
    ingres = request.data.decode("utf8")
    print(f"INGRES IS THIS {ingres}")

    mtrack(ingres, RIOTAPIKEY)
    gameData = fetchFromDB(ingres, 20)

    if len(gameData) < 1:
        print("Fetching new user data")
        mtrack(ingres, RIOTAPIKEY)
        gameData = fetchFromDB(ingres, 20)

    matchData = []
    for i in gameData:
        matchData.append(json.loads(i['matchdata']))
    #print(f"matchData:\n{matchData}")
    print(f"matchData:{len(matchData)}")

    playerStats = []
    # Loops through match data, gets player card data and 
    for i in matchData:
        try:
            for player in i:
                if player['sumName'] == ingres:
                    playerStats.append(player)
                    break
        except IndexError:
            break
        except Exception as e:
            print(e)

    print(f"playerStats:{len(playerStats)}")

    return jsonify({ 
        'gameData': gameData,
        'playerStats': playerStats
    })
    #return jsonify({"message": "Updated"})


# Run Server
if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=80)
    except KeyboardInterrupt:
        sys.exit(0)