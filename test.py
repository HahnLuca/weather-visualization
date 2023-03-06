# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# --------------------------------------------------------------------------------------------------------------------
# Test area

import random
from datetime import datetime
import dash
from sqlalchemy import create_engine, text
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Data
table = "wetterstation"
data_raw = [{"variable": "temperature", "value": 20},
            {"variable": "humidity", "value": 40}]
now = datetime.now()
data = {"datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        # "temperature": 10.2,
        "humidity": 90,
        "rssi": -82.4}

# Actual test area
url = "mysql+mysqlconnector://student:student@localhost/wetterstationen"
engine = create_engine(url)
con = engine.connect()

df = pd.read_sql_table(table, con=con, index_col='datetime')
# print(df.last("24h"))

# series = pd.date_range(start="2023-01-01", end="2023-02-23", freq="1H")
# df = pd.DataFrame(index=series)
# df["temperature"] = 15-abs(df.index.day-15) + 6-abs(df.index.hour-12)
# df["humidity"] = 50 + df["temperature"]
# df["rssi"] = -df["humidity"]-10
# df = df.reset_index(names="datetime")
# print(df)
# df.to_sql(name=table, con=engine, if_exists='append', index=False)


# df_daily = pd.DataFrame()
# for column in df.columns[1:-1]:
#     df_daily[f"{column}_min"] = df[f"{column}"].resample("D").min()
#     df_daily[f"{column}_mean"] = df[f"{column}"].resample("D").mean()
#     df_daily[f"{column}_max"] = df[f"{column}"].resample("D").max()
