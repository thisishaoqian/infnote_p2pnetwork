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


def create_server_socket(port, backlog=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    s.listen(backlog)
    return s