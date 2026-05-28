import numpy as np
from src.python.sph_naive import step

h = 0.05
dt = 0.0001
masses = 1.0
mu = 0.1
k = 10.0
rho0 = 50.0
x = np.linspace(0,0.3,10)
y = np.linspace(0,0.6,10)

xx, yy = np.meshgrid(x, y)
positions = np.column_stack([xx.ravel(), yy.ravel()])
velocities = np.zeros_like(positions)

for t in range(500):
    positions, velocities = step(positions,velocities,masses,h,dt,mu,k,rho0)
    if t % 10 == 0:
        print(f"t={t}, pos[0]={positions[0]}, v[0]={velocities[0]}")
        print(f"centroide={positions.mean(axis=0)}")

