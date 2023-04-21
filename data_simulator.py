# Studienarbeit
# HS Mannheim
# Fakultät Elektrotechnik
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# Abgabe: 21.04.2023
# --------------------------------------------------------------------------------------------------------------------
# Use this file to simulate a station in case you want to test the code for specific data
# Additionaly it can be used to verify the transmission of the warning messages from the main application

import time
import json
from paho.mqtt.client import Client
from config import mqtt


# MQTT callbacks -----------------------------------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
    mqtt_client.subscribe("station_warnings")
    if rc == 0:
        print("Successfully connected to MQTT broker")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    print(msg.payload.decode())


def on_publish(client, userdata, result):
    print("Data published")


# MQTT client initialization -----------------------------------------------------------------------------------------
mqtt_client = Client("47756267")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_publish = on_publish
mqtt_client.username_pw_set(mqtt["username"], mqtt["password"])
mqtt_client.connect(mqtt["host"], mqtt["port"])
mqtt_client.loop_start()

# Simulate and publish sensor data -----------------------------------------------------------------------------------
temperature = 20
while True:
    # Dynamically change temperature
    if temperature < 25:
        temperature += 1
    else:
        temperature = 20

    data = [
        {"variable": "temperature", "value": temperature},
        {"variable": "humidity", "value": "70"},
        {"variable": "rain", "value": "9"},
        {"variable": "winddirection", "value": "225"},
        {"variable": "windspeed", "value": "4"},
        {"variable": "rssi", "value": "-79"}
    ]

    # Publish simulated data and wait before publishing next data
    print(data)
    mqtt_client.publish("station1207", json.dumps(data), qos=2)
    time.sleep(5)
