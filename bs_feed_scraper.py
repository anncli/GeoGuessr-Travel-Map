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

def extract_game_tokens_list(entries):
    account_data = entries["entries"]

    # get session payloads list in stringified form
    session_payloads_stringified = [entry["payload"] for entry in account_data]
    session_payloads_json = []
    for entry in session_payloads_stringified:
        session_payloads_json.extend(json.loads(entry))

    game_payloads = [entry["payload"] for entry in session_payloads_json if "payload" in entry]
    game_tokens = [entry["gameToken"] for entry in game_payloads if "gameToken" in entry]
    return session_payloads_json, game_tokens

if __name__ == "__main__":
    load_dotenv()

    feed_data_url = "https://www.geoguessr.com/api/v4/feed/private"

    # parse rounds data from game data
    feed_data = scrape_feed_data(feed_data_url)
    payloads_list, game_tokens = extract_game_tokens_list(feed_data)
    print(game_tokens)

    # write rounds data to file
    games_list_file = open("games_list.json", 'w')
    json.dump(payloads_list, games_list_file)