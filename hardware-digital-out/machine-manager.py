#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO

pin_coin_out = 18

COIN_PULSE_LENGTH = 0.1 # seconds
COIN_PULSE_IDLE = GPIO.HIGH
COIN_PULSE_ACTIVE = GPIO.LOW

# setup GPIO output, default to IDLE state
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_coin_out, GPIO.OUT)
GPIO.output(pin_coin_out, COIN_PULSE_IDLE)

while True:
    try:
        cmdline = input("[machine_manager]#").split(" ")
    except KeyboardInterrupt:
        GPIO.cleanup()
        break

    if len(cmdline) < 2:
        continue
    operation = cmdline[0]
    if operation == "send_vend":
        if len(cmdline) < 2:
            continue
        try:
            num_quarters = int(cmdline[1]) / 25
            # send one pulse for each quarter to vend 
            while num_quarters > 0:
                GPIO.output(pin_coin_out, COIN_PULSE_ACTIVE)
                time.sleep(COIN_PULSE_LENGTH)
                GPIO.output(pin_coin_out, COIN_PULSE_IDLE)
                time.sleep(COIN_PULSE_LENGTH*2)
                num_quarters -= 1
        except:
            continue


