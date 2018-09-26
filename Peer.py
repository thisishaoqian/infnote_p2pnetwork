import asyncio
import websockets
import json
import logging
from uuid import uuid4

from Services.services import *
from Services.events import *

logging.basicConfig()


class Peer:

    # Beginning of Constructor
    def __init__(self, server_port, max_peers=None, my_id=None, server_host=None):
        self.debug = True
        self.server_port = int(server_port)
        self.protocol_version = "1.0.0"
        self.client_version = "Full-Node"

        # If not supplied, the max_peers variable will be set up to 0
        # 0 value means unlimited peers
        if max_peers:
            self.max_peers = int(max_peers)
        else:
            self.max_peers = 0

        # If not supplied, the host name/IP address will be determined
        # by attempting to connect to a random host.
        if server_host:
            self.server_host = server_host
        else:
            self.__init_server_host()

        # If not supplied, the id' peer will be defined with unique identifier thanks to uuid
        if my_id:
            self.my_id = my_id
        else:
            self.__init_node_id()

        # Hash Table of known/connected peers, in the future manage by an address manager
        self.peers = set()

    # End of Constructor

    def __init_node_id(self):
        self.my_id = str(uuid4()).replace('-', '')

    def __init_server_host(self):
        self.server_host = get_ip()

    def __debug(self, msg):
        if self.debug:
            thread_debug(msg)

    async def notify_handshaking(self):
        if self.peers:
            message = handshaking_event(self.protocol_version, self.client_version, self.server_port, self.my_id)
            await asyncio.wait([peer.send(message) for peer in self.peers])

    async def notify_status(self):
        if self.peers:
            message = status_event()
            await asyncio.wait([peer.send(message) for peer in self.peers])

    async def notify_ping(self):
        if self.peers:
            message = ping_event()
            await asyncio.wait([peer.send(message) for peer in self.peers])

    async def register_node(self, websocket):
        self.peers.add(websocket)
        await websocket.send(handshaking_event(self.protocol_version, self.client_version, self.server_port, self.my_id))

    def unregister_node(self, websocket):
        self.peers.remove(websocket)

    async def __loop_server(self, websocket, path):
        await self.register_node(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                if data['type'] == 'Hello':
                    self.__debug("Receive a Hello, Handshaking in process")
                    await self.notify_status()
                elif data['type'] == 'Status':
                    self.__debug("Receive a Status, Connection is now established")
                    await self.notify_ping()
                elif data['type'] == 'Pong':
                    self.__debug("Receive a pong")
                else:
                     logging.error(
                        "unsupported event: {}", data)
        finally:
            self.unregister_node(websocket)

    def run_server(self):

        start_server = websockets.serve(self.__loop_server, self.server_host, self.server_port)
        asyncio.get_event_loop().run_until_complete(start_server)
        self.__debug('Server started: %s (%s:%d)'
                     % (self.my_id, self.server_host, self.server_port))
        self.__debug('Listening for Connections...')
        asyncio.get_event_loop().run_forever()


    async def __hello_server(self, websocket, path):
        name = await websocket.recv()
        print(f"< {name}")

        greeting = f"Hello {name}!"

        await websocket.send(greeting)
        print(f"> {greeting}")


peer = Peer(8080, 5)
peer.run_server()
