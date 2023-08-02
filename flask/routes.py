from flask import Flask, render_template, request
import os
import sys
import logging
from configparser import ConfigParser
from dtrack import *

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
    return render_template('index.html')
@app.route('/dtrack', methods=['GET'])
def dtrackPage():
    logging.info(f"Connection incoming from - {request.remote_addr} to /dtrack")
    return render_template('dtrack.html')

# Run Server
if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=80)
    except KeyboardInterrupt:
        sys.exit(0)