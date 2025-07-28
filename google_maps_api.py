import os
import requests
import json
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_city_name(lat, lng):
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    request_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={google_maps_api_key}"

    response = requests.get(request_url)
    if response.status_code == 200:
        # parse city name from response
        reverse_geocode_data = response.json()
        if "plus_code" in reverse_geocode_data and "compound_code" in reverse_geocode_data["plus_code"]:
            compound_code = reverse_geocode_data["plus_code"]["compound_code"]
            city = compound_code[compound_code.find(" ")+1:]
            return city
        elif "results" in reverse_geocode_data and len(reverse_geocode_data["results"]) > 0:
            for result in reverse_geocode_data["results"]:
                location_name = ""
                if "formatted_address" in result and '+' not in result["formatted_address"]:
                    location_name = result["formatted_address"]
                    return location_name
        
        # if no location name found that doesn't contain a geocode
        print(f"Location name not found for {lat}, {lng}")
        with open("reverse_geocode.json", "a") as file:
            json.dump(reverse_geocode_data, file)
        return ""
    else:
        print(f"Failed to fetch reverse geocode data for {lat}, {lng}:", response.status_code)
        return ""

def process_round(round):
    # Try classic format first
    if "lat" in round and "lng" in round:
        lat, lng = round["lat"], round["lng"]
    # Try duel format (nested in panorama)
    elif "panorama" in round and "lat" in round["panorama"] and "lng" in round["panorama"]:
        lat, lng = round["panorama"]["lat"], round["panorama"]["lng"]
    else:
        print(f"Skipping round (missing lat/lng): {round}")
        round["city"] = ""
        return round

    city = get_city_name(lat, lng)
    round["city"] = city
    return round

def extract_rounds_from_games(games_data):
    # Flatten all rounds from all games into a single list
    all_rounds = []
    for game in games_data:
        rounds = game.get("rounds", [])
        for rnd in rounds:
            all_rounds.append(rnd)
    return all_rounds

def add_city_to_data(game_data_file, max_threads=20):
    with open(game_data_file, "r") as file:
        data = json.load(file)

    # If the file is a list of games, flatten to rounds
    if isinstance(data, list) and data and "rounds" in data[0]:
        rounds_data = extract_rounds_from_games(data)
    else:
        rounds_data = data

    updated_data = []

    # multithread API requests
    with ThreadPoolExecutor(max_threads) as executor:
        future_to_round = {executor.submit(process_round, rnd): rnd for rnd in rounds_data}
        for future in as_completed(future_to_round):
            updated_data.append(future.result())

    # save updated JSON
    with open(game_data_file, "w") as file:
        json.dump(updated_data, file)


if __name__ == "__main__":
    load_dotenv()

    add_city_to_data("classic_games_data.json")
    add_city_to_data("duel_games_data.json")
    print("City names added to all game rounds data.")