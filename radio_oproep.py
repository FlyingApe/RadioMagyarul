import os
import time
import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

from threading import Barrier
import radio 
import phatbeat
import subprocess

import socket
import threading 

i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, 16, 2)

global radio
radio = radio.Radio(lcd)
radio.play()

os.system("ping -c 1 google.com")
time.sleep(5)

def lcd_buttonthread():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        if lcd.select_button:
            try:
                s.connect(('10.255.255.255', 1))
                IP = s.getsockname()[0]
            except:
                IP = '127.0.0.1'
            finally:
                s.close()
            lcd.clear()
            lcd.message = IP
        if lcd.left_button:
            lcd.clear()
            os.system("shutdown now")
        time.sleep(7)

button_thread = threading.Thread(target=lcd_buttonthread)
button_thread.start()

global end_barrier
end_barrier = Barrier(2)

@phatbeat.on(phatbeat.BTN_PLAYPAUSE)
def playpause(pin):
    global radio
    print("pause")
    radio.toggle_playing()

@phatbeat.on(phatbeat.BTN_FASTFWD)
def nextstation(pin):
    global radio
    print("next")
    radio.next_station()

@phatbeat.on(phatbeat.BTN_REWIND)
def prevstation(pin):
    global radio
    print("previous")
    radio.previous_station()

@phatbeat.on(phatbeat.BTN_VOLUP)
def volumeup(pin):
    s = subprocess.run("amixer sset Master playback 5%+", shell=True)

@phatbeat.on(phatbeat.BTN_VOLDN)
def volumeup(pin):
    s = subprocess.run("amixer sset Master playback 5%-", shell=True)

end_barrier.wait()

radio.close()


