#!/usr/bin/python

#written by Shimanto on May 7 at Seager Wheeler

#if you press c -> the sensors takes data against the calibration material
#if you press d -> the sensors takes data against the sample
#if you press e -> the program stops
#for keyboard interrupt press Ctrl+c
#run from the terminal, doesn't work from the Thonny or other IDE (more specifically the fucntion getch doesn't work)
#don't forget to turn on RPi i2c from Start>Preferences>Raspberry Pi Configuration>Interfaces
#from terminal use python3 (not just python)


from time import sleep
from Adafruit_GPIO import I2C
import time
import sys,tty,termios
import AS7262_Pi as Spec
import os
import numpy as np
from picamera import PiCamera

import RPi.GPIO as GPIO

#the OLED
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#define the LEDPin connected with MOSFET
LEDPin = 4; 
# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()


GPIO.setmode(GPIO.BCM)
GPIO.setup(LEDPin, GPIO.OUT)
camera = PiCamera()

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd,termios.TCSADRAIN,old_settings)
        return ch
    

def tca_select(channel):
    if channel > 7:
        return
    tca.writeRaw8(1<<channel)

#in case I want to activate two channels with two different physical i2c address at the same time
def tca_set(mask):
    if mask > 0xff:
        return
    tca.writeRaw8(mask)

def specInit(specName, gain = 3, intTime = 50,measurementMode=2):
    #visible is connected with channel 0
    if(specName == 'VIS'):
        specNum = 0;
    elif(specName == 'NIR'):
        specNum =1;
    else:
        print('Invalid Keyword')


    tca_select(specNum)
    #Reboot the spectrometer, just in case
    Spec.soft_reset()

    #Set the gain of the device between 0 and 3.  Higher gain = higher readings
    Spec.set_gain(gain)

    #Set the integration time between 1 and 255.  Higher means longer readings
    Spec.set_integration_time(intTime)

    #Set the board to continuously measure all colours
    Spec.set_measurement_mode(measurementMode)

#get the mux ready; address of the mux = 0x70
tca = I2C.get_i2c_device(address = 0x70)

specInit(specName='VIS')
specInit(specName='NIR')

i =0;
j=0;
k = 0;
l = 0;

count = 0
print("All reset - Successful")


draw.rectangle((0,0,width,height), outline=0, fill=0)

            
# Write two lines of text.

draw.text((x, top),       "Welcome",  font=font, fill=255)

# Display image.
disp.image(image)
disp.display()


while True:
    
    try:
        #delay for 30s
        sleep(15)
        sleep(15)

            
        draw.rectangle((0,0,width,height), outline=0, fill=0)         
        # Write two lines of text.
        draw.text((x, top),       "Started Taking Data",  font=font, fill=255)
        
        # Display image.
        disp.image(image)
        disp.display()
        
        #visible is connected with channel 0
        specInit(specName='VIS')
        #Turn on the main LED
        Spec.enable_main_led()
        print("taking visible spectrum " + str(k))
        count = 0
        #Do this until the script is stopped:
        while True:
                #Store the list of readings in the variable "results"
                results = Spec.get_calibrated_values()
                
                #skip first 10 readings
                count = count + 1
                if (count<10):
                    continue

                reporttime = (time.strftime("%H:%M:%S"))
                csvresult = open("/home/pi/Desktop/habib_vai_Redefined/data/vis_"+ str(k)+".csv","a")
                csvresult.write(str(results[5])+ "," + str(results[4])+ "," + str(results[3])+ "," + str(results[2])+ "," +str(results[1])+ "," + str(results[0])+ "," +reporttime + "\n")
                csvresult.close
                
                if(count>=30):
                    #Set the board to measure just once (it stops after that)
                    Spec.set_measurement_mode(3)
                    #Turn off the main LED
                    Spec.disable_main_led()
                    #Notify the user
                    print("Visible Spectrum Done")
                    
                    draw.rectangle((0,0,width,height), outline=0, fill=0)
                    
                    # Write two lines of text.

                    draw.text((x, top),       "Visible Spectrum Done",  font=font, fill=255)
                    
                    # Display image.
                    disp.image(image)
                    disp.display()
                    
                    break;
    
        #NIR is connected with channel 1
        specInit(specName='NIR')
        
        #Turn on the main LED
        Spec.enable_main_led()
        print("taking NIR spectrum " + str(k))
        count = 0
        #Do this until the script is stopped:
        while True:
                #Store the list of readings in the variable "results"
                results = Spec.get_calibrated_values()
                
                #skip first 15 readings
                count = count + 1
                if (count<10):
                    continue
                
                reporttime = (time.strftime("%H:%M:%S"))
                csvresult = open("/home/pi/Desktop/habib_vai_Redefined/data/nir_"+ str(k)+".csv","a")
                csvresult.write(str(results[5])+ "," + str(results[4])+ "," + str(results[3])+ "," + str(results[2])+ "," +str(results[1])+ "," + str(results[0])+ "," +reporttime + "\n")
                csvresult.close
                
                if(count>=30):
                    #Set the board to measure just once (it stops after that)
                    Spec.set_measurement_mode(3)
                    #Turn off the main LED
                    Spec.disable_main_led()
                    #Notify the user
                    print("NIR Spectrum Done")
                    
                    draw.rectangle((0,0,width,height), outline=0, fill=0)


                    # Write two lines of text.

                    draw.text((x, top+8),     'NIR Spectrum Done', font=font, fill=255)
                    sleep(3)
                    
                    # Display image.
                    disp.image(image)
                    disp.display()
                    
                    
                    break;
        #k = k+1
        print('**Data Taken for set ' + str(k) +'**')
        
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        # Write two lines of text.
        draw.text((x, top+16),       "Data taken - " + str(k),  font=font, fill=255)
        # Display image.
        disp.image(image)
        disp.display()

        #take blank image and display
        camera.capture('/home/pi/Desktop/habib_vai_Redefined/'+str(k)+'_blank.jpg')

        draw.rectangle((0,0,width,height), outline=0, fill=0)
        # Write two lines of text.
        draw.text((x, top+16),       "Blank Image - " + str(k),  font=font, fill=255)
        # Display image.
        disp.image(image)
        disp.display()
        
        #turn on LED, Take Image and display
        GPIO.output(LEDPin,1)
        camera.capture('/home/pi/Desktop/habib_vai_Redefined/'+str(k)+'_excited.jpg')
        sleep(5)
        GPIO.output(LEDPin,0)

        draw.rectangle((0,0,width,height), outline=0, fill=0)
        # Write two lines of text.
        draw.text((x, top+16),       "Excited Image - " + str(k),  font=font, fill=255)
        # Display image.
        disp.image(image)
        disp.display()

        k = k+1
                
        
    except KeyboardInterrupt:
        tca_select(0)
        Spec.disable_main_led()
        tca_select(1)
        Spec.disable_main_led()
        print("program interrupted")
        break

