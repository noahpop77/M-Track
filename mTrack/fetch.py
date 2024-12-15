import psycopg2
from psycopg2 import sql
from configparser import ConfigParser
import os
import json

# Config file initiators for use in getting API key from config.ini
file = "../config.ini"
config = ConfigParser()
config.read(file)

host = config['DATABASE']['host']
user = config['DATABASE']['user']
password = config['DATABASE']['password']
database = config['DATABASE']['database']


# Rather than always running an extra 2 Riot API requests if we pre-store some of the previously searched riotIDs we can save execution time.
def fetchGameIDsFromDB(riotID):
    connection = None  # Initialize connection as None
    try:
        # Establish a connection to the PostgreSQL server
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=database
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the SQL query to retrieve the last 20 rows from matchHistory
        query = sql.SQL(
            'SELECT "gameID" FROM "matchHistory" WHERE "riotID" = %s'
        )

        cursor.execute(query, (riotID,))

        # Fetch the results as a list of dictionaries
        querylistOfDict = cursor.fetchall()

        # Prepare the gameID list
        gameIDList = [i[0] for i in querylistOfDict]  # Extract the gameID from the tuple

        # Return the retrieved data
        return gameIDList

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL Server: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()


def fetchFromRiotIDDB(riotID):
    connection = None  # Initialize connection as None
    try:
        # Establish a connection to the PostgreSQL server
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=database
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the SQL query to retrieve the puuid
        query = sql.SQL(
            'SELECT "puuid" FROM "riotIDData" WHERE "riotID" = %s'
        )

        cursor.execute(query, (riotID,))

        # Fetch the result
        riotIDDictionary = cursor.fetchone()

        # Check if the result is None
        if riotIDDictionary is None:
            return None

        # Return the puuid value
        return riotIDDictionary[0]

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL Server: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()


import psycopg2
from psycopg2 import sql

def fetchFromMatchHistoryDB(riotID, numberOfRecords, recordOffset=0):
    connection = None  # Initialize connection as None
    try:
        # Establish a connection to the PostgreSQL server
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=database
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the SQL query to retrieve match history records
        query = sql.SQL(
            'SELECT "gameID", "gameVer", "gameDurationMinutes", "gameCreationTimestamp", "gameEndTimestamp", "gameDate", '
            '"participants", "matchData" FROM "matchHistory" WHERE "riotID" = %s ORDER BY "gameID" DESC LIMIT %s OFFSET %s'
        )

        cursor.execute(query, (riotID, numberOfRecords, recordOffset))

        # Fetch the results
        querylistOfTuples = cursor.fetchall()

        # Convert the result tuples to dictionaries
        querylistOfDict = []
        columns = [desc[0] for desc in cursor.description]  # Get column names

        for row in querylistOfTuples:
            row_dict = dict(zip(columns, row))  # Zip column names with values
            querylistOfDict.append(row_dict)

        # Return the retrieved data as a list of dictionaries
        return querylistOfDict

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL Server: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()



import psycopg2
from psycopg2 import sql

def fetchFromSummonerRankedInfoDB(puuid):
    connection = None  # Initialize connection as None
    try:
        # Establish a connection to the PostgreSQL server
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=database
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Execute the SQL query to retrieve summoner ranked info
        query = sql.SQL(
            'SELECT * FROM "summonerRankedInfo" WHERE "encryptedPUUID" = %s'
        )

        cursor.execute(query, (puuid,))

        # Fetch the results
        rankedInfoTuples = cursor.fetchall()
        # Check if the result is empty
        if not rankedInfoTuples:
            return None  # Or return an empty list, depending on your preference

        # Convert the result tuples to dictionaries
        columns = [desc[0] for desc in cursor.description]  # Get column names
        rankedInfoDict = [dict(zip(columns, row)) for row in rankedInfoTuples]

        # Return the retrieved data as a list of dictionaries
        return rankedInfoDict

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL Server: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()

