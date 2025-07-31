# Raft Consensus Algorithm Simulation

This project is a minimal Python implementation of the Raft consensus algorithm using ZeroMQ (`pyzmq`) for message passing between simulated nodes.

## 🧠 Features
- Leader election
- Heartbeat mechanism
- Term tracking and vote requests
- In-process PUB/SUB communication (ZeroMQ)

## 🛠 Requirements
- Python 3.7+
- pyzmq

```bash
pip install pyzmq
