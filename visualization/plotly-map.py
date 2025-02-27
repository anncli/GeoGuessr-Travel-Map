import pandas as pd
with open('game_rounds.json') as data_points:
    df = pd.read_json(data_points)

df.to_csv('data_points.csv', encoding='utf-8', index=False)
# us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")

import plotly.express as px

fig = px.scatter_map(df, lat="lat", lon="lng", hover_name="streakLocationCode", hover_data=["startTime", "panoId"],
                        color_discrete_sequence=["light blue"], zoom=1.25, height=750)
fig.update_layout(map_style="carto-voyager-nolabels")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
