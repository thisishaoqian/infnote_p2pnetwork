import asyncio
import sys
import websockets
import json


class Client:
    def __init__(self, host, port):
        self.address='ws://' +host+':'+port

    def run_client(self):
        asyncio.get_event_loop().run_until_complete(self.__hello_client(self.address))
        asyncio.get_event_loop().run_forever()

    async def __hello_client(self, address):
            async with websockets.connect(
                    address) as websocket:
                greeting = await websocket.recv()
                print(f"< {greeting}")
                while 1:
                    name = input("Type:")
                    name = json.dumps({'type': name})
                    await websocket.send(name)
                    print(f"> {name}")

                    response = await websocket.recv()
                    print(f"< {response}")


peer = Client(sys.argv[1], sys.argv[2])
peer.run_client()
