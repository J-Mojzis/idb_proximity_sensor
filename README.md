## ReadMe für das IoT-Warnsystem mit Adafruit Feather nRF52840

### Inhaltsverzeichnis
1. [Überblick](#überblick)
2. [Anforderungen](#anforderungen)
3. [Hardware](#hardware)
4. [Installation](#installation)
5. [Konfiguration](#konfiguration)
6. [Verwendung](#verwendung)
7. [Fehlerbehebung](#fehlerbehebung)
8. [Beiträge](#beiträge)

### Überblick
Dieses Projekt implementiert ein IoT-Warnsystem, das Bewegungen erkennt, Entfernungen misst und diese Daten auf einem RGB-LED visualisiert sowie an ThingSpeak zur weiteren Analyse sendet. Das System besteht aus dem Adafruit Feather nRF52840, dem Adafruit AirLift FeatherWing für WiFi-Konnektivität und verschiedenen Grove-Sensoren.

### Anforderungen
- Adafruit Feather nRF52840
- Adafruit AirLift FeatherWing – ESP32 WiFi Co-Processor
- Grove Shield
- Grove Ultrasonic Ranger v2.0
- Grove PIR Motion Sensor v1.0
- Grove Chainable RGB LED v2.0
- Grove Buzzer v1.2
- ThingSpeak Account und API-Schlüssel
- Mu Editor (für die Entwicklung mit CircuitPython)

### Hardware
1. **Adafruit Feather nRF52840**: Mikrocontroller, der das System steuert.
2. **Adafruit AirLift FeatherWing**: WiFi-Konnektivität für das System.
3. **Grove Shield**: Verbindung zwischen Feather und Grove-Sensoren.
4. **Grove Ultrasonic Ranger v2.0**: Misst die Entfernung zu Objekten.
5. **Grove PIR Motion Sensor v1.0**: Erfasst Bewegungen.
6. **Grove Chainable RGB LED v2.0**: Zeigt die Entfernung als Farbe an.
7. **Grove Buzzer v1.2, adjustable**: Gibt bei Annäherung eines Objekts einen Warnton ab.

### Installation
1. **CircuitPython auf dem Feather installieren**:
   - Lade die neueste Version von CircuitPython von der [Adafruit Website](https://circuitpython.org/board/feather_nrf52840_express/) herunter und folge den Anweisungen zur Installation.
   
2. **Bibliotheken installieren**:
   - Lade das [Adafruit CircuitPython Bundle](https://circuitpython.org/libraries) herunter und kopiere die folgenden Bibliotheken in das `lib` Verzeichnis auf deinem Feather:
     - `adafruit_esp32spi`
     - `adafruit_bus_device`
     - `adafruit_requests`
   
3. **Projektdateien auf den Feather kopieren**:
   - Kopiere `code.py` und `secrets.py` auf das Hauptverzeichnis von `CIRCUITPY`.

### Konfiguration
1. **WiFi und ThingSpeak konfigurieren**:
   - Erstelle eine `secrets.py` Datei im Hauptverzeichnis von `CIRCUITPY` mit folgendem Inhalt:
     ```python
     secrets = {
         'ssid': 'YOUR_WLAN_NAME',
         'password': 'YOUR_WLAN_PASSWORD',
         'thingspeak_api_key': 'YOUR_THINGSPEAK_API_KEY'
     }
     ```
   
2. **ThingSpeak Channel einrichten**:
   - Melde dich bei [ThingSpeak](https://thingspeak.com/) an, erstelle einen neuen Kanal und füge die folgenden Felder hinzu:
     - `Motion`
     - `Distance`
     - `Color`
     - `Sound`
   - Kopiere den API-Schlüssel des Kanals in die `secrets.py`.

### Verwendung
1. **System einschalten**:
   - Schliesse das Feather an eine Stromquelle an.
   
2. **Systemüberwachung**:
   - Das System erkennt Bewegungen, misst Entfernungen und zeigt die entsprechenden Farben auf dem LED-Streifen an.
   - Die Daten werden in einem regelmässigen Abstand von 0.5 Sekunden an ThingSpeak gesendet.

3. **ThingSpeak-Dashboard**:
   - Gehe zu deinem ThingSpeak-Kanal und beobachte die Echtzeitdaten, die vom System gesendet werden.

### Fehlerbehebung
- **Keine WiFi-Verbindung**: Stelle sicher, dass die SSID und das Passwort in der `secrets.py` Datei korrekt sind.
- **Keine Daten an ThingSpeak gesendet**: Überprüfe den API-Schlüssel und stelle sicher, dass das WiFi funktioniert.
- **Falsche Entfernungen gemessen**: Kalibriere den Ultraschallsensor und überprüfe die Verbindungen.

### Beiträge
Beiträge und Erweiterungen zu diesem Projekt sind willkommen! Bitte erstelle einen Pull-Request oder öffne ein Issue, um Fehler zu melden oder neue Funktionen vorzuschlagen.
