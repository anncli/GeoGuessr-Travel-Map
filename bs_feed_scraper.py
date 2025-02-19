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

if __name__ == "__main__":
    load_dotenv()

    feed_data_url = "https://www.geoguessr.com/api/v4/feed/private"

    # parse rounds data from game data
    feed_data = scrape_feed_data(feed_data_url)

    # write rounds data to file
    games_list_file = open("games_list.json", 'w')
    json.dump(feed_data, games_list_file)