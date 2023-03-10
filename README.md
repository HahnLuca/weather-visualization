# Studienarbeit an der HS Mannheim

"Webbasierte Visualisierung von Umweltmessdaten mit Python und MQTT"

## Versionsdokumentation
Im Folgenden werden Änderungen zwischen den einzelnen Versionen dokumentiert.

### Version 0.1.0 - Erster Upload (10.03.2023)
* Speicherung aller über MQTT empfangenen Nachrichten in stationsspezifischen Tabellen (MySQL)
* Erste Version Dashboard
* Zugriffsbeschränkte "Konfigurieren" Seite
  * Hinzufügen Wetterstationen
  * Registrieren neuer Benutzer
* Login Möglichkeit
  * Benutzerverwaltung in Datenbank
  * Passwörter werden gehashed und nicht als Klartext gespeichert
* Anlegen neuer Wetterstationen
  * Üperprüfung, ob Änderungen keine Konflikte auslösen
  * Automatische Generation neuer stationsspezifischer Tabelle in Datenbank
  * Aktualisieren der MQTT Abonnements
    