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

    # compute "days ago" from startTime and add as a column for coloring
    df["start_dt"] = pd.to_datetime(df.get("startTime"), errors="coerce")
    if df["start_dt"].notna().any():
        max_dt = df["start_dt"].max()
        df["days_ago"] = (max_dt - df["start_dt"]).dt.days
        # fill NaN days_ago with max value
        df["days_ago"] = df["days_ago"].fillna(df["days_ago"].max() if df["days_ago"].notna().any() else 0)
    else:
        df["days_ago"] = 0

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lng",
        color="days_ago",
        labels={"days_ago": "days_since_last_visit",},
        color_continuous_scale="sunsetdark",
        hover_name="city",
        hover_data= [], # ["startTime", "panoId"]
        zoom=1.25,
        height=750
    )
    # use a small semi-transparent marker
    fig.update_traces(marker=dict(size=3.5, opacity=0.85))

    fig.update_layout(mapbox_style="carto-darkmatter")
    fig.update_layout(margin={"r":5,"t":5,"l":5,"b":5})
    fig.show()
