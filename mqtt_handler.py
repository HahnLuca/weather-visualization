# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# --------------------------------------------------------------------------------------------------------------------
# MQTT subscriber with automatic database inserting

from datetime import datetime
import json
import pandas as pd
from paho.mqtt.client import Client
from sqlalchemy import exc
from database import engine, table_stations


# MQTT callbacks -----------------------------------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        with engine.connect() as con:
            df_stations = pd.read_sql_table(table_stations, con)
        topics = [(topic, 0) for topic in df_stations["mqtt_topic"]]
        client.subscribe(topics)
        # TODO Enable line below when debug=False was set in app.run_server()
        # In debug mode message is printed multiple times
        # print("Successfully connected to MQTT broker")
    else:
        print(f"Failed to connect, return code {rc}")


def on_disconnect(client, userdata, rc):
    print(f"Disconnected from MQTT broker, return code{rc}")


def on_message(client, userdata, msg):
    try:
        data_raw = json.loads(msg.payload.decode())
        # Check if actual data besides the rssi value was transmitted
        if any(data_raw[:-1]):
            # Set up a dictionary to store data and add a timestamp
            now = datetime.now()
            data = {"datetime": now.strftime("%Y-%m-%d %H:%M:%S")}

            # Store transmitted data in prepared dictionary
            # TODO implement general data format
            for item in data_raw:
                if item["variable"] == "TimeStamp":
                    item["value"] = pd.to_datetime(item["value"])
                try:
                    data.update({item["variable"].lower(): item["value"]})
                # Skip single None items in received data
                except TypeError:
                    pass

            # Insert data into the right table depending on the topic
            df = pd.DataFrame([data])
            print(df)
            try:
                df.to_sql(name=msg.topic.lower(), con=engine, if_exists="append", index=False)
            except exc.SQLAlchemyError as err:
                print(f"An error occured while inserting data into {msg.topic.lower()}:\n{err.__cause__}\n")

        else:
            print("No data received")

    except json.JSONDecodeError as err:
        print(f"Fehlerhafte Daten wurden empfangen:\n{err}")


# MQTT client initialization -----------------------------------------------------------------------------------------
# "Random" number as client id
mqtt_client = Client(client_id="838465957297104110")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.username_pw_set(username="student", password="student")
mqtt_client.connect(host="85.209.51.45", port=1883)
