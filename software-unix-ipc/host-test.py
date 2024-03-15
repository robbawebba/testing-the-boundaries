#!/usr/bin/env python3

import sys
import time
import socket
from datetime import timedelta
import json

sys.path.append("rp2daq")

import rp2daq

machine_coin_in = 17 # Pico GP17
machine_busy_out = 16 # Pico GP16

# output states for simulating machine state
BUSY_ENABLE = 0
BUSY_DISABLE = 1

# falling and rising edge events from DAQ
COIN_PULSE_START_EVT = 4
COIN_PULSE_END_EVT = 8

# coin counting vars
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

def set_machine_state(pico: rp2daq.Rp2daq, state: int):
    if state == BUSY_DISABLE:
        # set pin high-impedance to allow pin to be pulled up, simulating IDLE state
        pico.gpio_out(machine_busy_out, BUSY_DISABLE, high_z=1)
    elif state == BUSY_ENABLE:
        # set pin to output low to simulate BUSY state
        pico.gpio_out(machine_busy_out, BUSY_ENABLE)

def test_credit_card_payment(pico, socket: socket.socket):
    # send $2.00 payment to device
    payment_cents = 200
    expected_coins = 8
    command = json.dumps({"command":"CARD_PAYMENT", "amount":payment_cents})
    socket.send((command+"\n").encode())
    resp = socket.recv(100)
    resp_json = json.loads(resp)
    if resp_json["result"] == "SUCCESS":
        print("CARD_PAYMENT command successful")
    else:
        print("CARD_PAYMENT command failed")
        return

    # confirm device sends $2.00 worth of coin pulses to machine
    print("waiting for coin pulses...")
    timeout = expected_coins / 2
    time.sleep(timeout)

    if coin_count != expected_coins:
        print(f"Unexpected number of coins detected. expected={expected_coins} actual={coin_count}")
        return
    
    print("All coins received! Test passed")


def test_payments_while_running(pico, socket: socket.socket):
    # set machine state to RUNNING
    set_machine_state(pico, BUSY_ENABLE)
    time.sleep(1)
    # send $2.00 payment to device
    command = json.dumps({"command":"CARD_PAYMENT", "amount":200})
    socket.send((command+"\n").encode())
    resp = socket.recv(100)
    resp_json = json.loads(resp)
    if resp_json["result"] == "SUCCESS":
        print("CARD_PAYMENT command successful")
    else:
        print("CARD_PAYMENT command failed")
        return

    # confirm device sends no coin pulses to machine
    print("waiting for coin pulses...")
    timeout = 5
    time.sleep(timeout)

    if coin_count > 0:
        print(f"Unexpected number of coins detected. expected=0 actual={coin_count}")
        return
    
    print("No coins received! Test passed")

# connect to the RPi Pico DAQ
pico = rp2daq.Rp2daq()
pico.gpio_on_change(machine_coin_in, on_rising_edge=1, on_falling_edge=1,  _callback=coin_event_callback)
set_machine_state(pico, BUSY_DISABLE)

# connect to UNIX Socket proxy on target device
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("192.168.1.217", 5000))

print("Test 1: Credit Card payment results in coin pulses sent to machine")
test_credit_card_payment(pico, sock)
coin_count = 0 

# Second test: credit card payment when machine is already running should result in 0 coin pulses
print("Test 2: Credit Card payment while machine is RUNNING results in 0 coin pulses sent to machine")
test_payments_while_running(pico, sock)

set_machine_state(pico, BUSY_DISABLE)
