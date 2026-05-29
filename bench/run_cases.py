import numpy as np
import time
import argparse
import sys
 
sys.path.insert(0, 'build')
 
# ── helpers ──────────────────────────────────────────────────────────────────
 
def run_python(fn, positions_init, velocities_init, masses, h, dt, mu, k, rho0, N):
    positions  = positions_init.copy()
    velocities = velocities_init.copy()
    t0 = time.perf_counter()
    for _ in range(N):
        positions, velocities = fn(positions, velocities, masses, h, dt, mu, k, rho0)
    return time.perf_counter() - t0
 
 
def run_hpc(fn, positions_init, velocities_init, N_particles, masses, h, dt, mu, k, rho0, N):
    pos_x = positions_init[:, 0].astype(np.float32).copy()
    pos_y = positions_init[:, 1].astype(np.float32).copy()
    vel_x = velocities_init[:, 0].astype(np.float32).copy()
    vel_y = velocities_init[:, 1].astype(np.float32).copy()
    t0 = time.perf_counter()
    for _ in range(N):
        fn(pos_x, pos_y, vel_x, vel_y, N_particles, masses, h, dt, mu, k, rho0)
    return time.perf_counter() - t0
 
 
def table(title, rows, col_headers):
    """Print a simple fixed-width table."""
    col_w = max(18, max(len(h) for h in col_headers) + 2)
    row_label_w = max(20, max(len(r[0]) for r in rows) + 2)
    sep = "─" * (row_label_w + col_w * len(col_headers))
    print(f"\n{'─'*4} {title} {'─'*4}")
    header = f"{'Implementation':<{row_label_w}}" + "".join(f"{h:>{col_w}}" for h in col_headers)
    print(header)
    print(sep)
    for row in rows:
        label, *vals = row
        print(f"{label:<{row_label_w}}" + "".join(f"{v:>{col_w}}" for v in vals))
    print(sep)
 
 
# ── main ─────────────────────────────────────────────────────────────────────
 
def main():
    parser = argparse.ArgumentParser(description="SPH benchmark")
    parser.add_argument("--funcs", nargs="+",
                        choices=["naive", "hashed", "hpc", "neon", "neon_omp"],
                        default=["naive", "hashed", "hpc", "neon", "neon_omp"],
                        help="Which implementations to run (default: all)")
    parser.add_argument("--nx",    type=int,   default=15,    help="Grid points in x (default 15)")
    parser.add_argument("--ny",    type=int,   default=30,    help="Grid points in y (default 30)")
    parser.add_argument("--steps", type=int,   default=100,   help="Simulation steps (default 100)")
    parser.add_argument("--compare-nx", nargs="+", type=int,
                        help="Run comparison across these nx values (ny and steps fixed)")
    parser.add_argument("--compare-ny", nargs="+", type=int,
                        help="Run comparison across these ny values (nx and steps fixed)")
    args = parser.parse_args()
 
    # shared physics params
    h, dt, masses, mu, k, rho0 = 0.05, 0.001, 1.0, 0.1, 10.0, 50.0
    N = args.steps
 
    # lazy imports so missing modules only fail if the impl is requested
    impls = {}
    if "naive" in args.funcs:
        from src.python.sph_naive import step as step_naive
        impls["naive"] = ("python", step_naive)
    if "hashed" in args.funcs:
        from src.python.sph_hashed import step as step_hashed
        impls["hashed"] = ("python", step_hashed)
 
    import hpc_sph
    if "hpc" in args.funcs:
        impls["hpc"] = ("hpc", hpc_sph.step)
    if "neon" in args.funcs:
        impls["neon"] = ("hpc", hpc_sph.step_neon)
    if "neon_omp" in args.funcs:
        impls["neon_omp"] = ("hpc", hpc_sph.step_neon_omp)
 
    # ── single-run mode ───────────────────────────────────────────────────────
    if not args.compare_nx and not args.compare_ny:
        x = np.linspace(0, 0.3, args.nx)
        y = np.linspace(0, 0.6, args.ny)
        xx, yy = np.meshgrid(x, y)
        positions_init  = np.column_stack([xx.ravel(), yy.ravel()])
        velocities_init = np.zeros_like(positions_init)
        N_particles = len(positions_init)
 
        print(f"\nGrid: {args.nx}x{args.ny}  ({N_particles} particles)  steps={N}")
        times = {}
        for name, (kind, fn) in impls.items():
            if kind == "python":
                t = run_python(fn, positions_init, velocities_init,
                               masses, h, dt, mu, k, rho0, N)
            else:
                t = run_hpc(fn, positions_init, velocities_init,
                            N_particles, masses, h, dt, mu, k, rho0, N)
            times[name] = t
            print(f"  {name:<12}: {t:.3f}s")
 
        _print_speedup_tables(times)
 
    # ── compare-nx mode ───────────────────────────────────────────────────────
    if args.compare_nx:
        _compare("nx", args.compare_nx, args.ny, N, impls,
                 h, dt, masses, mu, k, rho0)
 
    # ── compare-ny mode ───────────────────────────────────────────────────────
    if args.compare_ny:
        _compare("ny", args.compare_ny, args.nx, N, impls,
                 h, dt, masses, mu, k, rho0)
 
 
def _compare(vary, values, fixed, N, impls, h, dt, masses, mu, k, rho0):
    """Run all implementations for each value of the varied dimension."""
    print(f"\n{'─'*40}")
    print(f"Comparing across {vary} values: {values}")
 
    all_results = {}   # name -> list of times
    labels = []
 
    for v in values:
        nx, ny = (v, fixed) if vary == "nx" else (fixed, v)
        x = np.linspace(0, 0.3, nx)
        y = np.linspace(0, 0.6, ny)
        xx, yy = np.meshgrid(x, y)
        positions_init  = np.column_stack([xx.ravel(), yy.ravel()])
        velocities_init = np.zeros_like(positions_init)
        N_particles = len(positions_init)
        labels.append(f"{vary}={v} ({N_particles}p)")
 
        for name, (kind, fn) in impls.items():
            if kind == "python":
                t = run_python(fn, positions_init, velocities_init,
                               masses, h, dt, mu, k, rho0, N)
            else:
                t = run_hpc(fn, positions_init, velocities_init,
                            N_particles, masses, h, dt, mu, k, rho0, N)
            all_results.setdefault(name, []).append(t)
 
    # Table 1: absolute times
    rows = []
    for name, times in all_results.items():
        rows.append([name] + [f"{t:.3f}s" for t in times])
    table("Tiempo total (s)", rows, labels)
 
    # Table 2: speedup vs first implementation
    baseline_name = list(all_results.keys())[0]
    baseline_times = all_results[baseline_name]
    rows2 = []
    for name, times in all_results.items():
        speedups = [f"{b/t:.2f}x" for b, t in zip(baseline_times, times)]
        rows2.append([name] + speedups)
    table(f"Speedup vs {baseline_name}", rows2, labels)
 
 
def _print_speedup_tables(times: dict):
    names = list(times.keys())
    if len(names) < 2:
        return
 
    # Table 1: absolute times
    rows = [[n, f"{times[n]:.3f}s"] for n in names]
    table("Tiempo total", rows, ["Tiempo (s)"])
 
    # Table 2: pairwise speedup matrix  (row = baseline, col = compared)
    #   cell[i][j] = times[i] / times[j]  → >1 means row is slower than col
    col_w = max(10, max(len(n) for n in names) + 2)
    row_label_w = max(12, max(len(n) for n in names) + 2)
    sep = "─" * (row_label_w + col_w * len(names))
    print(f"\n{'─'*4} Speedup matrix  (fila / columna) {'─'*4}")
    print(f"  >1.0x  → fila es más lenta que columna")
    print(f"  <1.0x  → fila es más rápida que columna\n")
    header = f"{'':>{row_label_w}}" + "".join(f"{n:>{col_w}}" for n in names)
    print(header)
    print(sep)
    for row_name in names:
        cells = []
        for col_name in names:
            if row_name == col_name:
                cells.append(f"{'—':>{col_w}}")
            else:
                sp = times[row_name] / times[col_name]
                cells.append(f"{sp:>{col_w-1}.2f}x")
        print(f"{row_name:>{row_label_w}}" + "".join(cells))
    print(sep)
 
 
if __name__ == "__main__":
    main()
