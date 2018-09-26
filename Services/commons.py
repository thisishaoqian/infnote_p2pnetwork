import threading


def thread_debug( msg ):
    """ Prints a message to the screen with the name of the current thread """
    print("[%s] %s" % (str(threading.currentThread().getName()), msg))
