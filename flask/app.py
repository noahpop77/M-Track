from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import sys
import json
from datetime import timedelta
import csv

# init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


# Example test route that when it gets a GET request for the root of the web page it will return a jsonified response in the format of a python dictionary
@app.route('/getsummoners', methods=['GET'])
def summoners():
    # Catches if there is no summoners.csv file
    # If there is none then it returns a message rather than a CSV
    try:
        infile = open("summoners.csv", "r")
        indata = csv.reader(infile, delimiter=",")
        # Flatens the data (for soem reason the list being pulled from the CSV is a nested list)
        inlist = sum(indata, [])
        outstring = ""
        for i in inlist: outstring = outstring + i + ","
        outstring = outstring[:-1]
        return outstring
    except FileNotFoundError:
        return "THERE ARE NO SUMMONERS BEING TRACKED"



@app.route('/addSummoner', methods=['POST', 'GET'])
def addSummoner():
    # Data sent to api decoded and ready to use as a string
    ingres = request.data.decode('utf8')
    
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
        print(ingres)
        #for i in inlist:
        outfile.write(f",{ingres}")

    # Closing file handlers for in and out
    outfile.close()
    infile.close()

    # RETURN DATA FOR REQUEST (sent to user)
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
        #json_file.close()
        sys.exit(0)