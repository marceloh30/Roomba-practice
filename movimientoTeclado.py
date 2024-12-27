#!/usr/bin/env python3
#-*-coding:utf-8-*-
##############################################
# The MIT License (MIT)
# Copyright (c) 2017 Kevin Walchko
# see LICENSE for full details
##############################################
# moves the roomba through a simple sequence

import pycreate2
import time
import math
from pynput import keyboard
from pynput.keyboard import Key
Rx2=72
nCe=508.8
FACTOR_CONVERSION = Rx2*math.pi/nCe
global distancia

if __name__ == "__main__":
    # Create a Create2 Bot
    port = 'COM5'
    baud = {
        'default': 115200,
        'alt': 19200  # shouldn't need this unless you accidentally set it to this
    }

    bot = pycreate2.Create2(port=port, baud=baud['default'])
    bot.start()
    bot.safe()

def on_key_press(key):
    
    sensores = bot.get_sensors()
    distancia = sensores.distance

    if key == Key.right:
        print("Right key clicked")
        bot.drive_direct(0, 200)

    elif key == Key.left:
        print("Left key clicked")
        bot.drive_direct(200,0)
    elif key == Key.up:
        print("Up key clicked")
        bot.drive_direct(200, 200)
    elif key == Key.down:
        print("Down key clicked")
        bot.drive_direct(-200, -200)
    elif key == Key.esc:
        listener.stop()
        print("Adios!")
        bot.drive_stop()
    elif key==Key.f3:
        bot.drive_stop()
    else:
        bot.drive_stop()

def on_key_release(key):
    distancia=0
    sensores = bot.get_sensors()
    distancia = distancia+sensores.distance
    print("Distancia (on key release):",sensores.distance)
    print("Distancia total:", distancia)

    bot.drive_stop()



with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
    listener.join()

    
    
  
