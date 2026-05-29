import argparse
import sys
import time
import numpy as np

sys.path.insert(0, 'build')
sys.path.insert(0, 'viz')

from ascii_renderer import render, clear_screen

H    = 0.05
DT   = 0.001
MASS = 1.0
MU   = 0.1
K    = 10.0
RHO0 = 50.0



class PythonImpl:
    def __init__(self, fn, name: str):
        self.fn   = fn
        self.name = name

    def init(self, positions_init, velocities_init):
        self.pos = positions_init.copy()
        self.vel = velocities_init.copy()

    def step(self):
        self.pos, self.vel = self.fn(
            self.pos, self.vel, MASS, H, DT, MU, K, RHO0
        )

    @property
    def positions(self):
        return self.pos

    @property
    def velocities(self):
        return self.vel


class HpcImpl:
    def __init__(self, fn, name: str):
        self.fn   = fn
        self.name = name

    def init(self, positions_init, velocities_init):
        self.pos_x = positions_init[:, 0].astype(np.float32).copy()
        self.pos_y = positions_init[:, 1].astype(np.float32).copy()
        self.vel_x = velocities_init[:, 0].astype(np.float32).copy()
        self.vel_y = velocities_init[:, 1].astype(np.float32).copy()
        self._N    = len(self.pos_x)

    def step(self):
        self.fn(
            self.pos_x, self.pos_y,
            self.vel_x, self.vel_y,
            self._N, MASS, H, DT, MU, K, RHO0,
        )

    @property
    def positions(self):
        return np.column_stack([self.pos_x, self.pos_y])

    @property
    def velocities(self):
        return np.column_stack([self.vel_x, self.vel_y])



def build_impls(requested: list[str]) -> dict:
    impls = {}
    if "naive" in requested or "hashed" in requested:
        if "naive" in requested:
            from src.python.sph_naive import step as _naive
            impls["naive"] = PythonImpl(_naive, "naive")
        if "hashed" in requested:
            from src.python.sph_hashed import step as _hashed
            impls["hashed"] = PythonImpl(_hashed, "hashed")

    cpp_needed = [n for n in ("hpc", "neon", "neon_omp") if n in requested]
    if cpp_needed:
        import hpc_sph
        if "hpc" in cpp_needed:
            impls["hpc"]      = HpcImpl(hpc_sph.step,          "hpc")
        if "neon" in cpp_needed:
            impls["neon"]     = HpcImpl(hpc_sph.step_neon,     "neon")
        if "neon_omp" in cpp_needed:
            impls["neon_omp"] = HpcImpl(hpc_sph.step_neon_omp, "neon_omp")

    return impls



def mode_stats(impls, positions_init, velocities_init, steps, every):
    print(f"\n{'─'*60}")
    print(f"  SPH stats  |  {steps} steps  |  N={len(positions_init)}")
    print(f"{'─'*60}")
    for name, impl in impls.items():
        impl.init(positions_init, velocities_init)
        for t in range(steps):
            impl.step()
            if t % every == 0:
                c = impl.positions.mean(axis=0)
                print(f"  [{name:<10}]  t={t:>4}  centroid=({c[0]:.4f}, {c[1]:.4f})")
        print()


def mode_viz(impls, positions_init, velocities_init, steps, every,
             live: bool, delay_ms: int, domain_x, domain_y):
    """Run one impl at a time in animated ASCII."""
    for name, impl in impls.items():
        impl.init(positions_init, velocities_init)
        if live:
            print("\033[2J\033[H", end="")

        for t in range(steps):
            impl.step()
            if t % every == 0:
                frame = render(
                    impl.positions,
                    velocities = impl.velocities,
                    step       = t,
                    label      = name,
                    domain_x   = domain_x,
                    domain_y   = domain_y,
                )
                if live:
                    clear_screen()
                    sys.stdout.write(frame + "\n")
                    sys.stdout.flush()
                    time.sleep(delay_ms / 1000.0)
                else:
                    print(f"\n── {name}  t={t} ──")
                    print(frame)



def parse_args():
    p = argparse.ArgumentParser(description="SPH ASCII visualizer")
    p.add_argument("mode", nargs="?",
                   choices=["stats", "viz-live", "viz-frames"],
                   default="stats")
    p.add_argument("--impl", nargs="+",
                   choices=["naive", "hashed", "hpc", "neon", "neon_omp"],
                   default=["hpc"],
                   help="Implementation(s) to run  (default: hpc)")
    p.add_argument("--nx",    type=int, default=15,
                   help="Grid points in x  (default 15)")
    p.add_argument("--ny",    type=int, default=30,
                   help="Grid points in y  (default 30)")
    p.add_argument("--steps", type=int, default=200,
                   help="Simulation steps  (default 200)")
    p.add_argument("--every", type=int, default=5,
                   help="Render every K steps  (default 5)")
    p.add_argument("--delay", type=int, default=50,
                   help="ms between frames in viz-live  (default 50)")
    return p.parse_args()


def main():
    args  = parse_args()
    impls = build_impls(args.impl)

    if not impls:
        print("No valid implementations requested.")
        sys.exit(1)

    x = np.linspace(0.0, 0.3,  args.nx)
    y = np.linspace(0.0, 0.6,  args.ny)
    xx, yy         = np.meshgrid(x, y)
    positions_init  = np.column_stack([xx.ravel(), yy.ravel()])
    velocities_init = np.zeros_like(positions_init)

    domain_x = (0.0, 1.0)
    domain_y = (0.0, 1.0)

    if args.mode == "stats":
        mode_stats(impls, positions_init, velocities_init,
                   args.steps, args.every)

    elif args.mode in ("viz-live", "viz-frames"):
        mode_viz(
            impls, positions_init, velocities_init,
            args.steps, args.every,
            live     = (args.mode == "viz-live"),
            delay_ms = args.delay,
            domain_x = domain_x,
            domain_y = domain_y,
        )


if __name__ == "__main__":
    main()