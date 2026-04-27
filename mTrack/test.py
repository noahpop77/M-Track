import requests

ranked_info_response = requests.get(f"https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/5UyxKlJgSVTscUIoG7SSK3113Idik9TjRLEczegM3dH-v6WI48w4lTY_gwh2rLh_VoTpYDvbQYAyTA?api_key=RGAPI-29942555-30d4-40a8-ad7d-c9b60103cbd6")
ranked_info_response.raise_for_status()  # Raise exception for HTTP errors
rankedInfo = ranked_info_response.json()

print(rankedInfo, flush=True)
print(ranked_info_response, flush=True)