import os
import json
import requests
from dotenv import load_dotenv

def fetch_classic_game(game_token, headers):
    url = f"https://www.geoguessr.com/api/v3/games/{game_token}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch classic game {game_token}: {response.status_code}")
        return None

def fetch_duel_game(game_id, headers):
    url = f"https://game-server.geoguessr.com/api/duels/{game_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch duel game {game_id}: {response.status_code}")
        return None

if __name__ == "__main__":
    load_dotenv()
    cookie = os.getenv("BROWSER_COOKIE")
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie
    }

    # Load tokens
    with open("classic_game_tokens.json") as f:
        classic_tokens = json.load(f)
    with open("duel_game_tokens.json") as f:
        duel_tokens = json.load(f)

    # Fetch classic games
    classic_games_data = []
    for token in classic_tokens:
        data = fetch_classic_game(token, headers)
        if data:
            classic_games_data.append(data)

    # Fetch duel games
    duel_games_data = []
    for game_id in duel_tokens:
        data = fetch_duel_game(game_id, headers)
        if data:
            duel_games_data.append(data)

    # Save results
    with open("classic_games_data.json", "w") as f:
        json.dump(classic_games_data, f)
    with open("duel_games_data.json", "w") as f:
        json.dump(duel_games_data, f)