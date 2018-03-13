import serial
import time
import requests
import json
from datetime import datetime
import time
import Adafruit_CharLCD as LCD
# Raspberry Pi pin setup
lcd_rs = 25
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 18
lcd_d7 = 22
lcd_backlight = 2
# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows = 2
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)


firebase_url = 'https://smart-garbage-scorpion.firebaseio.com/'
locations=['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3','/dev/ttyACM4', '/dev/ttyACM5','/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3', '/dev/ttyUSB4', '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7', '/dev/ttyUSB8', '/dev/ttyUSB9', '/dev/ttyUSB10', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9', 'com10', 'com11', 'com12', 'com13', 'com14', 'com15', 'com16', 'com17', 'com18', 'com19', 'com20', 'com21', 'com1', 'end']

def write_to_firebase(data, category, table):
    firebase_url = 'https://smart-garbage-scorpion.firebaseio.com/'
    try:
         result=requests.put(firebase_url + '/' + category + '/' + table + '.json' , data=json.dumps(data))
#         print ('Record inserted. Result Code = ' + str(result.status_code) + ',' + result.text)
    except IOError:
        pass

for device in locations:
    try:
        print "Trying...",device
        ser = serial.Serial(device, 9600, timeout = 0)
        break
    except:
        print "Failed to connect on",device
        if device == 'end':
            print "Unable to find Serial Port, Please plug in cable or check cable connections."
            exit()
time.sleep(2)

# ser = serial.Serial('/dev/ttyACM0',9600)
print "running..."
lcd.message('     Hello !')

while True:
    #take input from arduino
    read_serial=(ser.readline().strip())
    if len(read_serial)<1:
        continue
    
    inArg=read_serial
    try:
        key = int(inArg[0])
    except:
        continue
   
    if key==2: #air quality
        if float(inArg[2:])>1000:
            print inArg[2:]
            write_to_firebase({'bin01':inArg[2:]},'Alerts','AirQuality')
            lcd.clear()
            lcd.message('Beware ! Air Polluted ')
            
    elif key==3: #temperature
        if float(inArg[2:])>100:
            write_to_firebase({'bin01':1},'Alerts','OverHeated')
            
    elif key==5:  #customer
        ser.readline()
        ser.readline()
        lcd.clear()
        lcd.message('Hello Michael \nNice to See You! ')
        customerID=inArg[2:]
        while True:
            #reading weight
            read_serial=(ser.readline().strip())
            if len(read_serial)<1 :
                continue
            try:
                key=int(read_serial[0])
            except:
                continue
            if key==0:
                start_weight=float(read_serial[2:])
                break

        time.sleep(10)
        lcd.clear()
        lcd.message('     Hello !')
        while True:
            #reading weight
            read_serial=(ser.readline().strip())
            if len(read_serial)<1:
                continue
            try:
                key=int(read_serial[0])
            except:
                continue
            if key==0:
                end_weight=float(read_serial[2:])
                break
            
        while True:
            #reading distance (in cm)
            read_serial=(ser.readline().strip())
            if len(read_serial)<1:
                continue
            try:
                key=int(read_serial[0])
            except:
                continue
            if key==1:
                end_distance=float(read_serial[2:])
                if end_distance<10:
                    write_to_firebase({'full':1} , 'dustbin', 'bin01')
                    lcd.clear()
                    lcd.message('Bin is Full !')
                break
            
        write_to_firebase({'garbage': end_weight - start_weight} , 'customer', 'cust01')

    elif key==6:  #collector
        ser.readline()
        ser.readline()
        lcd.clear()
        lcd.message('Great. You \ncan clean me up')
        collectorID=inArg[2:]
        a=str(datetime.now())
        write_to_firebase({'full':0} , 'dustbin', 'bin01')
        write_to_firebase({'bin01': a[:16] } , 'collector', 'col01')
        time.sleep(3)
        lcd.clear()
        lcd.message('Thank you \nfor cleaning me ')
        time.sleep(2)
        lcd.clear()
        lcd.message('     Hello ! ')
        



