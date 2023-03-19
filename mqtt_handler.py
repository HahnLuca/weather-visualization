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
from sqlalchemy import exc, text, insert
from database import engine, meta
from config import mqtt, table_stations, elements


# MQTT callbacks -----------------------------------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        with engine.connect() as con:
            df_stations = pd.read_sql_table(table_stations, con)
        # TODO Activate again
        topics = [("station" + str(station_id), 0) for station_id in df_stations["ID"]]
        # topics = [("Wetterstation", 0), ("Wetterstation_HSMA", 0)]
        client.subscribe(topics)
        # In debug mode message is printed multiple times
        # TODO Enable line below when debug=False was set in app.run_server()
        # print("Successfully connected to MQTT broker")
    else:
        print(f"Failed to connect, return code {rc}")


def on_disconnect(client, userdata, rc):
    print(f"Disconnected from MQTT broker, return code{rc}")


def on_message(client, userdata, msg):
    try:
        data_raw = json.loads(msg.payload.decode())
    except json.JSONDecodeError as err:
        print(f"Fehlerhafte Daten wurden empfangen:\n{err}")
        return

    # Preset a timestamp in case none is transmitted
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {"timestamp": now}
    # Remove Nones and not expected variables from data
    valid_variables = list(elements.keys())
    valid_variables.append("timestamp")
    data.update({item["variable"].lower(): item["value"] for item in data_raw
                 if item is not None and item["variable"].lower() in valid_variables})
    # Make sure transmitted timestamp is in correct format
    data["timestamp"] = pd.to_datetime(data["timestamp"])

    # Check if actual data besides rssi and timestamp value was transmitted
    if len(data) > 2:
        df = pd.DataFrame([data])
        print(df)

        # Insert data into the right table depending on the topic
        # TODO Activate again
        sql_table = "station" + msg.topic
        # if msg.topic == "Wetterstation":
        #     sql_table = "station1000"
        # elif msg.topic == "Wetterstation_HSMA":
        #     sql_table = "station2000"
        # else:
        #     sql_table = ""
        try:
            df.to_sql(name=sql_table, con=engine, if_exists="append", index=False)
        except exc.SQLAlchemyError as err:
            print(f"An error occured while inserting data into {sql_table}:\n{err.__cause__}\n")

        # Trigger a warning if certain temperature limits are exceeded
        # if "temperature" in df.columns:
        #     with engine.connect() as con:
        #         warnings = pd.read_sql_query(text(f"SELECT Hitzewarnung, Frostwarnung FROM {table_stations} "
        #                                           f"WHERE ID = {1000}"), con)
        #         active = pd.read_sql_query(text(f"SELECT active FROM warnings "
        #                                              f"WHERE station = {'1000'} AND warning_type = 'Hitzewarnung' "
        #                                              f"ORDER BY ID DESC LIMIT 1"), con)
        #         frost_active = pd.read_sql_query(text(f"SELECT active FROM warnings "
        #                                               f"WHERE station = {'1000'} AND warning_type = 'Frostwarnung' "
        #                                               f"ORDER BY ID DESC LIMIT 1"), con)
        #     print(active)
            # Log a message if heat warning is coming or going
            # if ((df["temperature"].iat[0] >= warnings["Hitzewarnung"].iat[0] and not mqtt_client.warning_heat) or
            #         (df["temperature"].iat[0] < warnings["Hitzewarnung"].iat[0] and mqtt_client.warning_heat)):
            #     mqtt_client.warning_heat = not mqtt_client.warning_heat
            #     warning = {
            #         "timestamp": now,
            #         "station": "1000",
            #         "warning_type": 'Hitzewarnung',
            #         "trigger_temp": warnings['Hitzewarnung'].iat[0],
            #         "active": mqtt_client.warning_heat
            #     }
            #     df_warning = pd.DataFrame([warning])
            #     df_warning.to_sql(name="warnings", con=engine, if_exists="append", index=False)
            #
            # # Log a message if frost warning is coming or going
            # elif ((df["temperature"].iat[0] <= warnings["Frostwarnung"].iat[0] and not mqtt_client.warning_frost) or
            #       (df["temperature"].iat[0] > warnings["Frostwarnung"].iat[0] and mqtt_client.warning_frost)):
            #     mqtt_client.warning_frost = not mqtt_client.warning_frost
            #     warning = {
            #         "timestamp": now,
            #         "station": "1000",
            #         "warning_type": 'Frostwarnung',
            #         "trigger_temp": warnings['Frostwarnung'].iat[0],
            #         "active": mqtt_client.warning_frost
            #     }
            #     df_warning = pd.DataFrame([warning])
            #     df_warning.to_sql(name="warnings", con=engine, if_exists="append", index=False)

    else:
        print("No data received")


# MQTT client initialization -----------------------------------------------------------------------------------------
mqtt_client = Client(mqtt["client_id"])
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.username_pw_set(mqtt["username"], mqtt["password"])
mqtt_client.connect(mqtt["host"], mqtt["port"])
