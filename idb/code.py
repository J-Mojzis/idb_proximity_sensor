#Project libraries
import time
import board
import analogio
import digitalio
import pwmio

#Airlift Wifi librarie
import busio
import adafruit_esp32spi.adafruit_esp32spi as esp32spi
import adafruit_esp32spi.adafruit_esp32spi_wifimanager as wifimanager
import adafruit_requests as requests

from secrets import secrets


# Pins for sensors and actuators
MOTION_SENSOR_PIN = board.A2
ULTRASONIC_PIN = board.D9 #D5
LED_CLK_PIN = board.D5 #D9
LED_DATA_PIN = board.D6 #D10
BUZZER_PIN = board.A0

# Pins for Airlift Wifi
ESP32_CS = board.D13
ESP32_READY = board.D11
ESP32_RESET = board.D12

# Constants for timeouts and thresholds
_TIMEOUT1 = 500
_TIMEOUT2 = 5000
NUMBER_OF_LEDS = 1
MOTION_THRESHOLD = 20000

# Setup for buzzer
cycle = 65535 // 5  # 20% power
buzzer = pwmio.PWMOut(BUZZER_PIN, duty_cycle=cycle, variable_frequency=True)

# Setup for motion sensor
motion_sensor = analogio.AnalogIn(MOTION_SENSOR_PIN)

# Setup for WiFi
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp32_cs = digitalio.DigitalInOut(ESP32_CS)
esp32_ready = digitalio.DigitalInOut(ESP32_READY)
esp32_reset = digitalio.DigitalInOut(ESP32_RESET)
esp = esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
wifi = wifimanager.ESPSPI_WiFiManager(esp, secrets, None)

# ThingSpeak API URL
THINGSPEAK_URL = "https://api.thingspeak.com/update"

class GroveUltrasonicRanger:
    def __init__(self, pin):
        """
        Initialize the ultrasonic ranger with the specified pin.
        Variables:
        - pin: Pin connected to the ultrasonic ranger (input).
        """
        self.dio = digitalio.DigitalInOut(pin)

    def _get_distance(self):
        """
        Method to measure distance using the ultrasonic sensor.
        Variables:
        - self.dio: Digital input/output pin for triggering and reading the ultrasonic sensor (input/output).
        - t0, t1, t2: Timing variables for pulse calculation (internal).
        - count: Counter for timeout loops (internal).
        Output:
        - distance: Calculated distance in cm, or None if measurement fails (output).
        """
        self.dio.direction = digitalio.Direction.OUTPUT
        self.dio.value = False
        time.sleep(0.000002)
        self.dio.value = True
        time.sleep(0.000010)
        self.dio.value = False

        self.dio.direction = digitalio.Direction.INPUT

        t0 = time.monotonic()
        count = 0
        while count < _TIMEOUT1:
            if self.dio.value:
                break
            count += 1
        if count >= _TIMEOUT1:
            return None

        t1 = time.monotonic()
        count = 0
        while count < _TIMEOUT2:
            if not self.dio.value:
                break
            count += 1
        if count >= _TIMEOUT2:
            return None

        t2 = time.monotonic()
        dt = int((t1 - t0) * 1000000)
        if dt > 530:
            return None

        duration = t2 - t1  # Zeit in Sekunden
        distance_cm = (duration * 34300) / 2 # Schallgeschwindigkeit in cm/s

        # Debugging-Informationen
        print(f"t0: {t0}, t1: {t1}, t2: {t2}, duration: {duration}, distance_cm: {distance_cm}")

        return distance_cm

    def get_distance(self):
        """
        Method to continuously measure and return the distance.
        Output:
        - dist: Measured distance in cm (output).
        """
        while True:
            dist = self._get_distance()
            if dist:
                return dist

class ChainableLED:
    def __init__(self, clk_pin, data_pin, number_of_leds):
        """
        Initialize the chainable LED with clock and data pins, and the number of LEDs.
        Variables:
        - clk_pin: Pin for the clock signal (input).
        - data_pin: Pin for the data signal (input).
        - number_of_leds: Number of LEDs in the chain (input).
        """
        self.__clk_pin = digitalio.DigitalInOut(clk_pin)
        self.__data_pin = digitalio.DigitalInOut(data_pin)
        self.__number_of_leds = number_of_leds

        self.__clk_pin.direction = digitalio.Direction.OUTPUT
        self.__data_pin.direction = digitalio.Direction.OUTPUT

        for i in range(self.__number_of_leds):
            self.setColorRGB(i, 0, 0, 0)

    def clk(self):
        """
        Clock pulse for the LED communication.
        Variables:
        - self.__clk_pin: Pin for the clock signal (output).
        """
        self.__clk_pin.value = False
        time.sleep(0.00002)
        self.__clk_pin.value = True
        time.sleep(0.00002)

    def sendByte(self, b):
        """
        Send a byte of data to the LED.
        Variables:
        - b: Byte to send (input).
        - self.__data_pin: Pin for the data signal (output).
        """
        for i in range(8):
            self.__data_pin.value = (b & 0x80) != 0
            self.clk()
            b = b << 1

    def sendColor(self, red, green, blue):
        """
        Send the color data to the LED.
        Variables:
        - red: Red color value (input).
        - green: Green color value (input).
        - blue: Blue color value (input).
        - prefix: Prefix for color data (internal).
        """
        prefix = 0xC0
        if (blue & 0x80) == 0:
            prefix |= 0x20
        if (blue & 0x40) == 0:
            prefix |= 0x10
        if (green & 0x80) == 0:
            prefix |= 0x08
        if (green & 0x40) == 0:
            prefix |= 0x04
        if (red & 0x80) == 0:
            prefix |= 0x02
        if (red & 0x40) == 0:
            prefix |= 0x01
        self.sendByte(prefix)
        self.sendByte(blue)
        self.sendByte(green)
        self.sendByte(red)

    def setColorRGB(self, led, red, green, blue):
        """
        Set the color of the specified LED.
        Variables:
        - led: LED index (input).
        - red: Red color value (input).
        - green: Green color value (input).
        - blue: Blue color value (input).
        """
        self.sendByte(0x00)
        self.sendByte(0x00)
        self.sendByte(0x00)
        self.sendByte(0x00)
        for i in range(self.__number_of_leds):
            self.sendColor(red, green, blue)
        self.sendByte(0x00)
        self.sendByte(0x00)
        self.sendByte(0x00)
        self.sendByte(0x00)

def send_to_thingspeak(distance, motion, color, sound):
    """
    Send data to ThingSpeak.
    Variables:
    - distance: Distance measured by the ultrasonic sensor (input).
    - motion: Motion detected by the motion sensor (input).
    - color: Color code for the LED (input).
    - sound: Sound state for the buzzer (input).
    """
    payload = {
        'api_key': secrets['thingspeak_api_key'],
        'field1': motion,
        'field2': distance,
        'field3': color,
        'field4': sound
    }
    # Manuelles Erstellen der URL mit Parametern
    url = THINGSPEAK_URL + "?"
    for key, value in payload.items():
        url += f"{key}={value}&"
    url = url.rstrip('&')  # Entferne das letzte '&'

    response = wifi.get(url)  # Verwende die manuell erstellte URL
    if response.status_code == 200:
        print("Data sent to ThingSpeak")
    else:
        print("Failed to send data")

def main():
    """
    Main function to detect motion, measure distance, and control LED and buzzer.
    Variables:
    - sonar: Instance of GroveUltrasonicRanger for distance measurement (internal).
    - rgb_led: Instance of ChainableLED for controlling LED colors (internal).
    - motion_value: Value read from the motion sensor (internal).
    - distance: Measured distance from the ultrasonic sensor (internal).
    """
    buzzer.duty_cycle = 0
    sonar = GroveUltrasonicRanger(ULTRASONIC_PIN)
    rgb_led = ChainableLED(LED_CLK_PIN, LED_DATA_PIN, NUMBER_OF_LEDS)

    # Connect to WiFi
    print("Connecting to WiFi...")
    wifi.connect()
    print("Connected to WiFi!")

    print('Detecting distance...')
    while True:
        color = "Off"  # Default color value
        sound = "Off"  # Default sound value
        motion_value = motion_sensor.value
        if motion_value > MOTION_THRESHOLD:
            print("Motion detected!")
            distance = sonar.get_distance()
            if distance > 0:
                print(f'Distance: {distance} cm')
            else:
                print("Distance-measurement faillure")

            if distance > 0:
                if distance > 350:
                    rgb_led.setColorRGB(0, 0, 105, 0)  # Green
                    buzzer.duty_cycle = 0  # Turn off buzzer
                    color = "Green"
                elif 200 < distance <= 350:
                    rgb_led.setColorRGB(0, 0, 105, 105)  # Cyan
                    buzzer.duty_cycle = 0
                    color = "Cyan"
                elif 100 < distance <= 200:
                    rgb_led.setColorRGB(0, 0, 0, 105)  # Blue
                    buzzer.duty_cycle = 0
                    color = "Blue"
                elif 50 < distance <= 100:
                    rgb_led.setColorRGB(0, 105, 0, 105)  # Violet
                    buzzer.duty_cycle = 0
                    color = "Violet"
                else:
                    rgb_led.setColorRGB(0, 105, 0, 0)  # Red
                    buzzer.frequency = 2200
                    buzzer.duty_cycle = cycle
                    color = "Red"
                    sound = "On"
                send_to_thingspeak(distance, 1, color, sound)  # Motion detected
            else:
                print("Failed to measure distance")
        else:
            print("No motion.")
            rgb_led.setColorRGB(0, 0, 0, 0)
            buzzer.duty_cycle = 0
            send_to_thingspeak(0, 0, color, sound)  # No motion
        time.sleep(0.5)

if __name__ == '__main__':
    main()
