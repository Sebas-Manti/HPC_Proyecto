import pytest
import numpy as np
from scipy.integrate import quad
from src.python.kernels import W

def test_W_normalization():
    
    resultado, _ = quad(lambda r: W(r, 1.0) * 2*np.pi*r, 0, 1.0)
    assert resultado == pytest.approx(1.0, abs=1e-6)

def test_W_positive():
    x = np.linspace(0.0,1.0,20)
    for i in x:
        
        assert W(i,1.0) >= 0

def test_W_zero_outside():
    x = [1.1, 1.5, 2.0]
    for i in x:
        assert W(i,1.0) == 0