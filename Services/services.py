import threading
import socket
import json


def thread_debug( msg ):
    """ Prints a message to the screen with the name of the current thread """
    print("[%s] %s" % (str(threading.currentThread().getName()), msg))


def get_local_ip():
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


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True
