import os
import json
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

from geoguessr_api import feed_scraper, game_scraper
import google_maps_api

def main():
    feed_url = "https://www.geoguessr.com/api/v4/feed/private"

    # 1) fetch feed
    print("Fetching feed...")
    feed_data = feed_scraper.fetch_feed_data(feed_url)
    if not feed_data:
        print("No feed data, exiting.")
        return

    # 2) extract tokens (separates classic and duel)
    print("Extracting game tokens...")
    classic_entries, duel_entries, classic_tokens, duel_tokens = (
        feed_scraper.extract_game_tokens_list(feed_data, check_timestamp=False)
    )

    # save token lists
    with open("classic_game_tokens.json", "w") as f:
        json.dump(classic_tokens, f, indent=2)
    with open("duel_game_tokens.json", "w") as f:
        json.dump(duel_tokens, f, indent=2)

    # prepare headers
    cookie = os.getenv("BROWSER_COOKIE")
    headers = {"User-Agent": "Mozilla/5.0"}
    if cookie:
        headers["Cookie"] = cookie
    else:
        print("Warning: BROWSER_COOKIE not set; some endpoints may require auth.")

    # 3) fetch game data
    print(f"Fetching {len(classic_tokens)} classic games...")
    classic_games = []
    for token in classic_tokens:
        g = game_scraper.fetch_classic_game(token, headers)
        if g:
            classic_games.append(g)

    print(f"Fetching {len(duel_tokens)} duel games...")
    duel_games = []
    for gid in duel_tokens:
        g = game_scraper.fetch_duel_game(gid, headers)
        if g:
            duel_games.append(g)

    # save fetched game data
    with open("classic_games_data.json", "w") as f:
        json.dump(classic_games, f, indent=2)
    with open("duel_games_data.json", "w") as f:
        json.dump(duel_games, f, indent=2)

    # 4) add city names to round data (in-place)
    print("Adding city names to classic games...")
    google_maps_api.add_city_to_data("classic_games_data.json")
    print("Adding city names to duel games...")
    google_maps_api.add_city_to_data("duel_games_data.json")

    # 5) run the visualization script from its folder (so relative paths resolve)
    visualization_dir = os.path.join(os.path.dirname(__file__), "visualization")
    print("Launching visualization...")
    subprocess.run([sys.executable, "plotly-map.py"], cwd=visualization_dir, check=False)

if __name__ == "__main__":
    main()
