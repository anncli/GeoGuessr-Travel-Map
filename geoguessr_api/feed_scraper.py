from dotenv import load_dotenv
import os
import requests
import json

def fetch_feed_data(url):
    cookie = os.getenv("BROWSER_COOKIE")
    if cookie is None:
        print("Error: BROWSER_COOKIE not found in environment variables.")
        exit(1)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve the feed. Status code: {response.status_code}")
        exit()

def extract_game_tokens_list(entries, check_timestamp=False):
    account_data = entries["entries"]

    '''
    type 1 - single player game (classic)
    type 6 - multiplayer game (duel)
    type 7 - contains a list of games played in the same session (can be type 1 or 6)
    '''
    classic_game_entries = []
    duel_game_entries = []
    classic_game_tokens = []
    duel_game_tokens = []

    for session in account_data:
        # Classic game
        if session["type"] == 1:
            if isinstance(session["payload"], str):
                session["payload"] = json.loads(session["payload"])
            classic_game_entries.append(session)
            payload = session["payload"]
            if isinstance(payload, str):
                payload = json.loads(payload)
            if "gameToken" in payload:
                classic_game_tokens.append(payload["gameToken"])
        # Duel game
        elif session["type"] == 6:
            if isinstance(session["payload"], str):
                session["payload"] = json.loads(session["payload"])
            duel_game_entries.append(session)
            payload = session["payload"]
            if isinstance(payload, str):
                payload = json.loads(payload)
            if "gameId" in payload:
                duel_game_tokens.append(payload["gameId"])
        # Set of games (could be classic or duel)
        elif session["type"] == 7 and "payload" in session:
            game_payloads = json.loads(session["payload"])
            for game in game_payloads:
                if game["type"] == 1:
                    classic_game_entries.append(game)
                    payload = game["payload"]
                    if isinstance(payload, str):
                        payload = json.loads(payload)
                    if "gameToken" in payload:
                        classic_game_tokens.append(payload["gameToken"])
                elif game["type"] == 6:
                    duel_game_entries.append(game)
                    payload = game["payload"]
                    if isinstance(payload, str):
                        payload = json.loads(payload)
                    if "gameId" in payload:
                        duel_game_tokens.append(payload["gameId"])

    return classic_game_entries, duel_game_entries, classic_game_tokens, duel_game_tokens

if __name__ == "__main__":
    load_dotenv()

    feed_data_url = "https://www.geoguessr.com/api/v4/feed/private"

    # fetch rounds data from game data
    feed_data = fetch_feed_data(feed_data_url)
    classic_entries, duel_entries, classic_tokens, duel_tokens = extract_game_tokens_list(feed_data, check_timestamp=False)

    # write rounds data to file
    with open("classic_games_list.json", 'w') as f:
        json.dump(classic_entries, f)
    with open("duel_games_list.json", 'w') as f:
        json.dump(duel_entries, f)
    with open("classic_game_tokens.json", 'w') as f:
        json.dump(classic_tokens, f)
    with open("duel_game_tokens.json", 'w') as f:
        json.dump(duel_tokens, f)