# Raft Consensus Algorithm Simulation

This project is a minimal Python implementation of the Raft consensus algorithm using ZeroMQ (`pyzmq`) for message passing between simulated nodes.

## 🤔 What is Raft?

Raft is a distributed consensus algorithm designed to be understandable while maintaining the same fault-tolerance and safety guarantees as Paxos. It allows a cluster of machines to agree on a shared state even in the presence of node failures, network delays, or partitions.

In simple terms, Raft is used to:
- Elect a **leader** among nodes
- Maintain **consistency** of data across nodes
- Recover safely from failures

Raft breaks consensus into three key components:
1. **Leader Election**: A node becomes the leader if it receives votes from the majority.
2. **Log Replication**: The leader accepts client requests and replicates them to followers.
3. **Safety**: Ensures that committed entries are not lost even if the leader crashes.

You can read more in the original paper: [In Search of an Understandable Consensus Algorithm (Raft)](https://raft.github.io/).

## 🧠 Features of this Project

- Simulates 3-node Raft cluster
- Leader election mechanism
- Heartbeat messages from leader
- Term tracking & voting
- Inter-node communication with ZeroMQ (inproc sockets)

## 🛠 Requirements

- Python 3.7+
- pyzmq

```bash
pip install pyzmq
