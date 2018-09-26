import json


def handshaking_event(protocol_version, client_version, server_port, my_id):
    return json.dumps({'type': 'Hello', 'p2pVersion': protocol_version, 'clientId': client_version,
                       'listenPort': server_port, 'nodeId': my_id})


def status_event():
    return json.dumps({'type': 'Status', 'genesisHash': "0000"})


def ping_event():
    return json.dumps({'type': 'ping'})


def pong_event():
    return json.dumps({'type': 'pong'})