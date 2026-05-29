"""
mode:
  viz-live     animación en vivo (default)
  viz-frames   imprime frames al stdout
  stats        imprime centroide y velocidad cada K pasos

--impl    naive | hashed | hpc | neon | neon_omp   (default: hpc)
--scene   path/to/scene.txt  o  dam_break           (default: dam_break)
--nx      puntos en x para el grid inicial           (default: 15)
--ny      puntos en y para el grid inicial           (default: 30)
--steps   pasos totales de simulación                (default: 400)
--every   renderizar cada K pasos                    (default: 3)
--delay   ms entre frames en viz-live                (default: 40)
--width   columnas del renderer                      (default: ancho terminal - 2)
--height  filas del renderer                         (default: alto terminal - 4)
"""

import argparse
import signal
import sys
import time
import numpy as np
 
sys.path.insert(0, 'build')
sys.path.insert(0, 'viz')
 
import shutil
from ascii_renderer import (
    render, dam_break_scene, load_scene,
    clear_screen, hide_cursor, show_cursor,
)
 
H    = 0.05
DT   = 0.001
MASS = 1.0
MU   = 0.1
K    = 10.0
RHO0 = 50.0
 
DOMAIN_X = (0.0, 1.0)
DOMAIN_Y = (0.0, 1.0)
 
 
 
class PythonImpl:
    def __init__(self, fn, name):
        self.fn, self.name = fn, name
 
    def init(self, pos, vel):
        self.pos, self.vel = pos.copy(), vel.copy()
 
    def step(self):
        self.pos, self.vel = self.fn(
            self.pos, self.vel, MASS, H, DT, MU, K, RHO0)
 
    @property
    def positions(self):  return self.pos
    @property
    def velocities(self): return self.vel
 
 
class HpcImpl:
    def __init__(self, fn, name):
        self.fn, self.name = fn, name
 
    def init(self, pos, vel):
        self.px = pos[:, 0].astype(np.float32).copy()
        self.py = pos[:, 1].astype(np.float32).copy()
        self.vx = vel[:, 0].astype(np.float32).copy()
        self.vy = vel[:, 1].astype(np.float32).copy()
        self._N = len(self.px)
 
    def step(self):
        self.fn(self.px, self.py, self.vx, self.vy,
                self._N, MASS, H, DT, MU, K, RHO0)
 
    @property
    def positions(self):  return np.column_stack([self.px, self.py])
    @property
    def velocities(self): return np.column_stack([self.vx, self.vy])
 
 
def build_impl(name: str):
    if name == "naive":
        from src.python.sph_naive import step as fn
        return PythonImpl(fn, "naive")
    if name == "hashed":
        from src.python.sph_hashed import step as fn
        return PythonImpl(fn, "hashed")
    import hpc_sph
    fns = {"hpc": hpc_sph.step,
           "neon": hpc_sph.step_neon,
           "neon_omp": hpc_sph.step_neon_omp}
    return HpcImpl(fns[name], name)
 
 
 
def run_viz(impl, pos_init, vel_init, walls, steps, every,
            live, delay_ms, width, height):
    impl.init(pos_init, vel_init)
 
    if live:
        hide_cursor()
        sys.stdout.write("\033[2J")
 
    def _cleanup(sig=None, frame=None):
        if live:
            show_cursor()
        sys.exit(0)
 
    signal.signal(signal.SIGINT, _cleanup)
 
    try:
        for t in range(steps):
            impl.step()
            if t % every == 0:
                frame = render(
                    impl.positions,
                    walls      = walls if len(walls) else None,
                    velocities = impl.velocities,
                    step       = t,
                    label      = impl.name,
                    width      = width,
                    height     = height,
                    domain_x   = DOMAIN_X,
                    domain_y   = DOMAIN_Y,
                )
                if live:
                    clear_screen()
                    sys.stdout.write(frame + "\n")
                    sys.stdout.flush()
                    time.sleep(delay_ms / 1000.0)
                else:
                    print(frame)
    finally:
        if live:
            show_cursor()
 
 
def run_stats(impls_names, pos_init, vel_init, steps, every):
    for name in impls_names:
        impl = build_impl(name)
        impl.init(pos_init, vel_init)
        print(f"\n── {name} ──")
        for t in range(steps):
            impl.step()
            if t % every == 0:
                c = impl.positions.mean(axis=0)
                v = np.linalg.norm(impl.velocities, axis=1).mean()
                print(f"  t={t:>4}  cx={c[0]:.4f}  cy={c[1]:.4f}  vmean={v:.4f}")
 
 
 
def main():
    tw, th = shutil.get_terminal_size((82, 28))
 
    p = argparse.ArgumentParser(description="SPH ASCII visualizer")
    p.add_argument("mode", nargs="?",
                   choices=["viz-live", "viz-frames", "stats"],
                   default="viz-live")
    p.add_argument("--impl", nargs="+",
                   choices=["naive", "hashed", "hpc", "neon", "neon_omp"],
                   default=["hpc"])
    p.add_argument("--scene",  default="dam_break",
                   help="Scene file path or 'dam_break'")
    p.add_argument("--nx",     type=int, default=15)
    p.add_argument("--ny",     type=int, default=30)
    p.add_argument("--steps",  type=int, default=400)
    p.add_argument("--every",  type=int, default=3)
    p.add_argument("--delay",  type=int, default=40,
                   help="ms between frames (viz-live only)")
    p.add_argument("--width",  type=int, default=tw - 2)
    p.add_argument("--height", type=int, default=th - 4)
    args = p.parse_args()
 
    walls = np.zeros((0, 2))
    if args.scene == "dam_break":
        pos_init = dam_break_scene(args.nx, args.ny, DOMAIN_X, DOMAIN_Y)
    else:
        pos_init, walls = load_scene(args.scene, DOMAIN_X, DOMAIN_Y)
        if len(pos_init) == 0:
            print("Scene file has no fluid particles.")
            sys.exit(1)
 
    vel_init = np.zeros_like(pos_init)
 
    if args.mode == "stats":
        run_stats(args.impl, pos_init, vel_init, args.steps, args.every)
        return
 
    for name in args.impl:
        impl = build_impl(name)
        run_viz(
            impl, pos_init, vel_init, walls,
            steps    = args.steps,
            every    = args.every,
            live     = (args.mode == "viz-live"),
            delay_ms = args.delay,
            width    = args.width,
            height   = args.height,
        )
        if args.mode == "viz-live" and len(args.impl) > 1:
            time.sleep(1.5)
 
 
if __name__ == "__main__":
    main()
