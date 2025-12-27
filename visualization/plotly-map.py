import os
import sqlite3
import pandas as pd
import plotly.express as px

def load_rounds_from_db(db_path=None):
    if db_path is None:
        db_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "geoguessr.db"))
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT lat,lng,city,startTime,panoId FROM rounds WHERE lat IS NOT NULL AND lng IS NOT NULL", conn)
    conn.close()
    return df

if __name__ == "__main__":
    df = load_rounds_from_db()
    if df.empty:
        print("No rounds found in DB.")
        raise SystemExit(1)

    df = df.dropna(subset=["lat", "lng"])

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
