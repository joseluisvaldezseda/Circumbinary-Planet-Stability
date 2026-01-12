import streamlit as st
import numpy as np
import scipy.integrate as spi
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Stable Orbit Simulator", layout="wide")

# CSS para tema oscuro
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div.stButton > button:first-child { background-color: #2ecc71; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CONTROLES LATERALES ---
st.sidebar.header("Simulation Parameters")
pos_x = st.sidebar.slider("Initial Position X (AU)", 1.0, 5.0, 2.8, 0.1)
vel_y = st.sidebar.slider("Initial Velocity (Orbital)", 0.05, 0.6, 0.13, 0.01)
tiempo_sim = st.sidebar.slider("Observation Time", 5, 200, 100)

# --- CONSTANTES FÍSICAS ---
G, m_nd, r_nd, v_nd, t_nd = 6.67408e-11, 1.989e+30, 5e+12, 30000, 79.91*365*24*3600*0.51
K1 = G * t_nd * m_nd / (r_nd**2 * v_nd)
K2 = v_nd * t_nd / r_nd

m1, m2 = 0.5, 1.0  # Masas de las estrellas
e, ep = 0.2, (1 - 0.2**2)**(1/2)
a1, a2 = m2 / (m1 + m2), m1 / (m1 + m2)

# --- MOTOR DE FÍSICA ---
def ThreeBodyEquations(w, t, m1, m2):
    # Estrellas siguiendo órbitas Keplerianas
    x1, y1 = -a1 * (np.cos(2*np.pi*t) - e), -ep * a1 * np.sin(2*np.pi*t)
    x2, y2 = a2 * (np.cos(2*np.pi*t) - e), ep * a2 * np.sin(2*np.pi*t)
    r1, r2, r3 = np.array([x1, y1]), np.array([x2, y2]), w[:2]
    
    r13, r23 = np.linalg.norm(r3 - r1), np.linalg.norm(r3 - r2)
    
    # Aceleración del planeta
    dv3dt = K1 * m1 * (r1 - r3) / r13**3 + K1 * m2 * (r2 - r3) / r23**3
    dr3dt = K2 * w[2:4]
    return np.concatenate((dr3dt, dv3dt))

# Cálculo de la trayectoria completa
init_params = np.array([pos_x, 0.0, 0.0, vel_y])
time_span = np.linspace(0, tiempo_sim, 2000)
sol = spi.odeint(ThreeBodyEquations, init_params, time_span, args=(m1, m2))

# Trayectorias de las estrellas
x1_p = -a1 * (np.cos(2*np.pi*time_span) - e)
y1_p = -ep * a1 * np.sin(2*np.pi*time_span)
x2_p = a2 * (np.cos(2*np.pi*time_span) - e)
y2_p = ep * a2 * np.sin(2*np.pi*time_span)

# --- RENDERIZADO DEL RESULTADO FINAL ---
st.title("Final Orbital Path Result")

col1, col2 = st.columns([2, 1])

with col1:
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Zona Habitable (Anillo verde de fondo)
    hab_zone = plt.Circle((0, 0), 3.2, color='#2ecc71', alpha=0.1)
    ax.add_patch(hab_zone)
    inner_void = plt.Circle((0, 0), 1.8, color='#0e1117', alpha=1.0)
    ax.add_patch(inner_void)
    
    # Dibujar trayectorias completas (Estela)
    ax.plot(x1_p, y1_p, color="#00d4ff", lw=0.5, alpha=0.3) # Órbita Estrella A
    ax.plot(x2_p, y2_p, color="#f1c40f", lw=0.5, alpha=0.3) # Órbita Estrella B
    ax.plot(sol[:, 0], sol[:, 1], color="white", lw=1, alpha=0.8, label="Planet Path")
    
    # Dibujar posiciones finales
    # Estrella A
    ax.scatter(x1_p[-1], y1_p[-1], color="#00d4ff", s=100, edgecolors="white", label="Star A")
    # Estrella B
    ax.scatter(x2_p[-1], y2_p[-1], color="#f1c40f", s=180, edgecolors="white", label="Star B")
    # Planeta
    ax.scatter(sol[-1, 0], sol[-1, 1], color="#e74c3c", s=50, edgecolors="white", label="Planet")
    
    # Formato del gráfico
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.set_aspect('equal')
    ax.axis('off')
    st.pyplot(fig)

with col2:
    # --- ANÁLISIS FINAL ---
    dist = np.sqrt(sol[:,0]**2 + sol[:,1]**2)
    is_stable = np.max(dist) < 8.0 and np.min(dist) > 0.4

    st.subheader("Stability Analysis")
    
    if is_stable:
        st.success(f"✨ Stable orbit detected over {tiempo_sim} units.")
        avg_d = np.mean(dist)
        if 1.8 <= avg_d <= 3.2:
            st.balloons()
            st.info("🌍 Habitable: The planet stayed within the liquid water zone.")
        else:
            st.warning("🌌 Non-Habitable: The orbit is stable but too far or too close to the stars.")
    else:
        st.error("💥 System Instability: The planet was ejected from the system.")

    st.write(f"**Max Distance:** {np.max(dist):.2f} AU")
    st.write(f"**Min Distance:** {np.min(dist):.2f} AU")

st.markdown("---")
st.markdown("**Note:** The white line represents the total path traveled by the planet during the selected time.")
