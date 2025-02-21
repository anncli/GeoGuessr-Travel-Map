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
    rounds_data = []
    with open("game_tokens_list.json", "r") as game_tokens_file:
        game_tokens_list = json.load(game_tokens_file)
        for game in game_tokens_list:
            game_token = game
            game_data_url = url_base + game_token

            # parse rounds data from game data
            game_data = scrape_game_data(game_data_url)
            rounds_data.extend(game_data["rounds"])

    # write rounds data to file
    with open("game_rounds.json", 'w') as game_rounds_file:
        json.dump(rounds_data, game_rounds_file)