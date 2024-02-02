import mysql.connector
from configparser import ConfigParser

# Config file initiators for use in getting API key from config.ini
# in the sanity check for the /addSummoner API endpoint
file = "../config.ini"
config = ConfigParser()
config.read(file)

host = config['DATABASE']['host']
user = config['DATABASE']['user']
password = config['DATABASE']['password']
database = config['DATABASE']['database']


# Rather than always running an extra 2 Riot API requests if we pre store some of the previously searched riotIDs we can save execution time.
def fetchGameIDsFromDB(summonerName):
    try:
        # Establish a connection to the MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            #print(f"Query made to MySQL Server: {host} | Database: {database}")

            # Create a cursor object to interact with the database
            cursor = connection.cursor(dictionary=True)  # Set dictionary=True to fetch rows as dictionaries

            # Execute the SQL query to retrieve the last 20 rows from matchHistory
            
            query = (
                "SELECT "
                "gameID "
                "FROM matchHistory "
                f"WHERE userSummoner = '{summonerName}'"

            )

            # Runs query
            cursor.execute(query)

            # Fetch the results as a list of dictionaries
            querylistOfDict = cursor.fetchall()
            #queryListOfValues = [row[0] for row in cursor.fetchall()]
            gameIDList = []
            for i in querylistOfDict:
                gameIDList.append(i['gameID'])

            # Return the retrieved data
            return gameIDList

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL Server: {e}")

    finally:
        # Close the cursor and connection when done
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()



def fetchFromRiotIDDB(riotID):
    try:
        # Establish a connection to the MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            #print(f"Query made to MySQL Server: {host} | Database: {database}")

            # Create a cursor object to interact with the database
            cursor = connection.cursor(dictionary=True)  # Set dictionary=True to fetch rows as dictionaries

            # Execute the SQL query to retrieve the last 20 rows from matchHistory
            query = (
                "SELECT "
                "summonerName, puuid "
                "FROM riotIDData "
                f"WHERE riotID = '{riotID}'"
            )

            # Runs query
            cursor.execute(query)

            # Fetch the results as a list of dictionaries
            riotIDDictionary = cursor.fetchone()

            # Check if the result is None, indicating no rows were found
            if riotIDDictionary is None:
                return None

            # Return the retrieved data
            return riotIDDictionary['summonerName'], riotIDDictionary['puuid']

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL Server: {e}")

    finally:
        # Close the cursor and connection when done
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()








def fetchFromMatchHistoryDB(summonerName, numberOfRecords, recordOffset = 0):

    try:
        # Establish a connection to the MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            #print(f"Query made to MySQL Server: {host} | Database: {database}")

            # Create a cursor object to interact with the database
            cursor = connection.cursor(dictionary=True)  # Set dictionary=True to fetch rows as dictionaries

            # Execute the SQL query to retrieve the last 20 rows from matchHistory
            
            query = (
                "SELECT "
                "gameID, gameVer, gameDurationMinutes, gameCreationTimestamp, gameEndTimestamp, gameDate, "
                "JSON_UNQUOTE(participants) as participants, "
                "JSON_UNQUOTE(matchdata) as matchdata "
                "FROM matchHistory "
                f"WHERE userSummoner = '{summonerName}'"
                f"ORDER BY gameID DESC LIMIT {recordOffset}, {numberOfRecords}"
            )

            # Runs query
            cursor.execute(query)

            # Fetch the results as a list of dictionaries
            querylistOfDict = cursor.fetchall()

            # Return the retrieved data
            return querylistOfDict

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL Server: {e}")

    finally:
        # Close the cursor and connection when done
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    