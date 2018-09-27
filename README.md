# infnote_p2pnetwork 

### Peer Discovery:
First time the program is run, several possibilities:
* Manual entry (Console or QR Code) : -addnode and -connect
* DNS request / seeding, use when data base file is empty (see below)
* Hard Coded "Seed" Addresses: Last Solution if DNS failed

Address Storage:

Address manager also keeps track of peer address in a data base file. Update the timestamp when got updates and know which node is new or not.

Broadcast UDP between peers:
* getaddr : get the addr of a peer or peers 
* addr : Response to getaddr
Can be a relay: Send last n peers (Sort by timestamp to get the active nodes)
Advertise their own address periodically to the connected nodes.
When a connection is made

### Protocole

Every Request will contain a 'type' to define the exact type of request
Session Management:

Handshaking and a Status message must be sent. Following the reception of the peer's Status message, the session is active.

* HandShaking: Hello [p2pVersion : string, clientId: string, listenPort: string, nodeId: uuid]

p2pVersion Specifies the implemented version of the P2P protocol
listenPort specifies the port that the client is listening on, 0 means the client is not listening
clientId specifies the client software identity, as a human-readable string (Full / light node for ex)
nodeId is the Unique Identity of the node and specifies a 512-bit hash that identifies this node.

* Blockchain Status: Status [height: int, genesisHash: hash, network_id: string]

Height is an Integer (Can be found in block head ?) which is the length of the chain
genesisHash is the hash of the fist block (initial block)
network id is the identifier for this blockchain / network 

Quit / Destroy a session : The peers must disconnect.
* Disconnect: Disconnect [reason: P] Inform the peer that a disconnection is imminent
reason is an optional integer specifying one reason to disconnect (TCP sub-system error, Too many peers, Already connected, Incompatible P2P protocol version)

* Ping: Ping [] Requests an immediate reply of Pong from the peer.
* Pong: Pong [] Reply to peer's Ping packet.

Transactions: Transactions [sender: B_20, receiver: B_20, message: [...] ]
Specify (a) transaction(s) that the peer should make sure is included on its transaction queue.
This packet must contain at least one (new) transaction and it must not send the same transaction to a peer in the same session.

Block Propagation:
Need more Blockchain knowledges, but basic interactions:
Request GetBlockHashes / Response: BlockHashes
Request GetBlocks / Response: Blocks 
Request: NewBlock

Nodes are free to store ratings for given IDs (how useful the node has been in the past)
