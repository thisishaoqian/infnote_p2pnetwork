# Socket Encapsulation


class PeerConnection:

    def __init__(self, peer_id, host, port, connection=None, debug=False):
        self.id = peer_id
        self.host = host
        self.port = port
        self.debug = debug

        if not connection:
            self.sock = connection.socket(connection.AF_INET, connection.SOCK_STREAM)
            self.sock.connect((host, int(self.port)))
        else:
            self.sock = connection
        self.sd = self.sock.makefile('rw', 0)

