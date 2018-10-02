import sys
import Peer
import signal
import _thread
import json
import asyncio


class App:

    def __init__(self):
        self.peer = Peer.Peer()

    def run(self):
        node = None
        if (len(sys.argv) > 2 and sys.argv[2] == '-add_node') or len(self.peer.get_peers()) == 0:
            try:
                node = input('Enter address and port:')
            except SyntaxError:
                node = None
            except KeyboardInterrupt:
                exit(0)
            if node is None or len(node) == 0:
                print("Address it not valid, no peer connected...")
            else:
                self.peer.addr_manager.add_node_console(node)
        if len(sys.argv) > 1:
            self.peer.server_port = int(sys.argv[1])
        self.run_peer()

    async def send_to_peer(self):
        await list(self.peer.peers_co)[0].send_data_json(json.dumps({'type': 'GET_ADDR'}))

    async def receive_from_peer(self):
        response = await list(self.peer.peers_co)[0].rcv_data_json()
        print("Response From Get ADDR:")
        print(response)

    def run_peer(self):
        # This restores the default Ctrl+C signal handler, which just kills the process
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        _thread.start_new_thread(self.peer.run_server, ())
        self.peer.addr_manager.peers_discovery()
        if len(self.peer.addr_manager.peers_known):
            _thread.start_new_thread(self.peer.run_client, (list(self.peer.addr_manager.peers_known)[0], ))
            print(self.peer.shutdown)
        while self.peer.shutdown is False:
            action = input("Type:")
            if action == "SEND":
                print("Will Send A GET_ADDR")
                list(self.peer.peers_co)[0].produce_actions.append('GET_ADDR')
            pass


if __name__ == '__main__':
    app = App()
    app.run()
