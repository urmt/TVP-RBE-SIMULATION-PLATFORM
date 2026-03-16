"""
Tests for P2P networking and consensus.
"""
import pytest
import asyncio
import time
from rbe.p2p.network import P2PNetworkManager, MessageType, PeerInfo
from rbe.p2p.lockstep import LockstepSimulation
from rbe.utils.deterministic import SeededRandom, verify_determinism

@pytest.mark.asyncio
async def test_peer_connection():
    """Test connecting two peers"""
    node1 = P2PNetworkManager("node1", port=9001)
    node2 = P2PNetworkManager("node2", port=9002)
    
    await node1.start()
    await node2.start()
    
    await node1.connect_peer("localhost:9002")
    
    assert "peer_localhost:9002" in node1.peers
    
    await node1.stop()
    await node2.stop()

def test_deterministic_rng():
    """Test that seeded RNG produces identical sequences"""
    rng1 = SeededRandom(12345)
    rng2 = SeededRandom(12345)
    
    seq1 = [rng1.next_int() for _ in range(100)]
    seq2 = [rng2.next_int() for _ in range(100)]
    
    assert seq1 == seq2, "RNG not deterministic!"

def test_determinism_verification():
    """Test determinism verification utility"""
    def deterministic_func(seed, iterations):
        rng = SeededRandom(seed)
        return {'result': sum(rng.next_int() for _ in range(iterations))}
    
    is_deterministic = verify_determinism(
        deterministic_func,
        inputs={'seed': 42, 'iterations': 100},
        iterations=50
    )
    
    assert is_deterministic, "Function should be deterministic!"

@pytest.mark.asyncio
async def test_message_broadcast():
    """Test broadcasting messages to peers"""
    node = P2PNetworkManager("test_node", port=9005)
    await node.start()
    
    node.peers["peer1"] = PeerInfo("peer1", "localhost", 9006, time.time())
    await node.broadcast_message(MessageType.PEER_ANNOUNCE, {"status": "alive"})
    
    await node.stop()

@pytest.mark.asyncio
async def test_tick_input_collection():
    """Test collecting tick inputs from peers"""
    node = P2PNetworkManager("test_node", port=9007)
    await node.start()
    
    local_input = {"player_id": "test_node", "actions": [{"type": "build_city"}]}
    inputs = await node.submit_tick_input(0, local_input)
    
    assert len(inputs) >= 1
    
    await node.stop()

def test_state_hashing():
    """Test deterministic state hashing"""
    from rbe.utils.deterministic import hash_simulation_state
    
    state1 = {"year": 1, "population": 1000, "resources": {"food": 100}}
    state2 = {"resources": {"food": 100}, "population": 1000, "year": 1}
    
    hash1 = hash_simulation_state(state1)
    hash2 = hash_simulation_state(state2)
    
    assert hash1 == hash2, "State hashing not deterministic!"
