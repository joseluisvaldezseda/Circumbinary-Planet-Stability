# Computational-Physics-Project: Binary Star System Stability

This project explores the complex gravitational dynamics of a planetary body within a binary star system. Using numerical integration and computational simulations, we aim to identify stable orbital "safe zones" for planets in circumbinary or S-type configurations.

## 🌌 Project Overview

The study focuses on a binary star system with the following characteristics:
*   **Star A:** 50% of the Sun’s mass ($0.5 M_\odot$).
*   **Star B:** Equal in mass to the Sun ($1.0 M_\odot$).
*   **Orbital Period:** 30 Earth days.

The core objective is to determine where a planet could maintain a stable orbit within this system and to describe the resulting trajectories using numerical methods.

## 🎯 Objectives

1.  **Baseline Modeling:** Implement a standard Earth-Sun simulation to calibrate the numerical integrator.
2.  **Binary Integration:** Incorporate a second stellar mass to analyze the 2-body dynamics of the stars.
3.  **Stability Mapping:** Explore planetary configurations considering:
    *   Semi-major axis.
    *   Initial eccentricity.
    *   Resonance conditions.
4.  **Safe Zone Identification:** Use stability criteria to determine regions where planets are not ejected from the system or consumed by the stars.

## 🛠️ Methodology

The project utilizes **Python** and the following scientific stack:
*   **Numerical Integration:** `scipy.integrate.odeint` for solving the coupled Newtonian differential equations.
*   **Gravitational Softening:** Implementation of a softening factor to prevent numerical singularities during close encounters.
*   **Normalization:** Physical quantities are normalized based on the Alpha Centauri reference system for better computational stability.
*   **Visualization:** An interactive **Streamlit** dashboard for real-time parameter manipulation and 2D orbital rendering.

## 🚀 Installation & Usage

### Prerequisites
Ensure you have Python 3.8+ installed.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Computational-Physics-Project.git
   cd Computational-Physics-Project
