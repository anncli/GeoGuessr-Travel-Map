import pandas as pd
import json

def load_classic_rounds(filename):
    with open(filename) as f:
        data = json.load(f)
    # Already flat, just select relevant fields
    rounds = []
    for r in data:
        rounds.append({
            "lat": r.get("lat"),
            "lng": r.get("lng"),
            "city": r.get("city", ""),
            "startTime": r.get("startTime", ""),
            "panoId": r.get("panoId", "")
        })
    return rounds

def load_duel_rounds(filename):
    with open(filename) as f:
        data = json.load(f)
    rounds = []
    for r in data:
        pano = r.get("panorama", {})
        rounds.append({
            "lat": pano.get("lat"),
            "lng": pano.get("lng"),
            "city": r.get("city", ""),
            "startTime": r.get("startTime", ""),
            "panoId": pano.get("panoId", "")
        })
    return rounds

classic_rounds = load_classic_rounds("../classic_games_data.json")
duel_rounds = load_duel_rounds("../duel_games_data.json")

all_rounds = classic_rounds + duel_rounds
df = pd.DataFrame(all_rounds)
df = df.dropna(subset=["lat", "lng"])  # Remove rounds missing coordinates

df.to_csv('data_points.csv', encoding='utf-8', index=False)

import plotly.express as px

fig = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lng",
    hover_name="city",
    hover_data=["startTime", "panoId"],
    color_discrete_sequence=["light blue"],
    zoom=1.25,
    height=750
)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_traces(marker=dict(size=4.5))
fig.show()
