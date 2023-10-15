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
import subprocess



conn= firebase.FirebaseApplication("https://smartwatermeter-cc7c4-default-rtdb.firebaseio.com/ ",None)

global rate_cnt,total_cnt
rate_cnt=0
total_cnt=0


GPIO.setmode(GPIO.BCM)
inpt=27
GPIO.setup(inpt,GPIO.IN)
time_new=0.0
rpt=1  
rate=0.0
r=0.0
vol=0.0
const= 0.004
RST = None     # on the PiOLED this pin isnt used
      # Note the following are only used with SPI:
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
draw.rectangle((0,0,width,height), outline=0, fill=0)
       
padding = -2
top = padding
bottom = height-padding
x = 0

font = ImageFont.truetype("Xerox Serif Wide.ttf",10)
font1= ImageFont.truetype("Minecraftia-Regular.ttf",7)

       
def pulse_cntr(inpt):
    global rate_cnt,total_cnt
    rate_cnt+=1
    total_cnt+=1

GPIO.add_event_detect(inpt,GPIO.FALLING,callback=pulse_cntr,bouncetime=10)

print("Press Control C to exit")

# time_cur=time.time()
time_loop=time.time()
       

while True:
#     time_cur=time.time()
   
    if time.time()>=time_loop+1:
       
        if rate_cnt!=0:
#             rate=((1/(time.time()-time_loop))*rate_cnt)/6.217
            rate=rate_cnt/6.25
            time_loop=time.time()
            r=(rate/60)
            vol=(vol+r)
            print("rate_cnt=%.2f"%rate_cnt)
            rate_cnt=0
            print("\nFlow Rate= %0.2f L/M" %rate)
            print("\nTotal Volume= %0.2f L"%vol)
                   
            draw.rectangle((0,0,width,height), outline=0, fill=0)


            disp.clear()
            disp.display()
                       
            draw.text((x, top+8),       " R :  " +str(round(rate,2)),  font=font, fill=255)
            draw.text((x+80, top+8),    "L / M",  font=font1, fill=255)
            draw.text((x, top+20),       " V :  " + str(round(vol,2)) ,  font=font, fill=255)
            draw.text((x+80, top+20),    "L",  font=font1, fill=255)
                       
            disp.image(image)
            disp.display()
            time.sleep(.1)
           
        else:
            rate=0.00
            print("\nFlow Rate= %0.2f L/M"%rate )
            print("\nTotal Volume= %0.2f L"%vol)
                   
            draw.rectangle((0,0,width,height), outline=0, fill=0)

            disp.clear()
            disp.display()
                       
            draw.text((x, top+8),       " R : 0.00 " ,  font=font, fill=255)
            draw.text((x+80, top+8),    "L / M",  font=font1, fill=255)
            draw.text((x, top+20),       " V :  " + str(round(vol,2)) ,  font=font, fill=255)
            draw.text((x+80, top+20),    "L",  font=font1, fill=255)
                     
            disp.image(image)
            disp.display()
            time.sleep(.1)
           
       
       
   
        try:
            None
        except KeyboardInterrupt:
            print("\nCTRL C - Exiting")
            GPIO.cleanup()  #clean up all the ports used
            sys.exit()
           
       
        conn.patch("/Sensor/" + str(datetime.now().strftime('%d-%m-%Y')), {"Rate":round(rate,2),"Volume":round(vol,2) })
