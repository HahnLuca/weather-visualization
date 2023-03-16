# Studienarbeit an der HS Mannheim

"Webbasierte Visualisierung von Umweltmessdaten mit Python und MQTT"

## Versionsdokumentation
Im Folgenden werden Änderungen zwischen den einzelnen Versionen dokumentiert.

### Version 0.2.0 - 16.03.2023
* Ersetzen der Zugangsdaten durch fiktive Daten
* Automatische Anpassung der Kartenzoomstufe je nach Verteilung der Wetterstationen
* Auswahl der Stationen sowohl über Karte als auch über Dropdown möglich
* Neustrukturierung der MySQL Tabelle "wetterstationen"
  * Stationen werden über ID identifiziert
* Auswahl der Anzeige aller Daten oder nur tagesspezifische Werte (min, mean, max)
* Verbesserte MQTT callback Funtion "on_message"
* Ergänzung neuer Plots für Wind, Regen und Signalstärke

### Version 0.1.0 - 10.03.2023
* Speicherung aller über MQTT empfangenen Nachrichten in stationsspezifischen Tabellen (MySQL)
* Erste Version Dashboard
* Zugriffsbeschränkte "Konfigurieren" Seite
  * Hinzufügen Wetterstationen
  * Registrieren neuer Benutzer
* Login Möglichkeit
  * Benutzerverwaltung in Datenbank
  * Passwörter werden gehashed und nicht als Klartext gespeichert
* Anlegen neuer Wetterstationen
  * Überprüfung, ob Änderungen keine Konflikte auslösen
  * Automatische Generation neuer stationsspezifischer Tabelle in Datenbank
  * Aktualisieren der MQTT Abonnements
    