import numpy as np
import time
from src.python.sph_naive import step as step_naive
from src.python.sph_hashed import step as step_hashed
import sys
sys.path.insert(0, 'build')
import hpc_sph

h = 0.05
dt = 0.001
masses = 1.0
mu = 0.1
k = 10.0
rho0 = 50.0
x = np.linspace(0,0.3,15)
y = np.linspace(0,0.6,30)
N = 100

xx, yy = np.meshgrid(x, y)
positions = np.column_stack([xx.ravel(), yy.ravel()])
velocities = np.zeros_like(positions)
N_particles = len(positions)
positions_init = positions.copy()
velocities_init = velocities.copy()

start = time.perf_counter()
for t in range(N):
    positions, velocities = step_naive(positions,velocities,masses,h,dt,mu,k,rho0)
end = time.perf_counter()
naive_times = end - start
print(f"Naive: {end - start:.3f}s")


positions = positions_init.copy()
velocities = velocities_init.copy()

start = time.perf_counter()
for t in range(N):
    positions, velocities = step_hashed(positions,velocities,masses,h,dt,mu,k,rho0)
end = time.perf_counter()
print(f"Hashed: {end - start:.3f}s")
hashed_times = end - start

pos_x = positions_init[:, 0].astype(np.float32).copy()
pos_y = positions_init[:, 1].astype(np.float32).copy()
vel_x = velocities_init[:, 0].astype(np.float32).copy()
vel_y = velocities_init[:, 1].astype(np.float32).copy()
start = time.perf_counter()
for t in range(N):
    hpc_sph.step(pos_x, pos_y, vel_x, vel_y,N_particles,masses,h,dt,mu,k,rho0)
end = time.perf_counter()
print(f"hpc: {end - start:.3f}s")
hpc_times = end - start

pos_x = positions_init[:, 0].astype(np.float32).copy()
pos_y = positions_init[:, 1].astype(np.float32).copy()
vel_x = velocities_init[:, 0].astype(np.float32).copy()
vel_y = velocities_init[:, 1].astype(np.float32).copy()
start = time.perf_counter()
for t in range(N):
    hpc_sph.step_neon(pos_x, pos_y, vel_x, vel_y,N_particles,masses,h,dt,mu,k,rho0)
end = time.perf_counter()
print(f"hpc: {end - start:.3f}s")
neon_times = end - start

speedup_naive_v_hashed = naive_times / hashed_times
speedup_hashed_v_hpc = hashed_times / hpc_times
speedup_naive_v_hpc = naive_times / hpc_times
speedup_naive_v_neon = naive_times / neon_times
speedup_hashed_v_neon = hashed_times / neon_times
speedup_hpc_v_neon = hpc_times / neon_times


print(f"Speedup: \n speedup_naive_v_hashed {speedup_naive_v_hashed:.2f}x \n speedup_hashed_v_hpc {speedup_hashed_v_hpc:.2f}x \n speedup_naive_v_hpc {speedup_naive_v_hpc:.2f}x")
print(f"Speedup: \n speedup_naive_v_neon {speedup_naive_v_neon:.2f}x \n speedup_hashed_v_neon {speedup_hashed_v_neon:.2f}x \n speedup_hpc_v_neon {speedup_hpc_v_neon:.2f}x")
