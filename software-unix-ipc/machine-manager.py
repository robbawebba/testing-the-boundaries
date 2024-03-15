#!/usr/bin/env python3
import asyncio
import time
import json
import os
import RPi.GPIO as GPIO
from ipc import UnixClient, serve_unix

machine_manager_sock = "/tmp/machine_manager.server.sock"
machine_manager_client_sock = "/tmp/machine_manager.client.sock"
main_app_sock = "/tmp/main_app.server.sock"

pin_coin_out = 18
pin_machine_busy = 16

COIN_PULSE_LENGTH = 0.1 # seconds
COIN_PULSE_IDLE = GPIO.HIGH
COIN_PULSE_ACTIVE = GPIO.LOW


MACHINE_IDLE = 1
MACHINE_BUSY = 0


def gpio_setup():
    # setup GPIO output to send coins, default to IDLE state
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_coin_out, GPIO.OUT)
    GPIO.output(pin_coin_out, COIN_PULSE_IDLE)

    # setup GPIO input to detect machine state
    GPIO.setup(pin_machine_busy, GPIO.IN)


def send_coin_pulses(amount: int):
    num_quarters = amount / 25
    # send one pulse for each quarter to vend 
    while num_quarters > 0:
        GPIO.output(pin_coin_out, COIN_PULSE_ACTIVE)
        time.sleep(COIN_PULSE_LENGTH)
        GPIO.output(pin_coin_out, COIN_PULSE_IDLE)
        time.sleep(COIN_PULSE_LENGTH*2)
        num_quarters -= 1

async def monitor_machine_state(mainapp: UnixClient):
    machine_state = -1
    while True:
        try:
            # connect to the mainapp when the connection is closed
            if mainapp.is_closed():
                await mainapp.connect()
        except:
           pass

        # check the busy GPIO for state changes
        new = GPIO.input(pin_machine_busy)
        if new != machine_state:
            state_str = "RUNNING" if new == MACHINE_BUSY else "IDLE"
            machine_state = new
            print(f"Machine State changed to {state_str}")
            # send machine state changes to the MainApp 
            await mainapp.write(json.dumps({"command":"MACHINE_STATE", "state":state_str}))

        await asyncio.sleep(1)

def message_handler(user_data, client_address, message):
    print(f"Received message from client {client_address}: {message}")
    message_json = json.loads(message)
    command = message_json["command"]
    if command == "SEND_VEND":
        amount = message_json["amount"]
        if amount <= 0:
            return '{"result": "FAIL"}\n'
        send_coin_pulses(amount)
        return '{"result": "SUCCESS"}\n'    

def main():
    eventloop = asyncio.new_event_loop()
    asyncio.set_event_loop(eventloop)
    gpio_setup()
    serve_unix(machine_manager_sock, message_handler, None)
    mainapp_client = UnixClient(main_app_sock, machine_manager_client_sock)
    eventloop.create_task(monitor_machine_state(mainapp_client))
    tasks = asyncio.gather(*asyncio.all_tasks(eventloop))
    try:
        eventloop.run_until_complete(tasks)
    except KeyboardInterrupt as e:
        tasks.cancel()
        eventloop.run_until_complete(tasks)
    finally:
        eventloop.close()
        GPIO.cleanup()
        os.unlink(machine_manager_client_sock)

main()
