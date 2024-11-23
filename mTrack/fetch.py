import psycopg2
from psycopg2 import sql
from configparser import ConfigParser
import os

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
            "SELECT gameID FROM matchHistory WHERE riotID = %s"
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
            "SELECT puuid FROM riotIDData WHERE riotID = %s"
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
            "SELECT gameID, gameVer, gameDurationMinutes, gameCreationTimestamp, gameEndTimestamp, gameDate, "
            "participants, matchdata FROM matchHistory WHERE riotID = %s ORDER BY gameID DESC LIMIT %s OFFSET %s"
        )

        cursor.execute(query, (riotID, numberOfRecords, recordOffset))

        # Fetch the results
        querylistOfDict = cursor.fetchall()

        # Return the retrieved data
        return querylistOfDict

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL Server: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()


def fetchFromSummonerRankedInfoDB(puuid):
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
            "SELECT * FROM summonerRankedInfo WHERE encryptedPUUID = %s"
        )

        cursor.execute(query, (puuid,))

        # Fetch the results
        rankedInfoDict = cursor.fetchall()

        # Check if the result is None
        if not rankedInfoDict:
            return None

        # Return the retrieved data
        return rankedInfoDict

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL Server: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
