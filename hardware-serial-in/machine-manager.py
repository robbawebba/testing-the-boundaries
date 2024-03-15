#!/usr/bin/env python3

import serial

# machine serial commands
STATE_COMMAND = "STATE"
PRICE_COMMAND = "PRICE"
VEND_COMMAND = "VEND"

def serial_encode(message: str) -> bytes:
    return "{:s}\n".format(message).encode('utf-8')

def serial_decode(message: bytes) -> list[str]:
    return message.decode('utf-8').strip()

# open serial port to machine
machine = serial.Serial("/dev/ttyS0", 115200, timeout=10)

while True:
    msg = input("[machine_manager]# ").lower()
    params = msg.split(" ")
    if len(msg) < 1:
        continue

    operation = params[0]
    if operation == "get_state":
        # request the current state of the machine
        machine.write(serial_encode(STATE_COMMAND))
        resp = serial_decode(machine.readline())
        print("current state:", resp)

    if operation == "get_price":
        # request the current price for the cycle
        machine.write(serial_encode(PRICE_COMMAND))
        resp = serial_decode(machine.readline())
        print("current price:", resp)

    if operation == "send_vend":
        # send dollar amount to machine to pay for the cycle
        if len(params) < 2:
            break
        command = "{:s} {:s}".format(VEND_COMMAND, params[1])
        machine.write(serial_encode(command))
        resp = serial_decode(machine.readline())
        if resp == "OK":
            print("VEND Successful")
        else:
            print("VEND Failed")
