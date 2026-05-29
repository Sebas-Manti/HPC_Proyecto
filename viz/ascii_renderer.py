import sys
import os
import numpy as np
 
_COLOUR = sys.stdout.isatty() and os.environ.get("TERM", "") != "dumb"
 
_RST = "\033[0m"
 
def _ansi(code: str, text: str) -> str:
    return f"\033[{code}m{text}{_RST}" if _COLOUR else text
 
_POP_COLOUR = {
    0: "",          # space – never coloured
    1: "2;34",      # dim blue
    2: "34",        # blue
    3: "1;36",      # bold cyan
    4: "1;97",      # bold white
}
 

_CHAR_TABLE = " '`-.|//,\\|\\_\\/#"
assert len(_CHAR_TABLE) == 16
 
 
def render(
    positions,
    walls=None,
    velocities=None,
    step: int  = 0,
    width: int  = 78,
    height: int = 22,
    domain_x: tuple = (0.0, 1.0),
    domain_y: tuple = (0.0, 1.0),
    label: str = "",
) -> str:
    positions = np.asarray(positions, dtype=float)
    # Drop NaN/Inf particles (physics blow-up)
    valid = np.isfinite(positions).all(axis=1)
    positions = positions[valid]
    N  = len(positions)
    xmin, xmax = domain_x
    ymin, ymax = domain_y
    dx = xmax - xmin or 1.0
    dy = ymax - ymin or 1.0

    buf = np.zeros((height + 1, width + 1), dtype=np.uint8)
 
    vheight = height * 2
 
    def _splat(pos, bit_pattern=0b1111):
        """Write a particle's 4 bits into buf."""
        col_f = (pos[0] - xmin) / dx * (width  - 1)
        row_f = (1.0 - (pos[1] - ymin) / dy) * (vheight - 1)
 
        if not (np.isfinite(col_f) and np.isfinite(row_f)):
            return
 
        col = int(col_f)
        row = int(row_f) // 2 
 
        if not (0 <= col < width - 1 and 0 <= row < height - 1):
            return
 

        sub = int(row_f) % 2
 
        if sub == 0:
            if bit_pattern & 0b1000: buf[row    ][col    ] |= 8
            if bit_pattern & 0b0100: buf[row    ][col + 1] |= 4
            if bit_pattern & 0b0010: buf[row + 1][col    ] |= 2
            if bit_pattern & 0b0001: buf[row + 1][col + 1] |= 1
        else:
            if bit_pattern & 0b1000: buf[row + 1][col    ] |= 8
            if bit_pattern & 0b0100: buf[row + 1][col + 1] |= 4
            if bit_pattern & 0b0010: buf[row + 2][col    ] |= 2
            if bit_pattern & 0b0001: buf[row + 2][col + 1] |= 1
 
    for pos in positions:
        _splat(pos)
 
    if walls is not None:
        for pos in np.asarray(walls, dtype=float):
            _splat(pos, 0b1111)
 
    lines = []
 
    # header bar
    N_str     = f"N={N}"
    step_str  = f"step={step:>4}"
    impl_str  = f"[{label}]" if label else ""
    title     = f" SPH Fluid  {impl_str}  {step_str}  {N_str} "
    title_pad = title[:width].ljust(width)
    lines.append(_ansi("1;44", title_pad))   
    for r in range(height):
        row_chars = []
        for c in range(width):
            val = int(buf[r][c])
            ch  = _CHAR_TABLE[val]
            if _COLOUR and val > 0:
                pop  = bin(val).count('1')
                code = _POP_COLOUR.get(pop, "34")
                ch   = _ansi(code, ch)
            row_chars.append(ch)
        lines.append("".join(row_chars))
 
    if velocities is not None and len(velocities):
        spd = np.linalg.norm(np.asarray(velocities, dtype=float), axis=1)
        stats = (f" cx={positions[:,0].mean():.3f}"
                 f"  cy={positions[:,1].mean():.3f}"
                 f"  vmax={spd.max():.3f}"
                 f"  vmean={spd.mean():.3f} ")
    else:
        stats = (f" cx={positions[:,0].mean():.3f}"
                 f"  cy={positions[:,1].mean():.3f} ")
    stats_pad = stats[:width].ljust(width)
    lines.append(_ansi("2;37", stats_pad))   # dim grey
 
    return "\n".join(lines)
 
 
 
def load_scene(path: str, domain_x=(0.0, 1.0), domain_y=(0.0, 1.0)):
    """
    Parse an Endoh-style scene .txt file.
 
    Returns
    -------
    fluid_pos : (N,2) float array   – initial fluid particle positions
    wall_pos  : (M,2) float array   – wall particle positions
    """
    with open(path) as f:
        raw_lines = f.read().splitlines()
 
    if not raw_lines:
        return np.zeros((0, 2)), np.zeros((0, 2))
 
    nrows = len(raw_lines)
    ncols = max(len(l) for l in raw_lines)
 
    fluid, walls = [], []
    xmin, xmax = domain_x
    ymin, ymax = domain_y
 
    for r, line in enumerate(raw_lines):
        for c, ch in enumerate(line):
            if ch == ' ':
                continue
            x = xmin + (c + 0.5) / ncols * (xmax - xmin)
            y = ymax - (r + 0.5) / nrows * (ymax - ymin)
            if ch == '#':
                walls.append([x, y])
            else:
                fluid.append([x, y])
 
    return (np.array(fluid, dtype=float) if fluid else np.zeros((0, 2)),
            np.array(walls, dtype=float) if walls else np.zeros((0, 2)))
 
 
 
def dam_break_scene(nx=15, ny=30, domain_x=(0.0, 1.0), domain_y=(0.0, 1.0)):
    """
    Classic dam-break: fluid column on the left, open right side.
    Returns fluid_positions, wall_positions (empty – walls enforced by physics).
    """
    xmin, xmax = domain_x
    ymin, ymax = domain_y
    x = np.linspace(xmin + 0.02, xmin + (xmax - xmin) * 0.32, nx)
    y = np.linspace(ymin + 0.02, ymin + (ymax - ymin) * 0.62, ny)
    xx, yy = np.meshgrid(x, y)
    return np.column_stack([xx.ravel(), yy.ravel()])
 
 
 
def clear_screen():
    sys.stdout.write("\033[H")
    sys.stdout.flush()
 
def hide_cursor():
    if _COLOUR:
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
 
def show_cursor():
    if _COLOUR:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()