#!/usr/bin/env python3

import sys
sys.path.append("rp2daq")

import rp2daq
import time
from datetime import timedelta

machine_coin_in = 17 # Pico GP17

# falling and rising edge events from DAQ
COIN_PULSE_START_EVT = 4
COIN_PULSE_END_EVT = 8

# connect to the RPi Pico DAQ
pico = rp2daq.Rp2daq()

coin_pulse_start_time = 0
coin_count = 0

def coin_event_callback(**kwargs):
    global coin_pulse_start_time, coin_count
    if kwargs["events"] == COIN_PULSE_START_EVT:
        coin_pulse_start_time = kwargs["time_us"]
    elif kwargs["events"] == COIN_PULSE_END_EVT and coin_pulse_start_time > 0:
        coin_count += 1
        duration_us = kwargs["time_us"] - coin_pulse_start_time
        print("New coin detected! duration={:.2f}ms count={:d}".format(duration_us/1000, coin_count))
        coin_pulse_start_time = 0

pico.gpio_on_change(machine_coin_in, on_rising_edge=1, on_falling_edge=1,  _callback=coin_event_callback)

print("waiting for coin pulses...")
while True:
    pass