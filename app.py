import streamlit as st
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from matplotlib import animation
import base64
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="EventHorizon | N-Body Simulator",
    page_icon="🌌",
    layout="wide"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4A90E2; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🌌 EventHorizon: Galactic N-Body Lab")
st.markdown("""
This simulator uses **Newtonian Physics** to model the interaction of multiple celestial bodies. 
By calculating the **gravitational tensors** between $N$ bodies, we can simulate the formation of 
vortices, galactic disks, and orbital resonances.
""")

# --- SIDEBAR PARAMETERS ---
st.sidebar.header("🚀 Simulation Command Center")

with st.sidebar.expander("Physics Constants", expanded=True):
    n_bodies = st.sidebar.slider("Number of Stars (N)", 2, 60, 20)
    sim_time = st.sidebar.slider("Time Span (Dimensionless)", 1.0, 50.0, 15.0)
    g_force = st.sidebar.select_slider("Gravitational Strength", options=[1e-11, 6.67e-11, 1e-10, 5e-10], value=6.67e-11)
    softening = st.sidebar.slider("Softening Factor (Prevents Explosions)", 0.01, 0.5, 0.15)

with st.sidebar.expander("Galaxy Generation (Vortex)", expanded=True):
    mass_mean = st.sidebar.number_input("Average Star Mass (Solar Masses)", 0.1, 10.0, 1.0)
    disk_radius = st.sidebar.slider("Initial Disk Radius", 1.0, 10.0, 5.0)
    vortex_strength = st.sidebar.slider("Orbital Velocity Factor", 0.0, 2.5, 1.2)
    central_bh = st.sidebar.checkbox("Add Central Supermassive Black Hole", value=True)

# --- PHYSICAL CONSTANTS & NORMALIZATION ---
# Using Alpha Centauri reference system provided in your prompt
M_ND = 1.989e+30    # kg (Sun)
R_ND = 5.326e+12    # m 
V_ND = 30000        # m/s
T_ND = 79.91 * 365 * 24 * 3600 * 0.51

K1 = g_force * T_ND * M_ND / ((R_ND ** 2) * V_ND)
K2 = V_ND * T_ND / R_ND

# --- CORE PHYSICS ENGINE ---
def n_body_derivs(state, t, n, m_stars):
    # state contains [x1,y1,z1... xn,yn,zn, vx1,vy1,vz1... vxn,vyn,vzn]
    r = state[:3*n].reshape((n, 3))
    v = state[3*n:].reshape((n, 3))
    
    drdt = K2 * v
    dvdt = np.zeros((n, 3))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                diff = r[j] - r[i]
                # Gravitational softening: avoids 1/0 infinity when stars collide
                dist = np.sqrt(np.sum(diff**2) + softening**2)
                dvdt[i] += K1 * m_stars[j] * diff / (dist**3)
                
    return np.concatenate([drdt.flatten(), dvdt.flatten()])

# --- GALAXY INITIALIZER (VORTEX LOGIC) ---
def generate_vortex(n, r_max, v_factor, has_bh):
    r0 = []
    v0 = []
    m_stars = np.full(n, mass_mean)
    
    if has_bh:
        m_stars[0] = 50.0  # The central body is 50x heavier
    
    for i in range(n):
        if i == 0 and has_bh:
            r0.append([0, 0, 0])
            v0.append([0, 0, 0])
            continue
            
        # Distribution in a disk
        radius = np.random.uniform(0.5, r_max)
        angle = np.random.uniform(0, 2 * np.pi)
        
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = np.random.uniform(-0.2, 0.2) # Flattened disk
        
        # Orbital Velocity: V = sqrt(G*M / r)
        # To create a vortex, velocity must be perpendicular to the radius vector
        v_mag = v_factor * np.sqrt(m_stars.mean() / radius)
        vx = -v_mag * np.sin(angle)
        vy = v_mag * np.cos(angle)
        vz = np.random.uniform(-0.02, 0.02)
        
        r0.append([x, y, z])
        v0.append([vx, vy, vz])
        
    return np.array(r0).flatten(), np.array(v0).flatten(), m_stars

# --- SIMULATION EXECUTION ---
if st.sidebar.button("✨ Run Simulation"):
    with st.status("Solving Differential Equations...", expanded=True) as status:
        st.write("Initializing stellar positions...")
        r_init, v_init, m_stars = generate_vortex(n_bodies, disk_radius, vortex_strength, central_bh)
        w0 = np.concatenate([r_init, v_init])
        
        t_steps = 300
        t = np.linspace(0, sim_time, t_steps)
        
        st.write("Integrating trajectories (Scipy ODEINT)...")
        sol = odeint(n_body_derivs, w0, t, args=(n_bodies, m_stars))
        
        st.write("Rendering 3D Animation...")
        # Animation setup
        fig = plt.figure(figsize=(10, 10), facecolor='black')
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor('black')
        
        # Hide axes for cinematic feel
        ax.set_axis_off()
        
        # Dynamic trails and star points
        lines = [ax.plot([], [], [], '-', lw=0.8, alpha=0.5, color='cyan')[0] for _ in range(n_bodies)]
        points = [ax.plot([], [], [], 'o', markersize=3, color='white')[0] for _ in range(n_bodies)]
        
        if central_bh:
            points[0].set_color('yellow')
            points[0].set_markersize(6)

        def init():
            limit = disk_radius * 1.5
            ax.set_xlim(-limit, limit)
            ax.set_ylim(-limit, limit)
            ax.set_zlim(-limit/2, limit/2)
            return lines + points

        def animate(i):
            for body in range(n_bodies):
                idx = body * 3
                # Update trails
                x_data = sol[:i, idx]
                y_data = sol[:i, idx+1]
                z_data = sol[:i, idx+2]
                lines[body].set_data(x_data, y_data)
                lines[body].set_3d_properties(z_data)
                
                # Update current position
                points[body].set_data
