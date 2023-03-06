# Studienarbeit
# Name: Luca Hahn
# Matrikelnr: 1923199
# Betreuer: Prof. Dr. Christof Hübner
# ------------------------------------------------------------------------------------------------------------------
# Project specific configurations

import pandas as pd

# Weather stations
# Additional stations can be added here (no need to change code somewhere else)
stations = pd.DataFrame({
    "name": ["Wetterstation", "Wetterstation1"],
    "latitude": [49.481562, 49.497],
    "longitude": [8.502555, 8.52]
})

# MQTT configurations (case-sensitive)
mqtt = {
    "broker": "85.209.51.45",
    "port": 1883,
    "user": "student",
    "passwd": "student",
    "client_id": "192319968165",
    "topics": [("Wetterstation", 0), ("Wetterstation_HSMA", 0)]  # [(name, 0) for name in stations["name"]]
}

# MySQL configurations (case-sensitive and case-insensitive possible)
sql = {
    "user": "student",
    "passwd": "student",
    "host": "localhost",
    "database": "wetterstationen",
    "tables": [name.lower() for name in stations["name"]]
}

# Color configuration for different types of data
colors = {
    "temperature": "indianred",
    "humidity": "cadetblue",
    "air pressure": "slategray",
    "wind": "coral",
    "rain": "steelblue",
    "signal": "olivedrab"
}
