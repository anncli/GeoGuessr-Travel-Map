import os
import requests
import json
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_city_name(lat, lng):
    """
    Use Google Geocoding API. On any error or non-OK status return empty string.
    """
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not google_maps_api_key:
        print("GOOGLE_MAPS_API_KEY not set; skipping reverse geocode")
        return ""

    params = {"latlng": f"{lat},{lng}", "key": google_maps_api_key}
    try:
        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params=params,
            timeout=10,
        )
    except Exception as e:
        print(f"Reverse geocode request failed for {lat},{lng}: {e}")
        return ""

    if response.status_code != 200:
        print(f"Geocode HTTP {response.status_code} for {lat},{lng}")
        return ""

    reverse_geocode_data = response.json()
    status = reverse_geocode_data.get("status")
    if status != "OK":
        print(f"Geocode API status {status} for {lat},{lng} - saving response to geocode_debug.json")
        with open("geocode_debug.json", "a") as fh:
            fh.write(json.dumps({"lat": lat, "lng": lng, "status": status, "response": reverse_geocode_data}) + "\n")
        return ""

    # Prefer locality / postal_town from address_components
    for result in reverse_geocode_data.get("results", []):
        for comp in result.get("address_components", []):
            types = comp.get("types", [])
            if "locality" in types or "postal_town" in types:
                return comp.get("long_name", "")

    # Fallback to admin areas then formatted_address
    for preferred in ("administrative_area_level_2", "administrative_area_level_1", "country"):
        for result in reverse_geocode_data.get("results", []):
            for comp in result.get("address_components", []):
                if preferred in comp.get("types", []):
                    return comp.get("long_name", "")

    first = reverse_geocode_data.get("results", [None])[0]
    if first and "formatted_address" in first:
        return first["formatted_address"]

    # nothing found — log and return empty
    with open("geocode_debug.json", "a") as fh:
        fh.write(json.dumps({"lat": lat, "lng": lng, "response": reverse_geocode_data}) + "\n")
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