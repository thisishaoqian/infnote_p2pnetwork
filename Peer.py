from Services.network import *
from uuid import uuid4


class Peer:

    # Beginning of Constructor
    def __init__( self, server_port, max_peers=None, my_id=None, server_host=None):
        self.debug = 0
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

        self.shutdown = False
    # End of Constructor

    def __init_node_id(self):
        self.my_id = str(uuid4()).replace('-', '')

    def __init_server_host(self):
        self.server_host = get_ip()
