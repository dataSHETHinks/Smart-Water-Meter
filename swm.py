# Python program that measures the flow rate and total volume of water 
# using a flow sensor connected to a Raspberry Pi. The measured values 
# are then displayed on an OLED screen (Adafruit_SSD1306) and are also 
# sent to a Firebase Realtime Database.

# Libraries and Initializations:

# Import necessary libraries.
# Initialize GPIO pins, display, and other variables.
# Connect to Firebase database.
# Global Variables:

# rate_cnt and total_cnt track the number of pulses and the total count respectively.
# GPIO Setup:

# Set the GPIO mode.
# Define an input pin to listen to the flow sensor.
# Create an event to detect a falling edge (this is where the sensor sends a pulse indicating a certain volume of water has passed through).
# Display Setup:

# Set up the Adafruit OLED display, clear it, and set the dimensions.
# Define fonts and other display related constants.
# pulse_cntr Function:

# Callback function that increments the pulse count every time the sensor sends a pulse (i.e., when a falling edge is detected on the input pin).
# Main Loop:

# If there's a rate count detected, calculate the flow rate and volume.
# Update the OLED display with the flow rate and volume.
# If there's no flow, show 0 flow rate.
# The last action inside the loop sends the data to Firebase using the patch method. This updates the database with the flow rate and volume under the current date.      


import RPi.GPIO as GPIO
import time
import sys
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from firebase import firebase
from datetime import datetime

conn = firebase.FirebaseApplication("https://smartwatermeter-cc7c4-default-rtdb.firebaseio.com/", None)

global rate_cnt, total_cnt
rate_cnt = 0
total_cnt = 0

GPIO.setmode(GPIO.BCM)
inpt = 27
GPIO.setup(inpt, GPIO.IN)
rpt = 1
rate = 0.0
r = 0.0
vol = 0.0
const = 0.004

RST = None
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
disp.begin()
disp.clear()
disp.display()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

padding = -2
top = padding
bottom = height - padding
x = 0

font = ImageFont.truetype("Xerox Serif Wide.ttf", 10)
font1 = ImageFont.truetype("Minecraftia-Regular.ttf", 7)


def pulse_cntr(inpt_channel):
    global rate_cnt, total_cnt
    rate_cnt += 1
    total_cnt += 1


def update_display(rate, vol):
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    disp.clear()
    disp.display()

    draw.text((x, top+8), " R :  " + str(round(rate, 2)), font=font, fill=255)
    draw.text((x+80, top+8), "L / M", font=font1, fill=255)
    draw.text((x, top+20), " V :  " + str(round(vol, 2)), font=font, fill=255)
    draw.text((x+80, top+20), "L", font=font1, fill=255)

    disp.image(image)
    disp.display()
    time.sleep(.1)


GPIO.add_event_detect(inpt, GPIO.FALLING, callback=pulse_cntr, bouncetime=10)

print("Press Control C to exit")
time_loop = time.time()

try:
    while True:
        if time.time() >= time_loop + 1:
            if rate_cnt != 0:
                rate = rate_cnt / 6.25
                time_loop = time.time()
                r = (rate / 60)
                vol = (vol + r)
                rate_cnt = 0
            else:
                rate = 0.00
            update_display(rate, vol)
            conn.patch("/Sensor/" + str(datetime.now().strftime('%d-%m-%Y')), {"Rate": round(rate, 2), "Volume": round(vol, 2)})
except KeyboardInterrupt:
    print("\nCTRL C - Exiting")
finally:
    GPIO.cleanup()  # clean up all the ports used
