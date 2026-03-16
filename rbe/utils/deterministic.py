"""Deterministic random number generation for P2P consistency."""
import hashlib
from typing import List

class SeededRandom:
    """Mersenne Twister PRNG with explicit seed."""
    
    def __init__(self, seed: int):
        self.seed = seed
        self.state = seed
    
    def next_int(self, min_val: int = 0, max_val: int = 2**31 - 1) -> int:
        self.state = (self.state * 1103515245 + 12345) & 0x7fffffff
        return min_val + (self.state % (max_val - min_val + 1))
    
    def next_float(self) -> float:
        return self.next_int() / 0x7fffffff
    
    def choice(self, items: List):
        return items[self.next_int(0, len(items) - 1)]
    
    def shuffle(self, items: List) -> List:
        result = items.copy()
        for i in range(len(result) - 1, 0, -1):
            j = self.next_int(0, i)
            result[i], result[j] = result[j], result[i]
        return result

def hash_simulation_state(state: dict) -> str:
    import json
    state_json = json.dumps(state, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(state_json.encode('utf-8')).hexdigest()

def verify_determinism(simulation_func, inputs: dict, iterations: int = 100) -> bool:
    results = []
    for _ in range(iterations):
        result = simulation_func(**inputs)
        results.append(hash_simulation_state(result))
    return len(set(results)) == 1
