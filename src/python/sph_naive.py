import numpy as np
from src.python.kernels import W, grad_W, lap_W

def compute_density(positions, masses, h):
    """
    Función que calcula la densidad de una partícula.

    Args: 
        positions (np.ndarray, shape (N,2)): Posición de la partícula
        masses (float): Masa de la partícula
        h (float): Radio de interacción
    
    Returns (np.ndarray, shape (N,)):
    Devuelve el valor de las densidades
    """
    rho = np.zeros(len(positions))
    for i in range(len(positions)):
        for j in range(len(positions)):
            d = positions[i]-positions[j]
            r = np.linalg.norm(d)
            rho[i] = masses*W(r,h)+rho[i]

    return rho

    
def compute_forces(positions, velocities, densities, masses, h, mu, k, rho0):
    """
    Función que calcula las fuerzas.

    Args: 
        positions (np.ndarray, shape (N,2)): Posición de la partícula
        velocities (np.ndarray, shape (N,2)): Velocidad de la partícula
        densities (np.ndarray, shape (N,)): densidad de la partícula
        masses (float): Masa de la partícula
        h (float): Radio de interacción
        mu (float): coeficiente de viscocidad
        k (float): coeficiente de rigidez
        rho0 (float): Es la densidad de reposo del fluido
    
    Returns (np.ndarray, shape (N,2)):
    Calcula las fuerzas
    """
    v = velocities
    rho = densities
    g = np.array([0, -9.8])
    F = np.zeros((len(positions), 2))
    for i in range(len(positions)):
        for j in range(len(positions)):
            if i == j:
                continue
            else:
                d = positions[i]-positions[j]
                r = np.linalg.norm(d)
                if 0 < r < 2 * h:
                    p_i = k * (rho[i] - rho0)
                    p_j = k * (rho[j] - rho0)
                    F_press = -masses * (p_i + p_j) / (2 * rho[j]) * grad_W(d, h)
                    F_visc = mu * masses * (v[j] - v[i]) / rho[j] * lap_W(r, h)
                    F[i] = F[i] + F_press + F_visc
        F[i] = F[i] + rho[i] * g
    return F


def step(positions, velocities, masses, h, dt, mu, k, rho0):
    """
    Función que calcula los pasos.

    Args: 
        positions (np.ndarray, shape (N,2)): Posición de la partícula
        velocities (np.ndarray, shape (N,2)): Velocidad de la partícula
        masses (float): Masa de la partícula
        h (float): Radio de interacción
        dt (float): Es el paso temporal
        mu (float): Coeficiente de viscocidad
        k (float): Coeficiente de rigidez
        rho0 (float): Es la densidad de reposo del fluido
    
    Returns (np.ndarray, np.ndarray):
    Calcula cada paso
    """
    rho = compute_density(positions,masses,h)
    F = compute_forces(positions, velocities, rho, masses, h, mu, k, rho0)

    for i in range(len(positions)):
        velocities[i] = velocities[i] * dt + F[i]/rho[i]
        positions[i] = positions[i] + dt * velocities[i]

    for i in range(len(positions)):
        if positions[i,0] < 0 or positions[i,0]>1:
            positions[i,0] = np.clip(positions[i,0],0,1)
            velocities[i,0] = -velocities[i,0]

        elif positions[i,1] < 0 or positions[i,1]>1:
            positions[i,1] = np.clip(positions[i,1],0,1)
            velocities[i,1] = -velocities[i,1]

    return positions, velocities



    