#!/usr/bin/env python3

import sys
sys.path.append("rp2daq")

import rp2daq
import time

machine_busy_out = 16 # Pico GP16

BUSY_ENABLE = 0
BUSY_DISABLE = 1

# connect to the RPi Pico DAQ
pico = rp2daq.Rp2daq()
pico.gpio_out(machine_busy_out, BUSY_DISABLE, high_z=1) # set pin to input to allow pin to be pulled up, simulating IDLE state

while True:
    print("Simulating BUSY state")
    pico.gpio_out(machine_busy_out, BUSY_ENABLE)  # set pin to output low to simulate BUSY state
    time.sleep(10)
    print("Simulating IDLE state")
    pico.gpio_out(machine_busy_out, BUSY_DISABLE, high_z=1) # set pin to input to allow pin to be pulled up, simulating IDLE state
    time.sleep(10)

