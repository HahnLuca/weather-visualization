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
from utils import connect_to_db
import config


class MQTTHandler:
    def __init__(self, mqtt, eng):
        self.broker = mqtt["broker"]
        self.port = mqtt["port"]
        self.user = mqtt["user"]
        self.client_id = mqtt["client_id"]
        self.topics = mqtt["topics"]
        self.mqtt_connected = False

        self.engine = eng

        # Client initialization
        self.client = Client(self.client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.user, mqtt["passwd"])
        self.client.connect(self.broker, self.port)

    # Callback - Subscribe to topic on connection
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.mqtt_connected = True
            client.subscribe(self.topics)
            print("Successfully connected to MQTT broker")
        else:
            print(f"Failed to connect, return code {rc}")

    # Callback - Reset flag on disconnection
    def on_disconnect(self, client, userdata, rc):
        self.mqtt_connected = False
        print(f"Disconnected from MQTT broker, return code{rc}")

    # Callback - Convert message and add a timestamp
    def on_message(self, client, userdata, msg):
        # Convert JSON to Python format
        try:
            data_raw = json.loads(msg.payload.decode())
            # Check if actual data besides the rssi value was transmitted
            if any(data_raw[:-1]):
                # Set up a dictionary to store data and add a timestamp
                now = datetime.now()
                data = {"datetime": now.strftime("%Y-%m-%d %H:%M:%S")}

                # Store transmitted data in prepared dictionary
                for item in data_raw:
                    try:
                        data.update({item["variable"]: item["value"]})
                    # Skip single None items in received data
                    except TypeError:
                        pass

                # Insert data into the right table depending on the topic
                df = pd.DataFrame([data])
                print(df)
                try:
                    df.to_sql(name=msg.topic.lower(), con=self.engine, if_exists="append", index=False)
                except exc.SQLAlchemyError as err:
                    print(f"An error occured while inserting data into {msg.topic.lower()}:\n{err.__cause__}\n")

            else:
                print("No data received")

        except json.JSONDecodeError as err:
            print(f"Fehlerhafte Daten wurden empfangen:\n{err}")


if __name__ == '__main__':
    handler = MQTTHandler(config.mqtt, connect_to_db(config.sql))
    handler.client.loop_forever()
