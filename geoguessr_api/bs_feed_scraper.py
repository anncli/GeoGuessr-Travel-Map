from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import json

def scrape_feed_data(url):
    cookie = os.getenv("BROWSER_COOKIE")
    if cookie is None:
        print("Error: BROWSER_COOKIE not found in environment variables.")
        exit()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie
    }
    page = requests.get(url, headers=headers)

    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "html.parser")
        soup_str = str(soup)
        feed_data = json.loads(soup_str)
        return feed_data
    else:
        print(f"Failed to retrieve the page. Status code: {page.status_code}")

def extract_game_tokens_list(entries, check_timestamp=False):
    account_data = entries["entries"]

    '''
    type 1 - single player game (classic)
    type 6 - multiplayer game (duel)
    type 7 - contains a list of classic games played in the same session
    '''
    game_entries = []
    for session in account_data:
        if session["type"] == 1: # classic game
            # If payload is a string, parse it into a dictionary
            if isinstance(session["payload"], str):
                session["payload"] = json.loads(session["payload"])
            game_entries.append(session)
        elif session["type"] == 7: # set of games
            if "payload" in session:
                game_payloads = json.loads(session["payload"])  # convert string to list
                for game in game_payloads:
                    if game["type"] == 1:
                        game_entries.append(game)
    
    # extract gameTokens from game_entries
    game_tokens = []
    for game in game_entries:
        if check_timestamp:
            # TODO: stop appending once we reached previously loaded games
            continue
        game_tokens.append(game["payload"]["gameToken"])

    return game_entries, game_tokens


if __name__ == "__main__":
    load_dotenv()

    feed_data_url = "https://www.geoguessr.com/api/v4/feed/private"

    # parse rounds data from game data
    feed_data = scrape_feed_data(feed_data_url)
    game_entries, game_tokens_list = extract_game_tokens_list(feed_data, check_timestamp=False)

    # write rounds data to file
    with open("games_list.json", 'w') as games_list_file:
        json.dump(game_entries, games_list_file)
    with open("game_tokens_list.json", 'w') as game_tokens_file:
        json.dump(game_tokens_list, game_tokens_file)