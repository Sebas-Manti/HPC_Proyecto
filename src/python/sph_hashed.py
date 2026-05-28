def build_hash_table(positions, h):
    """
    Construye la tabla hash espacial

    Args: 
        positions (np.ndarray, shape (N,2)): Posición de la partícula
        h (float): Radio de interacción
    
    Returns (dict):
    Devuelve una tabla
    """
    pass

def query_neighbors(i, positions, hash_table, h):
    """ 
    Retorna los índices de vecinos de la partícula i
    
    Args: 
        i (int): la partícula a calcular
        positions (np.ndarray, shape (N,2)): Posición de la partícula
        hash_table (dict): Referencia espacial de las partículas
        h (float): Radio de interacción
    
    Returns (np.ndarray, shape (M,)):
    Los vecinos de la partícula i
    """
    pass

def compute_density(positions, masses, h):
    """
    Función que calcula la densidad de una partícula con relación a sus vecinos.

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
    Función que calcula las fuerzas con relación a sus vecinos.

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
    Función que calcula los pasos con relación a sus vecinos.

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