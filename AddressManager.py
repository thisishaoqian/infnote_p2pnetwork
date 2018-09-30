import os


class AddressManager:

    def __init__(self):
        self.peers_db = "peers.dat"
        self.new_peer_console = None

        # List of peers address
        self.peers_known = set()

    def add_node_console(self, new_peer):
        self.new_peer_console = new_peer

    def fill_peers_db(self, peer):
        found = False
        if os.path.exists(self.peers_db) == False:
            open(self.peers_db, "w")
        with open(self.peers_db, 'r+') as peers:
            for node_peer in peers:
                if node_peer == peer + '\n' or node_peer == peer:
                    found = True
                    break
            if found == False:
                peers.write(peer + '\n')

    def peers_discovery(self):
        # This function will try different peer discovery methods
        if self.new_peer_console is not None:
            self.peers_known.add(self.new_peer_console)
        # Read the peers.dat file