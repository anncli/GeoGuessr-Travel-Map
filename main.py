import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

from geoguessr_api import feed_scraper, game_scraper
import google_maps_api
import geoguessr_db

def main():
    PROFILE_FEED_URL = "https://www.geoguessr.com/api/v4/feed/private"

    geoguessr_db.init_db()   # Initialize DB file

    # 1) Fetch Profile Feed
    print("Fetching feed...")
    feed_data = feed_scraper.fetch_feed_data(PROFILE_FEED_URL)
    if not feed_data:
        print("No feed data, exiting.")
        return

    # 2) Extract Tokens
    print("Extracting game tokens...")
    classic_entries, duel_entries, classic_tokens, duel_tokens = (
        feed_scraper.extract_game_tokens_list(feed_data, check_timestamp=False)
    )

    # prepare headers
    cookie = os.getenv("BROWSER_COOKIE")
    headers = {"User-Agent": "Mozilla/5.0"}
    if cookie:
        headers["Cookie"] = cookie
    else:
        print("Warning: BROWSER_COOKIE not set; some endpoints may require auth.")

    # 3) Fetch & Save New Game Data to DB
    print(f"Processing {len(classic_tokens)} classic tokens...")
    for token in classic_tokens:
        existing_game_id = geoguessr_db.get_game_id_by_token(token)
        if existing_game_id and geoguessr_db.has_rounds_for_game(existing_game_id):
            continue

        print(f"Fetching classic game {token}...")
        game = game_scraper.fetch_classic_game(token, headers)
        if game:
            game_id = geoguessr_db.save_game("classic", token, game)
            # only save rounds if DB doesn't already have them
            if not geoguessr_db.has_rounds_for_game(game_id):
                rounds = game.get("rounds", [])
                geoguessr_db.save_rounds(game_id, rounds)

    print(f"Processing {len(duel_tokens)} duel tokens...")
    for duel_id in duel_tokens:
        existing_game_id = geoguessr_db.get_game_id_by_token(duel_id)
        if existing_game_id and geoguessr_db.has_rounds_for_game(existing_game_id):
            continue

        print(f"Fetching duel game {duel_id}...")
        duel = game_scraper.fetch_duel_game(duel_id, headers)
        if duel:
            game_id = geoguessr_db.save_game("duel", duel_id, duel)
            if not geoguessr_db.has_rounds_for_game(game_id):
                rounds = duel.get("rounds", [])
                geoguessr_db.save_rounds(game_id, rounds)

    # 4) Call Google Maps API to Reverse Geocode Ungeocoded Rounds
    print("Geocoding ungeocoded rounds...")
    to_process = geoguessr_db.get_ungeocoded_rounds(limit=2000)
    for rid, lat, lng in to_process:
        city = google_maps_api.get_city_name(lat, lng)
        geoguessr_db.update_round_city(rid, city)

    # 5) Export CSV and Launch Visualization
    geoguessr_db.export_rounds_to_csv(os.path.join("visualization", "data_points.csv"))
    visualization_dir = os.path.join(os.path.dirname(__file__), "visualization")
    print("Launching visualization...")
    subprocess.run([sys.executable, "plotly-map.py"], cwd=visualization_dir, check=False)

if __name__ == "__main__":
    main()
