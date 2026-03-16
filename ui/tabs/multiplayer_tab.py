"""Multiplayer setup UI for P2P RBE simulation."""
import streamlit as st
import asyncio
from rbe.simulation import RBESimulation

def render_multiplayer_tab():
    """Render multiplayer P2P setup interface"""
    st.header("🌐 Multiplayer RBE Simulation")
    
    st.markdown("""
    **Distributed P2P Mode**: Join a peer-to-peer network to run collaborative RBE simulations.
    
    - No central server (fully decentralized)
    - Censorship-resistant
    - Zero hosting costs
    - Demonstrates RBE principles through infrastructure
    """)
    
    st.subheader("Network Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        peer_id = st.text_input(
            "Your Peer ID", 
            value=f"player_{st.session_state.get('user_id', 'anonymous')}",
            help="Unique identifier for your node"
        )
    
    with col2:
        mode = st.selectbox(
            "Join Mode",
            ["Create New Network", "Join Existing Network"],
            help="Create a new simulation network or join an existing one"
        )
    
    if mode == "Join Existing Network":
        seed_node_input = st.text_area(
            "Seed Nodes (one per line)",
            placeholder="/ip4/127.0.0.1/tcp/9000/p2p/QmExample...",
            help="Enter addresses of bootstrap nodes to connect to"
        )
        seed_nodes = [s.strip() for s in seed_node_input.split('\n') if s.strip()]
    else:
        seed_nodes = None
        st.info("You'll be the first node in a new network. Share your address with others to let them join.")
    
    st.subheader("Simulation Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        population = st.number_input("Starting Population", 1000, 1000000, 50000)
    
    with col2:
        climate = st.selectbox("Climate Zone", ["Tropical", "Temperate", "Arid", "Arctic"])
    
    with col3:
        duration_years = st.slider("Simulation Years", 1, 100, 10)
    
    if st.button("🚀 Start Multiplayer Simulation", type="primary"):
        with st.spinner("Connecting to P2P network..."):
            sim = RBESimulation(mode="multiplayer")
            try:
                asyncio.run(sim.start_multiplayer(peer_id, seed_nodes))
                st.success("✓ Connected to P2P network!")
                st.session_state['multiplayer_active'] = True
                st.session_state['simulation'] = sim
            except Exception as e:
                st.error(f"✗ Failed to connect: {e}")
                st.info("Falling back to single-player mode...")
    
    if st.session_state.get('multiplayer_active'):
        st.divider()
        render_network_status()
        render_simulation_controls()

def render_network_status():
    """Show P2P network status"""
    st.subheader("Network Status")
    
    sim = st.session_state.get('simulation')
    if not sim or not sim.p2p_network:
        return
    
    network = sim.p2p_network
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Connected Peers", len(network.peers))
    col2.metric("Current Tick", network.current_tick)
    col3.metric("Network Health", "Healthy" if len(network.peers) > 0 else "Isolated")
    col4.metric("Consensus", "✓ Synced" if sim.lockstep_engine.divergence_count == 0 else "⚠️ Diverged")
    
    with st.expander("View Connected Peers"):
        for peer_id, peer_info in network.peers.items():
            st.text(f"• {peer_id} - {peer_info.address}:{peer_info.port} (latency: {peer_info.latency_ms}ms)")

def render_simulation_controls():
    """Simulation control panel"""
    st.subheader("Simulation Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⏸️ Pause Simulation"):
            st.session_state['simulation'].lockstep_engine.stop()
    
    with col2:
        if st.button("▶️ Resume Simulation"):
            asyncio.run(st.session_state['simulation'].lockstep_engine.start())
    
    with col3:
        if st.button("🔄 Force Resync"):
            asyncio.run(st.session_state['simulation'].lockstep_engine._resync())
