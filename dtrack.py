import logging
import requests
import datetime
import time

# Small class that is used to simplify adding color to the console output
# Example: print(bcolors.OKCYAN + f"{banked:.2f} days until decay..." + bcolors.ENDC)
# You need to add the beginning part and the end part cause what python wants python gets
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# THE CHONKY BOIIIIIIIIIIIIIIIIIIII
def dtrack(ans, mykey):

    logging.info(f"dtrack function started, scanning for decay on account {ans}")

    # Sets API key variable
    APIKEY = mykey
    # Searches theough 4 matches to determine decay since the MAX you can have banked is 4 matches played immediately after one another to a cap of 28 days so no point searching past 4 matches
    matchCount = 4

    logging.info(f"Querying ... https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ans.replace(' ','%20')}?api_key=<APIKEY>")
    # Gets PUUID from Summoner Name
    sumByName = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{ans.replace(' ','%20')}?api_key={APIKEY}").json()

    logging.info(f"Querying ... https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{sumByName['puuid']}/ids?queue=420&start=0&count={matchCount}&api_key=<APIKEY>")
    # Converts response to JSON
    matches = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{sumByName['puuid']}/ids?queue=420&start=0&count={matchCount}&api_key={APIKEY}")


    print(f"Player User ID: \t\t{sumByName['puuid']}")
    print(f"Player Summoner ID {sumByName['id']}")

    logging.info(f"Querying ... https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{sumByName['id']}?api_key=<APIKEY>")
    # Request to get full payload containing player rank
    summonerRankData = requests.get(f"https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{sumByName['id']}?api_key={APIKEY}").json()

    # Catches unexpected output from the riot api for players who dont have sufficient ranked data causing the return to be []
    try:
        # Sifting through the output from the ranked data dump
        # FOR SOME REASON RIOT RETURNS THIS AS A LIST WITH 1 ENTITY IN IT WHICH IS THE DICTIONARY RATHER THAN JUST A DICTIONARY
        summonerRank = summonerRankData[0]
        summonerRank = summonerRank['tier']
        print(f"\nCurrent Rank: \t\t\t{summonerRank}")

        # Checks the rank of the player and if they are below DIAMOND then the player can not decay so it returns a relevant response and stops the function early to not waste time
        if summonerRank not in ["DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]:
            #print(f"\n{ans} can not decay(too shit to decay)")
            print(bcolors.FAIL + "Rank too low to decay" + bcolors.ENDC)
            logging.info(f"Returning ... {ans} can not decay(too shit to decay)")
            return f"{ans} can not decay(too shit to decay)"
        print("Fetching Ranked data...")
    except:
        print(bcolors.FAIL + f"{ans} has insufficient ranked information at the moment" + bcolors.ENDC)
        logging.info(f"Returning ... {ans} has insufficient ranked information at the moment")
        return f"{ans} has insufficient ranked information at the moment"
    
    
    # Gets return as a json/list, Splits it into list of dictionaries
    sepList = str(matches.json()).split(",")
    matchList = []      # Appends to a new list with proper formatting
    for i in sepList:   # Cuts random useless characters in match list
        matchList.append(i.replace(" ","").replace("'", "").replace("[", "").replace("]", ""))
    matchData = []
    
    
    for i in matchList:
        #print(f"Game ID: \t\t\t{i}")
        matchData.append(requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/{i}?api_key={APIKEY}").json())
    
    # Sets times and diffs variables
    times = []
    diffs = []

    # Loops through match data and grabs the game creation times and appends them to the times list
    for i in matchData:
        gameDate = i['info']['gameCreation']
        times.append(gameDate)

    # Prints Game IDs that are getting scanned
    print("")
    for i in matchList:
        print(f"Game ID: \t\t\t{i}")

    # Gets the current time in unix epoch time
    ms = datetime.datetime.now()
    times.append(int(time.mktime(ms.timetuple()) * 1000))

    times.sort(reverse=True)
    # Calculates time differences and appends them to diffs
    for index, i in enumerate(times):
        try:
            diffs.append(times[index] - times[index + 1])
        except IndexError:
            continue

    #print(f"Diffs: {diffs}")
    print("")
    for i in diffs: print(f"Game Time differentials: \t{i}")

    banked = 0
    hoursdiff = []

    # Diffs conversion
    for i in diffs:
        # 3600 seconds in an hour and 3600000 is milliseconds in an hour. Multiplying it by 24 divides unix epoch timestamp in milliseconds by milliseconds in the day
        # Basically converts the millisecond epoch times into days to a decimal
        hoursdiff.append(i/(3600000 * 24)) 
    
    # Main function to determine how many days the player has banked
    for i in hoursdiff:
        newTime =  7 - i
        banked = banked + newTime
        if banked < 0: banked = 0
        if banked > 28: banked = 28
    
    # Rounds output to 2 digits past 0
    banked = round(banked, 2)
    banked = banked

    print(f"\nBanked: {banked}")

    if banked == 0.0:
        print("PLAY MORE GAMES")
        logging.info(f"Return ... Execution ended for {ans}, play more games")
        return "PLAY GAME NOW BITCH (stream that shit)"
    else:
        print(bcolors.OKCYAN + f"{banked:.2f} days until decay..." + bcolors.ENDC)
        logging.info(f"Return ... {ans} has {banked:.2f} days until decay...")
        return f"{ans} has {banked:.2f} days until decay..."