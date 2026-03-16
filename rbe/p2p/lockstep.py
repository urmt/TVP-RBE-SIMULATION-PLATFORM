"""Lockstep simulation engine for P2P RBE simulation."""
import asyncio
from typing import Dict, List, Callable
from rbe.p2p.network import P2PNetworkManager
from rbe.utils.deterministic import hash_simulation_state, SeededRandom

class LockstepSimulation:
    """Coordinates distributed simulation execution."""
    
    def __init__(self, network: P2PNetworkManager, simulation_step_func: Callable, initial_state: dict):
        self.network = network
        self.simulation_step = simulation_step_func
        self.state = initial_state
        self.current_tick = 0
        self.running = False
        self.tick_rate = 1.0
        self.divergence_count = 0
        self.max_divergences = 3
    
    async def start(self):
        self.running = True
        while self.running:
            try:
                await self._execute_tick()
            except Exception as e:
                print(f"Tick {self.current_tick} failed: {e}")
                await self._resync()
            await asyncio.sleep(1.0 / self.tick_rate)
    
    def stop(self):
        self.running = False
    
    async def _execute_tick(self):
        tick_start = asyncio.get_event_loop().time()
        local_input = self._collect_local_inputs()
        all_inputs = await self.network.submit_tick_input(self.current_tick, local_input)
        if not all_inputs:
            print(f"Tick {self.current_tick}: No inputs received, skipping")
            return
        rng = SeededRandom(self.current_tick)
        self.state = self.simulation_step(self.state, all_inputs, rng)
        state_hash = hash_simulation_state(self.state)
        consensus = await self.network.verify_consensus(self.current_tick, state_hash)
        if consensus is True:
            self.divergence_count = 0
            self.current_tick += 1
            tick_duration = asyncio.get_event_loop().time() - tick_start
            print(f"Tick {self.current_tick} complete ({tick_duration*1000:.1f}ms)")
        elif consensus is False:
            self.divergence_count += 1
            print(f"Divergence #{self.divergence_count} at tick {self.current_tick}")
            if self.divergence_count >= self.max_divergences:
                print("Too many divergences, triggering resync...")
                await self._resync()
                self.divergence_count = 0
        else:
            print(f"No consensus at tick {self.current_tick}, halting simulation")
            self.stop()
    
    def _collect_local_inputs(self) -> dict:
        return {"player_id": self.network.local_peer_id, "actions": []}
    
    async def _resync(self):
        print("Resyncing state from network...")
