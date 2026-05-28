import numpy as np
from src.python.sph_naive import step as step_naive
from src.python.sph_hashed import step as step_hashed
import sys
sys.path.insert(0, 'viz')
from ascii_renderer import render

mode = sys.argv[1] if len(sys.argv) > 1 else "viz-hashed"
mode = sys.argv[1] if len(sys.argv) > 1 else "viz-naive"
mode = sys.argv[1] if len(sys.argv) > 1 else "stats"



h = 0.05
dt = 0.001
masses = 1.0
mu = 0.1
k = 10.0
rho0 = 50.0
x = np.linspace(0,0.3,15)
y = np.linspace(0,0.6,30)

xx, yy = np.meshgrid(x, y)
positions = np.column_stack([xx.ravel(), yy.ravel()])
velocities = np.zeros_like(positions)


if mode == "stats":
    positions_init = positions.copy()
    velocities_init = velocities.copy()
    for t in range(100):
        positions, velocities = step_naive(positions,velocities,masses,h,dt,mu,k,rho0)
        if t % 5 == 0:
            print(f"t={t} centroide-naive={positions.mean(axis=0)}")



    positions = positions_init.copy()
    velocities = velocities_init.copy()
    for t in range(100):
        positions, velocities = step_hashed(positions,velocities,masses,h,dt,mu,k,rho0)
        if t % 5 == 0:
            print(f"t={t} centroide-hashed={positions.mean(axis=0)}")

elif mode == "viz-naive":
    for t in range(100):
        positions, velocities = step_naive(positions,velocities,masses,h,dt,mu,k,rho0)
        if t % 5 == 0:
            print(f"\nt={t}")
            print(render(positions))


elif mode == "viz-hashed":
    for t in range(100):
        positions, velocities = step_hashed(positions,velocities,masses,h,dt,mu,k,rho0)
        if t % 5 == 0:
            print(f"\nt={t}")
            print(render(positions))
