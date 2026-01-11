import streamlit as st
import numpy as np
import scipy.integrate as spi
import matplotlib.pyplot as plt
import time

# Page Configuration
st.set_page_config(page_title="Stable Orbit Simulator", layout="wide")

# CSS for a clean Dark Theme
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div.stButton > button:first-child { background-color: #2ecc71; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Parameters")
# Defaults set for a "Beautiful Orbit"
pos_x = st.sidebar.slider("Initial Position X (AU)", 1.0, 5.0, 2.8, 0.1)
vel_y = st.sidebar.slider("Initial Velocity (Orbital)", 0.05, 0.6, 0.13, 0.01)
tiempo_sim = st.sidebar.slider("Observation Time", 5, 100, 40)
velocidad_animacion = st.sidebar.select_slider("Animation Speed", options=["Slow", "Normal", "Fast"], value="Normal")

# Speed Mapping
step_map = {"Slow": 2, "Normal": 5, "Fast": 10}
anim_step = step_map[velocidad_animacion]

# --- PHYSICAL CONSTANTS ---
G, m_nd, r_nd, v_nd, t_nd = 6.67408e-11, 1.989e+30, 5e+12, 30000, 79.91*365*24*3600*0.51
K1 = G * t_nd * m_nd / (r_nd**2 * v_nd)
K2 = v_nd * t_nd / r_nd

m1, m2 = 0.5, 1.0  # Star masses
e, ep = 0.2, (1 - 0.2**2)**(1/2)
a1, a2 = m2 / (m1 + m2), m1 / (m1 + m2)

# --- PHYSICS ENGINE ---
def ThreeBodyEquations(w, t, m1, m2):
    # Stars following Keplerian orbits
    x1, y1 = -a1 * (np.cos(2*np.pi*t) - e), -ep * a1 * np.sin(2*np.pi*t)
    x2, y2 = a2 * (np.cos(2*np.pi*t) - e), ep * a2 * np.sin(2*np.pi*t)
    r1, r2, r3 = np.array([x1, y1]), np.array([x2, y2]), w[:2]
    
    r13, r23 = np.linalg.norm(r3 - r1), np.linalg.norm(r3 - r2)
    
    # Planet acceleration
    dv3dt = K1 * m1 * (r1 - r3) / r13**3 + K1 * m2 * (r2 - r3) / r23**3
    dr3dt = K2 * w[2:4]
    return np.concatenate((dr3dt, dv3dt))

# Pre-calculating the entire trajectory
init_params = np.array([pos_x, 0.0, 0.0, vel_y])
time_span = np.linspace(0, tiempo_sim, 1000)
sol = spi.odeint(ThreeBodyEquations, init_params, time_span, args=(m1, m2))

# Stars trajectories
x1_p = -a1 * (np.cos(2*np.pi*time_span) - e)
y1_p = -ep * a1 * np.sin(2*np.pi*time_span)
x2_p = a2 * (np.cos(2*np.pi*time_span) - e)
y2_p = ep * a2 * np.sin(2*np.pi*time_span)

# --- REAL-TIME ANIMATION ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<h2 style='text-align: center;'></h2>", unsafe_allow_html=True)
    plot_placeholder = st.empty()
    
    for i in range(0, len(time_span), anim_step):
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # Habitable Zone (Green Ring)
        hab_zone = plt.Circle((0, 0), 3.2, color='#2ecc71', alpha=0.1)
        ax.add_patch(hab_zone)
        inner_void = plt.Circle((0, 0), 1.8, color='#0e1117', alpha=1.0)
        ax.add_patch(inner_void)
        
        # Draw Trarails (Faint stardust)
        ax.plot(sol[:i, 0], sol[:i, 1], color="white", lw=0.8, alpha=0.4)
        
        # DRAW STARS (With Glow Effect)
        # Star A (Blue)
        ax.scatter(x1_p[i], y1_p[i], color="#00d4ff", s=150, alpha=0.2) # Outer Glow
        ax.scatter(x1_p[i], y1_p[i], color="#00d4ff", s=50, edgecolors="white", label="Star A")
        
        # Star B (Gold/Yellow - Larger)
        ax.scatter(x2_p[i], y2_p[i], color="#f1c40f", s=250, alpha=0.2) # Outer Glow
        ax.scatter(x2_p[i], y2_p[i], color="#f1c40f", s=100, edgecolors="white", label="Star B")
        
        # DRAW PLANET (Small and distinct)
        ax.scatter(sol[i, 0], sol[i, 1], color="#e74c3c", s=20, edgecolors="white", label="Planet")
        
        # Formatting
        ax.set_xlim(-6, 6)
        ax.set_ylim(-6, 6)
        ax.axis('off') 
        
        plot_placeholder.pyplot(fig)
        plt.close(fig)

# --- FINAL ANALYSIS (EN) ---
dist = np.sqrt(sol[:,0]**2 + sol[:,1]**2)
is_stable = np.max(dist) < 8.0 and np.min(dist) > 0.4

if is_stable:
    st.success(f"✨ Simulation Complete: Stable orbit detected over {tiempo_sim} time units.")
    avg_d = np.mean(dist)
    if 1.8 <= avg_d <= 3.2:
        st.balloons()
        st.info("🌍 Life Potential: The planet is staying within the Habitable Zone!")
    else:
        st.warning("🌌 Stable but Cold/Hot: The planet is outside the Habitable Zone.")
else:
    st.error("💥 System Instability: The planet was ejected or collided with a star.")

st.markdown("""
**How to use:**
1. Use the sidebar to change the starting conditions.
2. **Blue Star (A)** is smaller, **Golden Star (B)** is more massive.
3. The **Green Ring** represents the liquid water zone.
4. Aim for a trajectory that stays inside the green ring without being thrown away!
""")