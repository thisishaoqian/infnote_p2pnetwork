import socket


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except ConnectionError:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


# The backlog parameter indicates how many incoming connections should be queued up
def create_server_socket(port, backlog=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set the Socket options
    # SO_REUSEADDR option, the port number of the socket will be immediately reusable after the socket is closed
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    s.listen(backlog)
    return s
