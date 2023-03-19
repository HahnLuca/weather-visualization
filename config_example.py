# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# ------------------------------------------------------------------------------------------------------------------
# Example for project specific configurations


# MQTT configurations
mqtt = {
    "client_id": "123456789",  # TODO Choose a random number as client id
    "username": "your_mqtt_username",  # TODO Enter the username for your MQTT broker
    "password": "your_mqtt_password",  # TODO Enter the password for your MQTT broker
    "host": "1.2.3.4",  # TODO Enter your host address
    "port": 1883
}

# MySQL configurations
sql = {
    "drivername": "mysql",
    "username": "your_db_username",  # TODO Enter the previously set username for your MySQL server
    "password": "your_db_password",  # TODO Enter the previously set password for your MySQL server
    "host": "localhost",
    "database": "project_weather_dash"
}

# Name of table in database storing all the weather stations
table_stations = "weather_stations"

# Element configurations
elements = {
    "temperature": {"name": "Temperatur", "unit": "°C", "range": [-10, 40],
                    "color": "indianred", "icon": "bi bi-thermometer-half"},
    "humidity": {"name": "Luftfeuchtigkeit", "unit": "%", "range": [0, 100],
                 "color": "cadetblue", "icon": "bi bi-droplet-half"},
    "windspeed": {"name": "Windstärke", "unit": "(Bft)", "range": [0, 12],
                  "color": "coral", "icon": "bi bi-wind"},
    "winddirection": {"name": "Windrichtung", "unit": "°", "range": [0, 360],
                      "color": "slategray", "icon": "bi bi-compass"},
    "rain": {"name": "Regen", "unit": "mm", "range": [0, 100],
             "color": "steelblue", "icon": "bi bi-cloud-rain"},
    "rssi": {"name": "Signalstärke", "unit": "dBm", "range": [-100, 100],
             "color": "olivedrab", "icon": "bi bi-reception-4"},
}
