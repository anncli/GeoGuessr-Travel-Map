import requests
from bs4 import BeautifulSoup
import json

def scrape_game_data(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    soup_str = str(soup)
    game_data = json.loads(soup_str)
    return game_data

if __name__ == "__main__":
    url_base = "https://www.geoguessr.com/api/v3/games/"
    game_token = "EahFhgl0fFz7HGW7/"
    game_data_url = url_base + game_token

    # parse rounds data from game data
    game_data = scrape_game_data(game_data_url)
    rounds_data = game_data["rounds"]

    # write rounds data to file
    with open("game_rounds.json", 'w') as game_rounds_file:
        json.dump(rounds_data, game_rounds_file)