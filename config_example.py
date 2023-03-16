# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# ------------------------------------------------------------------------------------------------------------------
# Example for project specific configurations


# MQTT configurations
mqtt = {
    # "Random" number as client id
    "client_id": "123456789",
    "username": "your_mqtt_username",
    "password": "your_mqtt_password",
    "host": "1.2.3.4",
    "port": 1883
}

# MySQL configurations
sql = {
    "drivername": "mysql",
    "username": "your_db_username",
    "password": "your_db_password",
    "host": "localhost",
    "database": "your_database_name"
}

# Name of table in database storing all the weather stations
table_stations = "wetterstationen"

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

