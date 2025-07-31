import time
import threading
import random
import zmq
import json

# Election timeout interval (randomly selected within this range)
ELECTION_TIMEOUT = (1.5, 3.0)
# Interval between heartbeat messages sent by the leader
HEARTBEAT_INTERVAL = 1.0

class Node:
    def __init__(self, node_id, peer_ids, context):
        self.id = node_id
        self.peers = peer_ids  # List of other node IDs in the cluster
        self.role = 'follower'  # Initial role is follower
        self.term = 0  # Current term number
        self.voted_for = None  # ID of candidate this node voted for
        self.votes_received = 0  # Number of votes received (when candidate)

        self.context = context
        # Subscriber socket to receive messages from other nodes
        self.sub = self.context.socket(zmq.SUB)
        self.sub.setsockopt(zmq.SUBSCRIBE, b'')  # Subscribe to all messages
        for peer in peer_ids:
            self.sub.connect(f'inproc://{peer}')  # Connect to each peer's PUB socket

        # Publisher socket to send messages to other nodes
        self.pub = self.context.socket(zmq.PUB)
        self.pub.bind(f'inproc://{self.id}')  # Bind PUB socket to this node's ID

        self.last_heartbeat = time.time()  # Timestamp of last received heartbeat
        self.lock = threading.Lock()  # Lock for synchronizing shared state

    def send(self, msg):
        # Send a JSON message to all peers
        self.pub.send_json(msg)

    def receive_loop(self):
        # Continuously receive and handle incoming messages
        while True:
            msg = self.sub.recv_json()
            with self.lock:
                if msg['type'] == 'heartbeat' and msg['term'] >= self.term:
                    # Reset heartbeat timer and follow newer term
                    self.term = msg['term']
                    self.role = 'follower'
                    self.last_heartbeat = time.time()
                elif msg['type'] == 'vote_request':
                    # Grant vote if term is higher and node hasn't voted yet
                    if msg['term'] > self.term and (self.voted_for is None or self.voted_for == msg['candidate_id']):
                        self.term = msg['term']
                        self.voted_for = msg['candidate_id']
                        self.send({
                            'type': 'vote_response',
                            'term': self.term,
                            'vote_granted': True,
                            'to': msg['candidate_id']
                        })
                elif msg['type'] == 'vote_response' and self.role == 'candidate':
                    if msg['vote_granted']:
                        self.votes_received += 1
                        # Become leader if majority is reached
                        if self.votes_received > len(self.peers) // 2:
                            self.role = 'leader'
                            print(f"{self.id} became LEADER (term {self.term})")

    def election_loop(self):
        # Periodically check for timeouts or act based on role
        while True:
            time.sleep(0.1)
            with self.lock:
                if self.role == 'leader':
                    # Send heartbeat periodically to maintain leadership
                    self.send({'type': 'heartbeat', 'term': self.term})
                    time.sleep(HEARTBEAT_INTERVAL)
                elif time.time() - self.last_heartbeat > random.uniform(*ELECTION_TIMEOUT):
                    # Start election if no heartbeat received in time
                    self.role = 'candidate'
                    self.term += 1
                    self.voted_for = self.id
                    self.votes_received = 1  # Vote for self
                    print(f"{self.id} started election (term {self.term})")
                    self.send({
                        'type': 'vote_request',
                        'term': self.term,
                        'candidate_id': self.id
                    })
                    self.last_heartbeat = time.time()

    def start(self):
        # Start the receive loop in a separate thread and run the election loop
        threading.Thread(target=self.receive_loop, daemon=True).start()
        self.election_loop()


context = zmq.Context()

nodes = []
node_ids = ['node1', 'node2', 'node3']
for nid in node_ids:
    peers = [p for p in node_ids if p != nid]  # All other nodes are peers
    node = Node(nid, peers, context)
    thread = threading.Thread(target=node.start, daemon=True)
    thread.start()
    nodes.append(node)

# Keep the main thread alive indefinitely
while True:
    time.sleep(10)
