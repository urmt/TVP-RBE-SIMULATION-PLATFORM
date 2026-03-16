"""Peer-to-peer network management for distributed RBE simulation."""
import asyncio
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time

class MessageType(Enum):
    PEER_ANNOUNCE = "peer_announce"
    TICK_INPUT = "tick_input"
    STATE_HASH = "state_hash"
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"

@dataclass
class PeerInfo:
    peer_id: str
    address: str
    port: int
    last_seen: float
    latency_ms: float = 0
    
    def is_alive(self, timeout_seconds: int = 30) -> bool:
        return time.time() - self.last_seen < timeout_seconds

@dataclass
class SimulationMessage:
    message_type: MessageType
    sender_id: str
    tick_number: int
    payload: dict
    timestamp: float

class P2PNetworkManager:
    def __init__(self, local_peer_id: str, port: int = 9000):
        self.local_peer_id = local_peer_id
        self.port = port
        self.peers: Dict[str, PeerInfo] = {}
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.current_tick = 0
        self.tick_inputs: Dict[int, Dict[str, dict]] = {}
        self.tick_hashes: Dict[int, Dict[str, str]] = {}
        self.running = False
    
    async def start(self, seed_nodes: List[str] = None):
        self.running = True
        asyncio.create_task(self._listen())
        if seed_nodes:
            for address in seed_nodes:
                await self.connect_peer(address)
        asyncio.create_task(self._discover_peers())
        asyncio.create_task(self._heartbeat())
    
    async def stop(self):
        self.running = False
        await self.broadcast_message(MessageType.PEER_ANNOUNCE, {"status": "leaving"})
    
    async def connect_peer(self, address: str):
        peer_id = f"peer_{address}"
        self.peers[peer_id] = PeerInfo(
            peer_id=peer_id,
            address=address,
            port=self.port,
            last_seen=time.time()
        )
        print(f"Connected to peer: {peer_id}")
    
    async def broadcast_message(self, msg_type: MessageType, payload: dict):
        message = SimulationMessage(
            message_type=msg_type,
            sender_id=self.local_peer_id,
            tick_number=self.current_tick,
            payload=payload,
            timestamp=time.time()
        )
        for peer_id in self.peers.keys():
            await self._send_to_peer(peer_id, message)
    
    async def _send_to_peer(self, peer_id: str, message: SimulationMessage):
        pass
    
    async def _listen(self):
        while self.running:
            await asyncio.sleep(0.1)
    
    async def _discover_peers(self):
        while self.running:
            await asyncio.sleep(10)
    
    async def _heartbeat(self):
        while self.running:
            await self.broadcast_message(MessageType.PEER_ANNOUNCE, {
                "status": "alive",
                "tick": self.current_tick
            })
            await asyncio.sleep(5)
    
    def register_handler(self, msg_type: MessageType, handler: Callable):
        self.message_handlers[msg_type] = handler
    
    async def handle_message(self, message: SimulationMessage):
        handler = self.message_handlers.get(message.message_type)
        if handler:
            await handler(message)
    
    async def submit_tick_input(self, tick_number: int, local_input: dict):
        await self.broadcast_message(MessageType.TICK_INPUT, {
            "tick": tick_number,
            "input": local_input
        })
        if tick_number not in self.tick_inputs:
            self.tick_inputs[tick_number] = {}
        self.tick_inputs[tick_number][self.local_peer_id] = local_input
        
        deadline = time.time() + 2.0
        while time.time() < deadline:
            if self._all_inputs_received(tick_number):
                break
            await asyncio.sleep(0.01)
        return self._get_sorted_inputs(tick_number)
    
    def _all_inputs_received(self, tick_number: int) -> bool:
        if tick_number not in self.tick_inputs:
            return False
        active_peers = {p for p in self.peers.keys() if self.peers[p].is_alive()}
        active_peers.add(self.local_peer_id)
        received_peers = set(self.tick_inputs[tick_number].keys())
        return active_peers.issubset(received_peers)
    
    def _get_sorted_inputs(self, tick_number: int) -> List[dict]:
        if tick_number not in self.tick_inputs:
            return []
        inputs = self.tick_inputs[tick_number]
        return [inputs[peer_id] for peer_id in sorted(inputs.keys())]
    
    async def verify_consensus(self, tick_number: int, local_state_hash: str):
        await self.broadcast_message(MessageType.STATE_HASH, {
            "tick": tick_number,
            "hash": local_state_hash
        })
        if tick_number not in self.tick_hashes:
            self.tick_hashes[tick_number] = {}
        self.tick_hashes[tick_number][self.local_peer_id] = local_state_hash
        
        deadline = time.time() + 1.0
        while time.time() < deadline:
            if self._all_hashes_received(tick_number):
                break
            await asyncio.sleep(0.01)
        
        hashes = list(self.tick_hashes[tick_number].values())
        hash_counts = {}
        for h in hashes:
            hash_counts[h] = hash_counts.get(h, 0) + 1
        
        majority_hash = max(hash_counts, key=hash_counts.get)
        majority_count = hash_counts[majority_hash]
        total_nodes = len(hashes)
        consensus_threshold = total_nodes * 2 // 3
        
        if majority_count >= consensus_threshold:
            return local_state_hash == majority_hash
        return None
    
    def _all_hashes_received(self, tick_number: int) -> bool:
        if tick_number not in self.tick_hashes:
            return False
        active_peers = {p for p in self.peers.keys() if self.peers[p].is_alive()}
        active_peers.add(self.local_peer_id)
        received_peers = set(self.tick_hashes[tick_number].keys())
        return active_peers.issubset(received_peers)
