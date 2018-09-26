import traceback
import time

from Services.network import *
from Services.commons import *
from uuid import uuid4


class Peer:

    # Beginning of Constructor
    def __init__(self, server_port, max_peers=None, my_id=None, server_host=None):
        self.debug = True
        self.running = False
        self.server_port = int(server_port)

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

        # Hash Table of known peers, in the future manage by an address manager
        self.peers = {}

    # End of Constructor

    def __init_node_id(self):
        self.my_id = str(uuid4()).replace('-', '')

    def __init_server_host(self):
        self.server_host = get_ip()

    def __debug(self, msg):
        if self.debug:
            thread_debug(msg)

    def __display_peer_status(self):
        print("running: --%r--, server_port: --%d--, server_host: --%s--, node id: --%s--, max_peers: --%d--" %
              (self.running,
               self.server_port,
               self.server_host,
               self.my_id,
               self.max_peers))

    def run_server(self):
        # New socket object used to send and receive data on the connection
        listening_socket = create_server_socket(self.server_port)

        # Timeout applies to a single call to socket read/write operation, basically each 'recv' call.
        listening_socket.settimeout(2)

        # running variable is used to shutdown server loop.
        self.running = True

        self.__debug('Server started: %s (%s:%d)'
                     % (self.my_id, self.server_host, self.server_port))

        while self.running:
            if self.debug:
                self.__display_peer_status()
                time.sleep(1)  # Delays for n seconds for debug
            try:
                self.__debug('Listening for Connections...')
                # accept return a new socket object usable to send and receive data on the connection
                # And return an address which is the address bound to the socket on the other end of the connection.
                client_sock, client_addr = listening_socket.accept()
                client_sock.settimeout(None)

                # Handle incoming connection by creating a new thread. Thread is close when the handler finish the task
                # handle_peer will dispatch the tasks depending on the request type
                th = threading.Thread(target=self.__handle_peer, args=[client_sock])
                th.start()

            except KeyboardInterrupt:
                print("Keyboard interruption - Stopping Server loop")
                self.running = False
                continue
            except:
                if self.debug:
                    traceback.print_exc()
                    continue
        # end while loop

        self.__debug('Server loop exiting')
        listening_socket.close()
    # end server run method


peer = Peer(80, 5)
peer.run_server()
