import numpy as np

def W(r, h):
    """
    Función que calcula el valor del kernel.

    Args: 
        r (float): Distancia entre partículas
        h (float): Radio de interacción
    
    Returns (float):
    Devuelve el valor del kernel en un punto 
    """
    if 0 <= r <= h:
        return (4 / (np.pi * h**8)) * (h**2 - r**2)**3
    else:
        return 0
    

def grad_W(r_vec, h):
    """
    Función que calcula el gradiente de W.

    Args: 
        r_vec (np.ndarray, shape (2,)): vector director de la interacción
        h (float): Radio de interacción
    
    Returns (np.ndarray):
    El gradiente de W
    """
    r = np.linalg.norm(r_vec)
    if 0 <= r <= h:
        return -(945 / (32*np.pi*h**9)) * (h**2 - r**2)**2 * r_vec
    else:
        return np.zeros(2)

def lap_W(r, h):
    """
    Función que calcula el laplaciano del kernel.

    Args: 
        r (float): Distancia entre partículas
        h (float): Radio de interacción
    
    Returns (float):
    El Laplaciano de W
    """
    if 0 <= r <= h:
        return -(945 / (32*np.pi*h**9)) * (h**2 - r**2) * (3*h**2 - 7*r**2)
    else:
        return 0
    


