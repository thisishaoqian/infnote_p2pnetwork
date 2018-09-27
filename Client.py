import asyncio
import sys
import websockets
import json


class Client:
    def __init__(self, host, port):
        self.address='ws://' +host+':'+port

    def run_client(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__hello_client(self.address, loop))
        loop.close()

    async def __hello_client(self, address, loop):
            async with websockets.connect(
                    address) as websocket:
                greeting = await websocket.recv()
                print(f"< {greeting}")
                try:
                    while 1:
                        name = input("Type:")
                        name = json.dumps({'type': name})
                        await websocket.send(name)
                        print(f"> {name}")

                        response = await websocket.recv()
                        print(f"< {response}")
                except KeyboardInterrupt:
                    exit(0)


peer = Client(sys.argv[1], sys.argv[2])
peer.run_client()
