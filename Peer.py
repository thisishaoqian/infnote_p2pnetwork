import asyncio
import signal
import websockets
import logging
from uuid import uuid4
import _thread

from PeerConnection import PeerConnection
from Services.services import *
from Services.events import *

logging.basicConfig()


class Peer:

    # Beginning of Constructor
    def __init__(self, server_port=None, max_peers=None, my_id=None, server_host=None,
                 protocol_version=None, client_version=None):
        self.debug = True
        self.shutdown = False
        self.server_socket = None
        self.peer_to_discover = None

        # If not supplied, the server_port variable will be set up to 4242, will be define to be unique in the future
        if server_port:
            self.server_port = int(server_port)
        else:
            self.server_port = 4242

        # If not supplied, the protocol version variable will be set up to '1.0.0'
        if protocol_version:
            self.protocol_version = protocol_version
        else:
            self.protocol_version = "1.0.0"

        if client_version:
            self.client_version = client_version
        else:
            self.client_version = "Full-Node"
        # If not supplied, the max_peers variable will be set up to 0
        # 0 value means unlimited peers
        if max_peers:
            self.max_peers = int(max_peers)
        else:
            self.max_peers = 0

        # If not supplied, the host name/IP address will be determined by attempting to connect to a random host.
        if server_host:
            self.server_host = server_host
        else:
            self.__init_server_host()

        # If not supplied, the id' peer will be defined with unique identifier thanks to uuid
        if my_id:
            self.my_id = my_id
        else:
            self.__init_node_id()

        # Hash Table of connected peers
        self.peers = set()

        # List of peers address
        self.peers_addr = set()

        # Handlers initialisation, basically the type of message accepted associated to the functions
        self.__init_handlers()

    # End of Constructor

    def __init_handlers(self):
        self.handlers = {}
        self.handlers = {
            'HELLO': self.notify_handshaking,
            'GET_STATUS': self.notify_status,
            'GET_ADDR': self.notify_addr_broadcast
        }

    def __init_node_id(self):
        self.my_id = str(uuid4()).replace('-', '')

    def __init_server_socket(self):
        self.__debug('Server started: %s (%s:%d)'
                     % (self.my_id, self.server_host, self.server_port))
        self.__debug('handlers size %s' % len(self.handlers))
        self.server_socket = websockets.serve(self.__consumer_handler, self.server_host, self.server_port)

    def __init_server_host(self):
        self.server_host = get_local_ip()

    def get_peers(self):
        return self.peers

    def add_node_discovery(self, entry):
        self.peer_to_discover = entry

    def __debug(self, msg):
        if self.debug:
            thread_debug(msg)

    async def notify_handshaking(self, websocket, data):
        if self.peers:
            message = handshaking_event(self.protocol_version, self.client_version, self.server_port, self.my_id)
            self.__debug("Notify Handshaking")
            await websocket.send(message)

    async def notify_addr_broadcast(self, websocket, data):
        if self.peers:
            message = addr_event(self.server_host, self.server_port)
            await asyncio.wait([peer.send(message) for peer in self.peers])

    async def notify_status(self, websocket, data):
        if self.peers:
            message = status_event()
            await websocket.send(message)

    async def notify_ping(self, websocket, data):
        pong_waiter = await websocket.ping()
        await pong_waiter

    async def notify_pong(self, websocket, data):
        await websocket.pong()

    def register_node(self, websocket):
        self.peers.add(websocket)

    def unregister_node(self, websocket):
        self.peers.remove(websocket)

    async def consumer(self, message, websocket):
        msg_type = None
        try:
            data = json.loads(message)
            print(data)
            if 'type' in data:
                if data['type']:
                    msg_type = data['type'].upper()
                if msg_type not in self.handlers:
                    logging.error(
                        "unsupported event: {}", data)
                else:
                    self.__debug('Handling peer msg: %s: %s' % (msg_type, data))
                    await self.handlers[msg_type](websocket, data)
            else:
                self.__debug("Need a 'type' key in every json message")
        except ValueError:
            self.__debug("Message need to respect Json Format")

    async def __consumer_handler(self, websocket, path):
        self.register_node(websocket)
        self.__debug('Consumer Handler !')
        try:
            async for message in websocket:
                await self.consumer(message, websocket)
        finally:
            self.unregister_node(websocket)

    '''async def __producer_handler(self, websocket, path):
        self.__debug("Producer Handler !")

        while True:
            message = handshaking_event(self.protocol_version, self.client_version, self.server_port, self.my_id)
            await websocket.send(self.my_id)

    async def handler(self, websocket, path):
        await self.register_node(websocket)
        self.__debug('path: %s, peers_number: %s' % (path, len(self.peers)))
        self.__debug('Current Server Listening: %s (%s:%d)'
                     % (self.my_id, self.server_host, self.server_port))
        self.__debug('Listening for Connections on the open socket...')

        try:
            # Implement logic here.

            consumer_task = asyncio.ensure_future(
                self.__consumer_handler(websocket, path))
            producer_task = asyncio.ensure_future(
                self.__producer_handler(websocket, path))
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_EXCEPTION,
            )
            for task in pending:
                task.cancel()
        finally:
            # Unregister.
            self.unregister_node(websocket)'''

    async def connect_and_send(self, ip_port_peer):
        ip_port_peer = str(ip_port_peer)
        async with websockets.connect('ws://'+ip_port_peer) as websocket:
            host, port = websocket.remote_address
            connected_peer = PeerConnection(None, host, port, websocket)
            message = json.dumps({'type': "Hello"})
            await connected_peer.send_data_json(message)
            await connected_peer.rcv_data_json()
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

    def peers_discovery(self):
        # This function will try different peer discovery methods
        self.__debug('Peer Discovery')
        if self.peer_to_discover is not None:
            self.peers_addr.add(self.peer_to_discover)
        self.__debug('List of current peer to connect to:')
        print(self.peers_addr)

    def run_server(self):
        self.__debug("Run Server !")
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.__init_server_socket()
        asyncio.get_event_loop().run_until_complete(self.server_socket)
        asyncio.get_event_loop().run_forever()

    def run_client(self, ip_port_peer):
        self.__debug("Run Client !")
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(self.connect_and_send(ip_port_peer))
        self.__debug("Loop Connect and Send over")

    def run_peer(self):
        self.__debug('Peer Running...')
        # This restores the default Ctrl+C signal handler, which just kills the process
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        _thread.start_new_thread(self.run_server, ())
        self.peers_discovery()
        if len(self.peers_addr):
            _thread.start_new_thread(self.run_client, (list(self.peers_addr)[0], ))
        while self.shutdown is False:
            pass
