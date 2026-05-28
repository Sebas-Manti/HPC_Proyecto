import numpy as np
from src.python.sph_naive import step
import sys
sys.path.insert(0, 'viz')
from ascii_renderer import render

h = 0.05
dt = 0.001
masses = 1.0
mu = 0.1
k = 10.0
rho0 = 50.0
x = np.linspace(0,0.3,4)
y = np.linspace(0,0.6,8)

xx, yy = np.meshgrid(x, y)
positions = np.column_stack([xx.ravel(), yy.ravel()])
velocities = np.zeros_like(positions)

for t in range(1000):
    positions, velocities = step(positions,velocities,masses,h,dt,mu,k,rho0)
    if t % 500 == 0:
        print(f"\nt={t}")
        print(render(positions))

