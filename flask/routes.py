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

# TODO: Need to fix this shit
@app.route('/', methods=['GET'])
def homePage():
    logging.info(f"Connection incoming from - {request.remote_addr} to Homepage")
    return render_template('mtrack.html')


# Actual webpage for the match history of a person
@app.route('/matchHistory', methods=['GET'])
def matchHistory():
    logging.info(f"Connection incoming from - {request.remote_addr} to /matchHistory")
    return render_template('matchHistory.html')


# TODO: Look for cleanup
@app.route('/summonerSearch', methods=['POST'])
def summonerSearch():
    logging.info(f"Connection incoming from - {request.remote_addr} to /matchHistory")

    ingres = request.data.decode("utf8")

    print(f"\nSummonerSearch endpoint hit \nSummoner: {ingres}\n")
    gameData = fetchFromDB(ingres, 20)

    if len(gameData) < 1:
        print("Fetching new user data")
        mtrack(ingres, RIOTAPIKEY)
        gameData = fetchFromDB(ingres, 20)

    matchData = []
    for i in gameData:
        matchData.append(json.loads(i['matchdata']))

    playerStats = []
    # Loops through match data, gets player card data and 
    for i in matchData:
        try:
            for player in i:
                lowerName = player['sumName'].lower()
                #print(f"{player['sumName']} == {ingres} == {lowerName}")
                if lowerName == ingres.lower():
                    playerStats.append(player)
                    break
        except IndexError:
            break
        except Exception as e:
            print(e)
    
    #print(matchData)

    return jsonify({ 
        'gameData': gameData,
        'playerStats': playerStats,
        'matchData': matchData
    })


@app.route('/getHistory', methods=['POST'])
def getHistory():
    print("\ngetHistory endpoint hit\n")
    ingres = request.data.decode("utf8")

    mtrack(ingres, RIOTAPIKEY)
    gameData = fetchFromDB(ingres, 20)
    
    if len(gameData) < 1:
        print("Fetching new user data")
        mtrack(ingres, RIOTAPIKEY)
        gameData = fetchFromDB(ingres, 20)

    matchData = []
    for i in gameData:
        matchData.append(json.loads(i['matchdata']))

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

    return jsonify({ 
        'gameData': gameData,
        'playerStats': playerStats,
        'matchData': matchData
    })



# Get champ icons
@app.route('/getIcon', methods=['POST'])
def getIcon():
    ingres = request.data.decode("utf8")

    print(f"\getIcon endpoint hit \nSummoner: {ingres}\n")

    # Specify the path to the folder containing PNGs
    icons_folder = './static/img/champIcons'

    # Check if the file with the given name exists
    file_path = os.path.join(icons_folder, f'{name}.png')
    if os.path.exists(file_path):
        # Return the PNG file as a response
        return send_file(file_path, mimetype='image/png')
    else:
        # If the file doesn't exist, return an error response
        return "File not found", 404




# Run Server
if __name__ == '__main__':
    try:
        os.system("clear")

        print("Starting Flask app 'routes.py'")
        print(f"Running app at - {config['SITE']['address']}:{config['SITE']['port']}")

        app.run(debug=True, host=config['SITE']['address'], port=config['SITE']['port'])

    except KeyboardInterrupt:
        sys.exit(0)