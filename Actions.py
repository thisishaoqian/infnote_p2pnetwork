import Protocol

# Handlers will set the status type of the connection in the future
# Then the peers will know the status of request with a specified peer


def handle_hello(peer, connected_peer, data):
    print("Handle_Hello data:")
    print(data)
    hello = Protocol.check_hello(data, peer.protocol_version)
    if hello is None:
        return False
    connected_peer.protocol_version = hello['p2pVersion']
    connected_peer.peer_id = hello['nodeId']
    connected_peer.client_id = hello['clientId']
    return True


def handle_status(peer, connected_peer, data):
    status = Protocol.check_status(data)
    if status is None:
        return False
    return True


async def notify_hello(peer, connected_peer):
    # Send a Hello event with the format defined in the Protocol file
    message = Protocol.handshaking_event(peer.protocol_version, peer.client_version,
                                         peer.server_port, peer.my_id)
    await connected_peer.send_data_json(message)


async def notify_status(peer_connected):
    # Send a Status event with the format defined in the Protocol file
    # Basically give information regarding the blockchain of the peer
    message = Protocol.status_event()
    await peer_connected.send_data_json(message)


async def produce_handshaking(peer_send, peer_connected):
    await notify_hello(peer_send, peer_connected)
    response_hello = await peer_connected.rcv_data_json()
    hello = handle_hello(peer_send, peer_connected, response_hello)
    if not hello:
        return False
    await notify_status(peer_connected)
    response_status = await peer_connected.rcv_data_json()
    status = handle_status(peer_send, peer_connected, response_status)
    if not status:
        return False
    return True
