# Studienarbeit
# HS Mannheim
# Fakultät Elektrotechnik
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# Abgabe: 21.04.2023
# -------------------------------------------------------------------------------------------------------------------
# Handle mqtt connection and write incoming data to database
# If current temperature is below/above certain values warnings will be publish on topic: 'station_warnings'

from datetime import datetime, timezone
import json
import pandas as pd
from paho.mqtt.client import Client
from sqlalchemy import exc, text,  inspect
from database import engine
from config import mqtt, table_stations, elements


# MQTT callbacks ----------------------------------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        # Subscribe to all the stations registered in database
        with engine.connect() as con:
            df_stations = pd.read_sql_table(table_stations, con)
        if not df_stations.empty:
            topics = [(f"station{station_id}", 0) for station_id in df_stations["ID"]]
            client.subscribe(topics)
        # Note: If app is running in debug mode message is printed multiple times
        print("Successfully connected to MQTT broker")
    else:
        print(f"Failed to connect, return code {rc}")


def on_disconnect(client, userdata, rc):
    # Note: If app is running in debug mode message is printed multiple times
    print(f"Disconnected from MQTT broker, return code {rc}")


def on_message(client, userdata, msg):
    # Format message and save to database ---------------------------------------------------------------------------
    try:
        data_raw = json.loads(msg.payload.decode())
    except json.JSONDecodeError as err:
        print(f"Fehlerhafte Daten wurden empfangen:\n{err}")
        return

    # Format data and add a utc timestamp
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    data = {"timestamp_utc": now}
    # Use only weather elements from config.py and ignore other transmitted data
    data.update({item["variable"]: item["value"] for item in data_raw
                 if item is not None and item["variable"] in list(elements.keys())})

    # Check if actual data besides rssi and timestamp value was transmitted
    if len(data) > 2:
        df = pd.DataFrame([data])
        print(df)

        # Insert data into the right table depending on the topic
        if inspect(engine).has_table(msg.topic):
            try:
                df.to_sql(name=msg.topic, con=engine, if_exists="append", index=False)
            except exc.SQLAlchemyError as err:
                print(f"An error occured while inserting data into {msg.topic}:\n{err.__cause__}\n")
        else:
            print(f"An error occured while inserting data into {msg.topic}: No table found called {msg.topic}")

        # Trigger a warning if certain temperature limit has been exceeded ------------------------------------------
        if "temperature" in df.columns:
            # Get station id from topic
            station_id = int(''.join(i for i in msg.topic if i.isdigit()))

            # Extract temperature to trigger a warning and current warning status from database
            warnings = {"Hitzewarnung": {"high_limit": True}, "Frostwarnung": {"high_limit": False}}
            for warning_type in warnings:
                with engine.connect() as con:
                    trigger_temp = pd.read_sql(text(f"SELECT {warning_type} FROM {table_stations} "
                                                    f"WHERE ID = {station_id}"), con)
                    active = pd.read_sql(text(f"SELECT active FROM warnings "
                                              f"WHERE station_ID = {station_id} AND warning_type = '{warning_type}' "
                                              f"ORDER BY ID DESC LIMIT 1"), con)

                # Create dictionary to work with
                warnings[warning_type]["trigger_temp"] = trigger_temp[warning_type].iat[0]
                if not active.empty:
                    warnings[warning_type]["active"] = active["active"].iat[0]
                else:
                    warnings[warning_type]["active"] = 0

            # Check current temperature and publish warning if required
            for warning_type in warnings:
                # Define warning conditions depending on warning type
                if warnings[warning_type]["high_limit"]:
                    warning_coming = (df["temperature"].iat[0] >= warnings[warning_type]["trigger_temp"] and
                                      not warnings[warning_type]["active"])
                    warning_going = (df["temperature"].iat[0] < warnings[warning_type]["trigger_temp"] - 0.5 and
                                     warnings[warning_type]["active"])
                else:
                    warning_coming = (df["temperature"].iat[0] <= warnings[warning_type]["trigger_temp"] and
                                      not warnings[warning_type]["active"])
                    warning_going = (df["temperature"].iat[0] > warnings[warning_type]["trigger_temp"] + 0.5 and
                                     warnings[warning_type]["active"])

                # Write a message to database and publish message on mqtt broker if warning is coming or going
                if warning_coming or warning_going:
                    warning = {
                        "timestamp_utc": now,
                        "station_ID": station_id,
                        "warning_type": warning_type,
                        "trigger_temp": warnings[warning_type]["trigger_temp"],
                        "active": not warnings[warning_type]["active"]
                    }
                    df_warning = pd.DataFrame([warning])
                    df_warning.to_sql(name="warnings", con=engine, if_exists="append", index=False)
                    warning_json = df_warning.to_json(orient="records")
                    mqtt_client.publish(topic="station_warnings", payload=warning_json, qos=2)

    # Skip saving data if only rssi was transmitted
    else:
        print("No data received")


def on_publish(client, userdata, result):
    print("Warning has been published")


# MQTT client initialization ----------------------------------------------------------------------------------------
mqtt_client = Client(mqtt["client_id"])
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message
mqtt_client.on_publish = on_publish
mqtt_client.username_pw_set(mqtt["username"], mqtt["password"])
mqtt_client.connect(mqtt["host"], mqtt["port"])

# File can be used without main application -------------------------------------------------------------------------
if __name__ == '__main__':
    mqtt_client.loop_forever()
