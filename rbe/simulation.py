"""RBE Simulation - supports both single-player and multiplayer P2P modes."""
from typing import List, Dict, Any
from rbe.p2p.network import P2PNetworkManager
from rbe.p2p.lockstep import LockstepSimulation
from rbe.utils.deterministic import SeededRandom

class RBESimulation:
    """Resource-Based Economy Simulation."""
    
    def __init__(self, mode="single_player"):
        self.mode = mode
        self.state = self._create_initial_state()
        self.p2p_network = None
        self.lockstep_engine = None
        self.current_year = 0
        self.population = 50000
        self.resources = {}
    
    def _create_initial_state(self) -> dict:
        return {
            "year": 0,
            "population": 50000,
            "resources": {
                "food": 100000,
                "water": 100000,
                "energy": 100000,
                "materials": 100000
            },
            "cities": [],
            "climate": {
                "temperature": 20.0,
                "rainfall": 1000.0
            }
        }
    
    def get_initial_state(self) -> dict:
        return self._create_initial_state()
    
    async def start_multiplayer(self, peer_id: str, seed_nodes: List[str] = None):
        if self.mode != "multiplayer":
            raise ValueError("Simulation not in multiplayer mode")
        self.p2p_network = P2PNetworkManager(peer_id)
        await self.p2p_network.start(seed_nodes)
        initial_state = self.get_initial_state()
        self.lockstep_engine = LockstepSimulation(
            network=self.p2p_network,
            simulation_step_func=self.deterministic_step,
            initial_state=initial_state
        )
        await self.lockstep_engine.start()
    
    def deterministic_step(self, state: dict, inputs: List[dict], rng: SeededRandom) -> dict:
        new_state = state.copy()
        new_state['resources'] = state['resources'].copy()
        new_state['climate'] = state['climate'].copy()
        new_state['cities'] = state['cities'].copy()
        for player_input in inputs:
            player_id = player_input.get("player_id", "unknown")
            actions = player_input.get("actions", [])
            for action in actions:
                new_state = self._apply_action(new_state, player_id, action, rng)
        new_state = self._simulate_environment(new_state, rng)
        new_state['year'] = state.get('year', 0) + 1
        return new_state
    
    def _apply_action(self, state: dict, player_id: str, action: dict, rng: SeededRandom) -> dict:
        action_type = action.get("type")
        if action_type == "build_city":
            city_name = action.get("name", f"City_{rng.next_int(0, 9999)}")
            city = {
                "name": city_name,
                "population": action.get("population", 1000),
                "resources": action.get("resources", {}),
                "owner": player_id
            }
            state['cities'].append(city)
        elif action_type == "allocate_resource":
            resource_type = action.get("resource_type")
            amount = action.get("amount", 0)
            if resource_type in state['resources']:
                state['resources'][resource_type] = max(0, state['resources'][resource_type] - amount)
        return state
    
    def _simulate_environment(self, state: dict, rng: SeededRandom) -> dict:
        temp_change = rng.next_float() * 0.2 - 0.1
        state['climate']['temperature'] += temp_change
        for resource in state['resources']:
            regen_rate = rng.next_float() * 0.05
            state['resources'][resource] = int(state['resources'][resource] * (1 + regen_rate))
        growth_rate = rng.next_float() * 0.02
        state['population'] = int(state['population'] * (1 + growth_rate))
        return state
