# TVP-RBE-SIMULATION-PLATFORM

A Resource-Based Economy (RBE) simulation platform implementing The Venus Project's concepts for resource tracking, allocation, and distributed simulation.

## Overview

The TVP-RBE-Simulation-Platform is a technical framework for modeling and tracking physical resources in a resource-based economy context. It provides real-time resource monitoring, allocation history tracking, and simulation capabilities for energy, water, and material resources.

### Key Features

- **Resource Tracking**: Real-time monitoring of energy (kWh), water (m³), and materials (kg/units)
- **Cybernation Hub**: AI-driven resource allocation with sustainability and equity metrics
- **P2P Lockstep**: Distributed simulation with deterministic consensus
- **SQLite Database**: Persistent storage for resources, allocations, and history
- **CLI Interface**: Command-line tools for resource management
- **API Layer**: Programmatic access to resource operations

## Architecture

### Phase 1: Resource Models (`rbe/models/`)
- Abstract base class for all resource types
- Energy resources (kWh)
- Water resources (m³)
- Material resources (kg, units)
- Physical unit validation and conversion

### Phase 2: Resource Tracker (`tracker/`)
- SQLite database for resource tracking
- Tables: resources, allocations, history, feeds
- Real-time data feed support
- CLI interface for data entry and queries

### Phase 3: Cybernation Hub (`hub/`)
- Central AI director for resource allocation
- Sustainability metrics (carbon footprint, renewable ratio)
- Equity metrics (population served, per-capita allocation)
- Scarcity scenario modeling

### Phase 4: P2P Network (`rbe/p2p/`)
- Peer-to-peer network management
- Distributed simulation coordination
- Message broadcasting and consensus
- State synchronization

### Phase 5: Lockstep Simulation (`rbe/p2p/lockstep.py`)
- Deterministic simulation execution
- Tick-based synchronization
- Divergence detection and resync
- Seeded random number generation

### Phase 6: Visualization (`visualization/`)
- Circular city visualization
- Resource flow diagrams
- Real-time dashboards

## Installation

### Quick Install

```bash
# Navigate to the repository
cd /home/student/RBE-TVP-SIM

# Run the installation script
chmod +x INSTALL.sh
./INSTALL.sh
```

### Manual Installation

```bash
# Create virtual environment
/usr/bin/python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-p2p.txt

# Initialize database
/usr/bin/python3 -c "from tracker.database import ResourceDatabase; ResourceDatabase()"
```

## Usage

### Single-Player Mode

#### Resource Management CLI

```bash
# Add a new resource
/usr/bin/python3 -m tracker.cli add-resource \
    --id solar_array_01 \
    --name "Solar Array A" \
    --type ENERGY \
    --unit kWh \
    --quantity 1000.0

# List all resources
/usr/bin/python3 -m tracker.cli list-resources

# Allocate resources
/usr/bin/python3 -m tracker.cli allocate \
    --resource-id solar_array_01 \
    --amount 100.0 \
    --to "Building A" \
    --purpose "Daily consumption"

# View allocation history
/usr/bin/python3 -m tracker.cli history --resource-id solar_array_01
```

#### Python API

```/usr/bin/python3
from tracker.database import ResourceDatabase
from tracker.api import ResourceAPI

# Initialize database
db = ResourceDatabase("rbe_resources.db")

# Add a resource
api = ResourceAPI("rbe_resources.db")
api.create_resource(
    resource_id="water_tank_01",
    name="Fresh Water Reserve",
    resource_type="WATER",
    unit="m³",
    initial_quantity=500.0
)

# Allocate resources
api.allocate("water_tank_01", 50.0, allocated_to="Community Center")

# Get allocation history
history = api.get_allocation_history("water_tank_01")
```

### P2P Multiplayer Mode

#### Starting a P2P Node

```/usr/bin/python3
import asyncio
from rbe.p2p.network import P2PNetworkManager
from rbe.p2p.lockstep import LockstepSimulation

async def run_node():
    # Create network manager
    network = P2PNetworkManager("node_1", port=9000)
    
    # Start the node
    await network.start(seed_nodes=["localhost:9001"])
    
    # Define simulation step
    def simulation_step(state, inputs, rng):
        # Your simulation logic here
        return state
    
    # Create lockstep simulation
    sim = LockstepSimulation(
        network=network,
        simulation_step_func=simulation_step,
        initial_state={"resources": {}}
    )
    
    # Start simulation
    await sim.start()

# Run the node
asyncio.run(run_node())
```

#### Running Tests

```bash
# Run all tests
/usr/bin/python3 -m pytest tests/ -v

# Run specific test modules
/usr/bin/python3 -m pytest tests/test_resource.py -v
/usr/bin/python3 -m pytest tests/test_p2p.py -v
```

## Project Structure

```
RBE-TVP-SIM/
├── .git/                       # Git repository
├── INSTALL.sh                  # Installation script
├── README.md                   # This file
├── requirements-p2p.txt      # Python dependencies
├── TVP_RBE_DESIGN_SPEC.md    # Design specification
├── INTEGRATION_TEST_REPORT.json  # Test results
├── rbe/                      # Core RBE modules
│   ├── __init__.py
│   ├── models/               # Resource models
│   │   ├── __init__.py
│   │   └── resource.py       # Energy, Water, Material classes
│   ├── p2p/                  # P2P networking
│   │   ├── __init__.py
│   │   ├── network.py        # P2P network manager
│   │   └── lockstep.py       # Lockstep simulation
│   ├── utils/                # Utilities
│   │   ├── __init__.py
│   │   └── deterministic.py  # Seeded RNG, state hashing
│   └── simulation.py           # Main simulation engine
├── tracker/                  # Resource tracking
│   ├── __init__.py
│   ├── database.py           # SQLite database
│   ├── api.py                # Resource API
│   └── cli.py                # Command-line interface
├── hub/                      # Cybernation Hub
│   ├── __init__.py
│   └── cybernation_hub.py    # AI resource allocation
├── connectors/               # External connectors
│   ├── __init__.py
│   └── iot_sensors.py        # IoT sensor integration
├── ui/                       # User interface
│   ├── __init__.py
│   └── tabs/
│       ├── __init__.py
│       └── multiplayer_tab.py
├── visualization/            # Visualization
│   ├── __init__.py
│   └── circular_city.py
├── tests/                    # Unit tests
│   ├── test_resource.py      # Resource model tests
│   └── test_p2p.py           # P2P network tests
└── rbe_resources.db          # SQLite database (generated)
```

## Physical Units

| Resource Type | Unit | Description |
|--------------|------|-------------|
| Energy | kWh | Kilowatt-hours |
| Water | m³ | Cubic meters |
| Materials | kg | Kilograms (or units for discrete items) |

## Cybernation Hub

The Cybernation Hub provides AI-driven resource allocation based on:

### Sustainability Metrics
- Carbon footprint (lower is better)
- Renewable ratio (higher is better)
- Recyclability (higher is better)
- Water usage (lower is better)

### Equity Metrics
- Population served
- Current allocation per capita
- Minimum required allocation
- Geographic distribution

### Priority Levels
1. **CRITICAL**: Essential services (hospitals, emergency)
2. **HIGH**: Important infrastructure
3. **MEDIUM**: Standard operations
4. **LOW**: Non-essential requests

## P2P Lockstep Simulation

The lockstep simulation ensures all peers remain synchronized:

1. **Tick-based execution**: Fixed time intervals
2. **Input collection**: Gather inputs from all peers
3. **Deterministic simulation**: Same inputs = same outputs
4. **State hashing**: Verify consensus across peers
5. **Divergence handling**: Resync when states diverge

## Testing

All modules include comprehensive unit tests:

```bash
# Run all tests with coverage
/usr/bin/python3 -m pytest tests/ -v --cov=rbe --cov=tracker --cov=hub

# Integration test report
cat INTEGRATION_TEST_REPORT.json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Acknowledgments

- The Venus Project (https://www.thevenusproject.com/)
- Resource-Based Economy concepts by Jacque Fresco

## Support

For issues and feature requests, please use the GitHub issue tracker.

---

**Note**: This is a simulation platform for educational and research purposes. Resource allocation decisions should always involve human oversight in real-world applications.
