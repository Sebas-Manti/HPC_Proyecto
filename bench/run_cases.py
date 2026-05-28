import numpy as np
import time
from src.python.sph_naive import step as step_naive
from src.python.sph_hashed import step as step_hashed

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

positions_init = positions.copy()
velocities_init = velocities.copy()

start = time.perf_counter()
for t in range(100):
    positions, velocities = step_naive(positions,velocities,masses,h,dt,mu,k,rho0)
end = time.perf_counter()
naive_times = end - start
print(f"Naive: {end - start:.3f}s")


positions = positions_init.copy()
velocities = velocities_init.copy()

start = time.perf_counter()
for t in range(100):
    positions, velocities = step_hashed(positions,velocities,masses,h,dt,mu,k,rho0)
end = time.perf_counter()
print(f"Hashed: {end - start:.3f}s")
hashed_times = end - start

speedup = naive_times / hashed_times
print(f"Speedup: {speedup:.2f}x")
