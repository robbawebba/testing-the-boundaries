import asyncio
import json
import socket
import os

class UnixClient():
    reader: asyncio.StreamReader = None
    writer: asyncio.StreamWriter = None
    
    def __init__(self, server_address, client_address=None):
        self.sock = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
        if client_address:
            self.sock.bind(client_address)
        self.server_address = server_address
        self.client_address = client_address
    
    async def connect(self):
        self.sock.connect(self.server_address)
        (r, w) = await asyncio.open_unix_connection(sock=self.sock)
        self.reader = r
        self.writer = w
        print(f'Client connected to {self.server_address}')
    
    async def write(self, message: str):
        if self.is_closed():
            return
        data = f"{message}\n".encode('utf-8')
        self.writer.write(data)
        await self.writer.drain()

        resp = await self.reader.readline()
        resp_json = json.loads(resp)
        if resp_json["result"] != "SUCCESS":
            print(f"Command to {self.server_address} failed")
    
    async def close(self):
        if self.is_closed():
            return
        self.writer.close()
        await self.writer.wait_closed()

    def is_closed(self):
        if self.writer == None:
            return True
        return self.writer.is_closing()

def serve_unix(socket_address, handler, user_data):
    async def conn_handler(reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"New connection from {addr}")
        while True:
            data = await reader.readline()
            if not data:
                break

            message = data.decode().strip()
            resp = handler(user_data, addr, message)
            if resp != None:
                writer.write(resp.encode())
                await writer.drain()

    server = asyncio.start_unix_server(conn_handler, socket_address)
    asyncio.get_event_loop().create_task(server)
    print(f'Serving on {socket_address}')