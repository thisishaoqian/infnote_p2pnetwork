import asyncio
import json
import socket

import websockets
import logging
from uuid import uuid4

from PeerConnection import PeerConnection
from Services import services
import Actions
import Protocol
from AddressManager import AddressManager

logging.basicConfig()


class Peer:

    # Beginning of Constructor
    def __init__(self, app, server_port=None, max_peers=None, my_id=None, server_host=None, client_version=None,
                 protocol_version=None):
        self.app = app
        self.debug = True
        self.shutdown = False
        self.server_socket = None
        self.addr_manager = AddressManager()

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
        self.peers_co = set()

        # Handlers initialisation, basically the type of message accepted associated to the functions
        self.__init_handlers()

    # End of Constructor

    def __init_handlers(self):
        self.handlers = {}
        self.handlers = {
            'PING': self.notify_ping,
            'HELLO': self.consume_hello,
            'STATUS': self.consume_status,
            'GET_ADDR': self.consume_get_addr
        }

    def __init_node_id(self):
        self.my_id = str(uuid4()).replace('-', '')

    def __init_server_socket(self):
        self.__debug('Server started: %s (%s:%d)'
                     % (self.my_id, self.server_host, self.server_port))
        self.__debug('handlers size %s' % len(self.handlers))
        self.server_socket = websockets.serve(self.__consumer_handler, self.server_host, self.server_port)

    def __init_server_host(self):
        self.server_host = services.get_local_ip()

    def get_peers(self):
        return self.peers_co

    def __debug(self, msg):
        if self.debug:
            services.thread_debug(msg)

    async def consume_hello(self, connected_peer, data):
        print("Consume Hello data:")
        print(data)
        hello = Actions.handle_hello(self, connected_peer, data)
        # Throw Custom Exception instead and print error message
        if not hello:
            return False
        await Actions.notify_hello(self, connected_peer)

    async def consume_get_addr(self, connected_peer, data):
        print("Will Send an answer to Get_Addr")
        message = Protocol.addr_event(self.server_host, self.server_port)
        await connected_peer.send_data_json(message)

    async def consume_status(self, connected_peer, data):
        status = Actions.handle_status(self, connected_peer, data)
        # Throw Custom Exception instead and print error message
        if not status:
            return False
        await Actions.notify_status(connected_peer)

    async def notify_ping(self, connected_peer, data):
        print("Sending Ping")
        pong_waiter = await connected_peer.sock.ping()
        await pong_waiter

    async def notify_pong(self, connected_peer, data):
        await connected_peer.sock.pong("pong")

    def register_node(self, peer_connected):
        self.peers_co.add(peer_connected)

    def unregister_node(self, peer_disconnected):
        self.peers_co.remove(peer_disconnected)

    def get_peer_by_address(self, address_and_port):
        host, port = address_and_port.split(':')
        for peer in self.peers_co:
            if peer.host == host and str(peer.port) == port:
                return peer
        return None

    async def consumer(self, message, connected_peer):
        msg_type = None
        try:
            data = json.loads(message)
            print("Main Consumer data:")
            print(data)
            if 'type' in data:
                if data['type']:
                    msg_type = data['type'].upper()
                if msg_type not in self.handlers:
                    logging.error(
                        "unsupported event: {}", data)
                else:
                    self.__debug('Handling peer msg: %s: %s' % (msg_type, message))
                    await self.handlers[msg_type](connected_peer, message)
            else:
                self.__debug("Need a 'type' key in every json message")
        except ValueError:
            self.__debug("Message need to respect Json Format")

    async def __consumer_handler(self, websocket, path):
        host, port = websocket.remote_address
        connected_peer = PeerConnection(None, host, port, websocket, None)
        self.__debug('Consumer Handler !')
        try:
            async for message in websocket:
                await self.consumer(message, connected_peer)
        except websockets.ConnectionClosed:
            print("Connection Closed handled!")
        finally:
            pass
            # Maybe need to register this node - Depending on the use cases -
            # In this case we need to unregister the node when the discussion is over
            # self.unregister_node(connected_peer)

    async def connect_and_send(self, ip_port_peer):
        ip_port_peer = str(ip_port_peer)
        try:
            async with websockets.connect('ws://'+ip_port_peer) as websocket:
                host, port = websocket.remote_address
                connected_peer = PeerConnection(None, host, port, websocket, None)
                await Actions.produce_handshaking(self, connected_peer)
                self.register_node(connected_peer)
                self.__debug("Successful Connection / Handshaking with:"+connected_peer.host+':'+str(connected_peer.port)+' !')
                self.addr_manager.fill_peers_db(str(host)+':'+str(port))
                while 1:
                    if connected_peer.produce_actions:
                        # try catch any exceptions - Connection Closed is basically handled in the finally
                        if connected_peer.produce_actions[0] == 'GET_ADDR':
                            await Actions.produce_get_addr(self, connected_peer)
                            connected_peer.produce_actions.pop(0)
        except (websockets.AbortHandshake, websockets.InvalidHandshake, websockets.InvalidMessage, socket.gaierror):
            print("Handshaking error - Peer:"+ip_port_peer+" Not connected")
        except websockets.ConnectionClosed:
            self.unregister_node(self.get_peer_by_address(ip_port_peer))

    def run_server(self):
        # Add a handler producer / consumer to handle mutliple asynchronous tasks in the same socket
        # See Handler above
        self.__debug("Run Server !")
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.__init_server_socket()
        asyncio.get_event_loop().run_until_complete(self.server_socket)
        asyncio.get_event_loop().run_forever()

    def run_client(self, ip_port_peer):
        # Add a handler producer / consumer to handle mutliple asynchronous tasks in the same socket
        # See Handler above
        self.__debug("Run Client !")
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(self.connect_and_send(ip_port_peer))
        self.__debug("Loop Connect and Send over")

