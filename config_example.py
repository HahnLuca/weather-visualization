# Studienarbeit
# HS Mannheim
# Fakultät Elektrotechnik
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# Abgabe: 21.04.2023
# ------------------------------------------------------------------------------------------------------------------
# In this file all the information about the MQTT broker and the MySQL server have to be added
# Additionaly the information about the weather elements can be changed here if desired

# Enter the information about the MQTT broker you are using (can be obtained by Prof. Hübner)
mqtt = {
    "client_id": "123456789",  # Choose a random number as client id
    "username": "your_mqtt_username",  # Enter the username for your MQTT broker
    "password": "your_mqtt_password",  # Enter the password for your MQTT broker
    "host": "1.2.3.4",  # Enter your host address
    "port": 1883
}

# Enter the information about the previously created MySQL server
sql = {
    "drivername": "mysql",
    "username": "your_db_username",  # Enter the previously set username for your MySQL server
    "password": "your_db_password",  # Enter the previously set password for your MySQL server
    "host": "localhost",  # In case you are using a webserver to host the database you have to change this attribute
    "database": "project_weather_dash"
}

# Name of table in database storing all the weather stations
table_stations = "weather_stations"

# In case you are prefering different units/ranges for your data you can change them here
elements = {
    "temperature": {"name": "Temperatur", "unit": "°C", "range": [-10, 40],
                    "color": "indianred", "icon": "bi bi-thermometer-half"},
    "humidity": {"name": "Luftfeuchtigkeit", "unit": "%", "range": [0, 100],
                 "color": "cadetblue", "icon": "bi bi-droplet-half"},
    "windspeed": {"name": "Windstärke", "unit": "(Bft)", "range": [0, 12],
                  "color": "coral", "icon": "bi bi-wind"},
    "winddirection": {"name": "Windrichtung", "unit": "°", "range": [0, 360],
                      "color": "slategray", "icon": "bi bi-compass"},
    "rain": {"name": "Regen", "unit": "mm", "range": [0, 60],
             "color": "steelblue", "icon": "bi bi-cloud-rain"},
    "rssi": {"name": "Signalstärke", "unit": "dBm", "range": [-120, 0],
             "color": "olivedrab", "icon": "bi bi-reception-4"},
}
