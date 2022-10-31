# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Note, you must create a feed called that corresponds to the feed referenced in your AdafruitIO account.
# Your secrets file must contain your aio_username and aio_key

# libraries
import time
import board
import busio
import adafruit_dht
from digitalio import DigitalInOut
from digitalio import Direction
import terminalio
import displayio
import adafruit_ssd1306
from adafruit_display_text import label

text = "HELLO WORLD"
font = terminalio.FONT
color = 0x0000FF

i2c = busio.I2C(board.GP1, board.GP0) #i2c bus for the display
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Make the display context
display.fill(0) #blank
display.show()

#test display
# Set a pixel in the origin 0,0 position.
display.pixel(0, 0, 1)
# Set a pixel in the middle 64, 16 position.
display.pixel(64, 16, 1)
# Set a pixel in the opposite 127, 31 position.
display.pixel(127, 31, 1)
display.show()


# ESP32 AT
from adafruit_espatcontrol import (
    adafruit_espatcontrol,
    adafruit_espatcontrol_wifimanager,
)

#Pins
dht = adafruit_dht.DHT22(board.GP15) #set up DHT22 on GP15/Pin 20
led = DigitalInOut(board.LED) 		# set up the Pico Led Pin
led.direction = Direction.OUTPUT 	# set to Output

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Pins setup with WizFi360 through UART connection
RX = board.GP5 #TX pin for WizFi360-EVB-PICO
TX = board.GP4 #RX pin for WizFi360-EVB-PICO
resetpin = DigitalInOut(board.GP20) #Reset pin for WizFi360-EVB-PICO
rtspin = False #RTS pin
uart = busio.UART(TX, RX, baudrate=11520, receiver_buffer_size=2048) #Serial settings

# Debug Level
# Change the Debug Flag if you have issues with AT commands
debugflag = False
status_light = False #only if board has neopixel

print("ESP AT commands")
# For Boards that do not have an rtspin like WizFi360-EVB-PICO set rtspin to False.
esp = adafruit_espatcontrol.ESP_ATcontrol(
    uart, 115200, reset_pin=resetpin, rts_pin=rtspin, debug=debugflag
)
wifi = adafruit_espatcontrol_wifimanager.ESPAT_WiFiManager(esp, secrets, status_light) #Class that handles HTTPs and MQTT (more information from lib)

temperature = dht.temperature #get temperature
humidity = dht.humidity       #get humidity
temp=str(temperature)
humid=str(humidity)
display.fill(0)
display.text('Readings Aquired', 10, 0, 1)
display.text('Temperature: '+temp+' C', 10, 10, 1)
display.text('Humidity: '+humid+'%', 10, 20, 1)

display.show()
print(dht.temperature)        #print temperature
print(dht.humidity)           #print humidity
while True:
    try:
        led.value = False #only for boards with integrated neopixel
        temperature = dht.temperature #get temperature
        humidity = dht.humidity       #get humidity

        print("Posting temperature...", end="") #Posting temperature to Adafruit.io
        data = temperature #counter result = input data
        feed = "temp-wizfi360" # Adafruit IO feed, the name on adafruit io needs to be lowercase, - only special char
        payload = {"value": data} # Json format
        # HTTP Post method to Adafruit IO
        response = wifi.post(
            "https://io.adafruit.com/api/v2/" #address to adafruit io
            + secrets["aio_username"] #input adafruit io name for "secret"
            + "/feeds/"
            + feed #feed = "test"
            + "/data",
            json=payload, # counter
            headers={"X-AIO-KEY": secrets["aio_key"]}, #input adafruit io key from "secret"
        )
        print(response.json()) #send data and print the data that you sent
        response.close() #close the connection
        print("OK")
        print(str(dht.temperature) + 'C') #print to serial to see if the senor is working

        print("Posting humidity...", end="") #Posting humidity to Adafruit.io
        data = humidity #counter result = input data
        feed = "humid-wizfi360" # Adafruit IO feed, the name on adafruit io needs to be lowercase, - only special char
        payload = {"value": data} # Json format
        # HTTP Post method to Adafruit IO
        response = wifi.post(
            "https://io.adafruit.com/api/v2/" #address to adafruit io
            + secrets["aio_username"] #input adafruit io name for "secret"
            + "/feeds/"
            + feed #feed = "test"
            + "/data",
            json=payload, # counter
            headers={"X-AIO-KEY": secrets["aio_key"]}, #input adafruit io key from "secret"
        )
        print(response.json()) #send data and print the data that you sent
        response.close() #close the connection
        print("OK")
        print(str(dht.humidity) +'%' )

    except (ValueError, RuntimeError, adafruit_espatcontrol.OKError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue
    response = None
    temp=str(temperature)
    humid=str(humidity)
    display.fill(0)
    display.text('Readings Posted', 10, 0, 1)
    display.text('Temperature: '+temp+' C', 10, 10, 1)
    display.text('Humidity: '+humid+'%', 10, 20, 1)
    display.show()
    led.value = True 	#Turn led on
    time.sleep(10)
    led.value = False 	#Turn led off
    time.sleep(5)
