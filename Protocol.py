import json
from Services import services


def handshaking_event(protocol_version, client_version, server_port, my_id):
    return json.dumps({'type': 'Hello', 'p2pVersion': protocol_version, 'clientId': client_version,
                       'listenPort': server_port, 'nodeId': my_id})


def check_hello(message, p2p_version_peer):
    print("Message in Check_Hello:")
    print(message)
    if not services.is_json(message):
        return None
    msg_json = json.loads(message)
    if 'type' not in msg_json or 'p2pVersion' not in msg_json or 'clientId' not in msg_json \
            or 'listenPort' not in msg_json or 'nodeId' not in msg_json:
        return None
    if msg_json['p2pVersion'] != p2p_version_peer:
        return None
    return msg_json


def check_status(message):
    if not services.is_json(message):
        return None
    msg_json = json.loads(message)
    if 'type' not in msg_json or 'genesisHash' not in msg_json:
        return None
    # Check Blockchain Information
    return msg_json

def status_event():
    return json.dumps({'type': 'Status', 'genesisHash': "0000"})


def addr_event(host, port):
    return json.dumps({'type': 'addr', 'host': host, 'port': str(port)})
