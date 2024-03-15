import asyncio
import json
from ipc import UnixClient, serve_unix

main_app_sock = "/tmp/main_app.server.sock"
main_app_client_sock = "/tmp/main_app.client.sock"
machine_manager_sock = "/tmp/machine_manager.server.sock"

class MainApp():
    paid_balance: int = 0
    machine_state: str = "IDLE"

    def add_payment(self, amount: int):
        self.paid_balance += amount

    def get_balance(self) -> int:
        return self.paid_balance

    def clear_balance(self):
        self.paid_balance = 0

    def get_machine_state(self)->str:
        return self.machine_state

    def set_machine_state(self, state: str)->str:
        self.machine_state = state

def message_handler(app: MainApp, client_address: str, message: str):
    print(f"Received from {client_address}: {message}")
    try:
        message_json = json.loads(message)
        command = message_json["command"]
        if command == "CARD_PAYMENT":
            amount = message_json["amount"]
            if amount <= 0:
                return '{"result": "FAIL"}\n'
            app.add_payment(amount)
            return '{"result": "SUCCESS"}\n'
        elif command == "MACHINE_STATE":
            state = message_json["state"]
            app.set_machine_state(state)
            return '{"result": "SUCCESS"}\n'

    except Exception as e:
        print(str(e))
        return json.dumps({"result": "FAIL"})

async def main():
    app = MainApp()
    serve_unix(main_app_sock, message_handler, app)
    machine_manager = UnixClient(machine_manager_sock)
    await machine_manager.connect()
    while True:
        payment_balance = app.get_balance()
        machine_state = app.get_machine_state()
        print(f"machine_state={machine_state} payment_balance={payment_balance}")

        if payment_balance > 0:
            # send recieved payment to machine_manager if it is IDLE 
            if machine_state == "RUNNING":
                print(f'Cannot send payment to machine when RUNNING')
            else:
                print(f"Sending payment of {payment_balance} cents to machine")
                await machine_manager.write(json.dumps({"command":"SEND_VEND", "amount": payment_balance}))

            # clear pending payments after sending vend
            app.clear_balance()

        await asyncio.sleep(1)


asyncio.run(main())

