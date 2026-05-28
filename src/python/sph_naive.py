def compute_density(positions, masses, h):
    """
    Función que calcula la densidad de una partícula.

    Args: 
        positions (np.ndarray, shape (N,2)): Posición de la partícula
        masses (float): Masa de la partícula
        h (float): Radio de interacción
    
    Returns (float):
    Devuelve el valor de las densidades
    """
    pass
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
    
    Returns (np.ndarray):
    Calcula las fuerzas
    """
    pass

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
    
    Returns (float):
    Calcula cada paso
    """
    pass
    