from flask import Flask, render_template, request
import os
import sys
import csv
import logging
import requests
from configparser import ConfigParser

# Config file initiators for use in getting API key from config.ini
# in the sanity check for the /addSummoner API endpoint
file = "../config.ini"
config = ConfigParser()
config.read(file)
RIOTAPIKEY = config['KEYS']['riotapi']

# init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", filename="routes.log")
logging.info("STARTED - ROUTES.PY")

# Example test route that when it gets a GET request for the root of the web page it will return a jsonified response in the format of a python dictionary
@app.route('/getSummoners', methods=['GET'])
def summoners():
    # Catches if there is no summoners.csv file
    # If there is none then it returns a message rather than a CSV
    logging.info(f"REQUEST - /getSummoners request received...")
    try:
        infile = open("summoners.csv", "r")
        indata = csv.reader(infile, delimiter=",")
        # Flatens the data (for soem reason the list being pulled from the CSV is a nested list)
        inlist = sum(indata, [])
        outstring = ""
        for i in inlist: outstring = outstring + i + ","
        outstring = outstring[:-1]
        logging.info(f"REQUEST - /getSummoners request returned!")
        return outstring
    except FileNotFoundError:
        logging.error(f"ERROR - There are no summoners being tracked!")
        return "THERE ARE NO SUMMONERS BEING TRACKED"


@app.route('/removeSummoner', methods=['POST', 'GET'])
def removeSummoner():
    logging.info(f"REQUEST - /removeSummoners request received...")
    # Data sent to api decoded and ready to use as a string
    ingres = request.args.get('name')
    
    try:
        infile = open("summoners.csv", "r")
    except FileNotFoundError:
        logging.error(f"ERROR - summoners.csv does not exist!")
        return "There are currently no summoner names being tracked"

    # Reads CSV data, comma delitits it, Flatens the data (for some reason the list being pulled from the CSV is a nested list
    indata = csv.reader(infile, delimiter=",")
    inlist = sum(indata, [])
    
    try:
        # Edits the list by removing the name in the request
        inlist.remove(ingres)

        # File handler for appending to summoner list
        outfile = open("summoners.csv", "w")
        outstring = ""
        for i in inlist: 
            outstring = outstring + i + ","
        outstring = outstring[:-1]
        outfile.write(f"{outstring}")

        # Closing file handlers for in and out
        outfile.close()
        infile.close()

        logging.info(f"REQUEST - /removeSummoner request returned!")
        return inlist
    except:
        return f"{ingres} was not found"


@app.route('/addSummoner', methods=['POST', 'GET'])
def addSummoner():
    logging.info(f"REQUEST - /addSummoner request received for {request.args.get('name')}...")

    # Data sent to api decoded and ready to use as a string
    #ingres = request.args.get('name')
    ingres = request.data.decode("utf8")
    print(request.data.decode("utf8"))

    # Does a sanity check to see if the user exists before it adds it to the summoners.csv file
    sumByName = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ingres.replace(' ','%20')}?api_key={RIOTAPIKEY}").status_code
    if sumByName != 200:
        logging.info(f"ERROR - /addSummoner request received for {request.args.get('name')} was not processed. USER DOES NOT EXIST...")
        return "This summoner does not exist. Nothing will be added."

    # File handling for file containing summoners
    try:
        infile = open("summoners.csv", "r")
    except FileNotFoundError:
        infile = open("summoners.csv", "w")
        infile.write(ingres)
        return ingres

    indata = csv.reader(infile, delimiter=",")
    # Flatens the data (for soem reason the list being pulled from the CSV is a nested list)
    inlist = sum(indata, [])
    
    # File handler for appending to summoner list
    outfile = open("summoners.csv", "a")
    # If the ingres name is not already being tracked it will append the name to the summoners.csv
    if ingres not in inlist:
        inlist.append(ingres) # Append after check to see if ingres name is unique in list
        print(inlist)
        outfile.write(f",{ingres}")

    # Closing file handlers for in and out
    outfile.close()
    infile.close()

    # RETURN DATA FOR REQUEST (sent to user)
    logging.info(f"REQUEST - /addSummoner request returned...")
    return inlist


@app.route('/', methods=['GET'])
def home():
    # the default for render_template looks inside of the templates directory on the same level as this file which starts the server
    try:
        infile = open("summoners.csv", "r")
        indata = csv.reader(infile, delimiter=",")
        # Flatens the data (for soem reason the list being pulled from the CSV is a nested list)
        inlist = sum(indata, [])
        return render_template('index.html', value=inlist)
    except FileNotFoundError:
        return "THERE ARE NO SUMMONERS BEING TRACKED"
     

# Run Server
if __name__ == '__main__':
    try:
        app.run(debug=True, host='10.0.0.150', port=5000)
    except KeyboardInterrupt:
        sys.exit(0)