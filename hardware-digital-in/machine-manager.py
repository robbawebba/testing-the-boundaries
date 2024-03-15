#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO

pin_machine_busy = 16

MACHINE_IDLE = 1
MACHINE_BUSY = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_machine_busy, GPIO.IN)

machine_state = -1

while True:
    new = GPIO.input(pin_machine_busy)
    if new != machine_state:
        print("Machine State changed to {:s}".format(
            "BUSY" if new == MACHINE_BUSY else "IDLE")
        )
        machine_state = new

    time.sleep(0.2)

