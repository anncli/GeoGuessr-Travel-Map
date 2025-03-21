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
        else:
            print(f"Compound code not found for {lat}, {lng}")
            return ""
    else:
        print(f"Failed to fetch reverse geocode data for {lat}, {lng}:", response.status_code)
        return ""

def process_round(round):
    """Processes a single round entry by adding the city name."""
    city = get_city_name(round["lat"], round["lng"])
    round["city"] = city
    return round


def add_city_to_data(game_rounds_file, max_threads=20):
    with open(game_rounds_file, "r") as file:
        data = json.load(file)
    
    updated_data = []

    # Multithread API requests
    with ThreadPoolExecutor(max_threads) as executor:
        future_to_round = {executor.submit(process_round, round): round for round in data}
        
        for future in as_completed(future_to_round):
            updated_data.append(future.result())

    # Save updated JSON
    with open(game_rounds_file, "w") as file:
        json.dump(updated_data, file)


if __name__ == "__main__":
    load_dotenv()
    
    game_rounds_file = "game_rounds.json"
    add_city_to_data(game_rounds_file)
    print("City names added to game rounds data.")