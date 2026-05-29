import numpy as np
import os
import sys
 
_HAS_COLOUR = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
 
_BLUE_RAMP = [17, 18, 19, 20, 21, 27, 33, 39, 45, 51]
 
def _fg(code: int, text: str) -> str:
    if not _HAS_COLOUR:
        return text
    return f"\033[38;5;{code}m{text}\033[0m"
 
def _bold(text: str) -> str:
    if not _HAS_COLOUR:
        return text
    return f"\033[1m{text}\033[0m"
 
def _dim(text: str) -> str:
    if not _HAS_COLOUR:
        return text
    return f"\033[2m{text}\033[0m"
 

_CHARS_COLOUR  = ' ·░░▒▒▓▓█'
_CHARS_PLAIN   = ' .,:;=+x#@'
 
def _density_char(count: int, max_count: int, palette: str) -> str:
    if count == 0 or max_count == 0:
        return palette[0]
    frac = count / max_count
    idx  = int(frac * (len(palette) - 1))
    return palette[min(idx, len(palette) - 1)]
 
def _colour_for(count: int, max_count: int) -> int:
    """Map density → blue ramp index."""
    if count == 0 or max_count == 0:
        return _BLUE_RAMP[0]
    frac = count / max_count
    idx  = int(frac * (len(_BLUE_RAMP) - 1))
    return _BLUE_RAMP[min(idx, len(_BLUE_RAMP) - 1)]
 
 
 
def render(
    positions,
    velocities=None,
    step: int = 0,
    width: int  = 78,
    height: int = 36,
    domain_x: tuple = (0.0, 1.0),
    domain_y: tuple = (0.0, 1.0),
    label: str = "",
) -> str:
    """
    Render SPH particles to an ASCII string.
 
    Parameters
    ----------
    positions  : (N, 2) array of float  – particle positions
    velocities : (N, 2) array of float  – optional, used for stats only
    step       : int                    – current simulation step
    width      : int                    – inner grid width  (chars)
    height     : int                    – inner grid height (rows)
    domain_x   : (xmin, xmax)          – physical domain in x
    domain_y   : (ymin, ymax)          – physical domain in y
    label      : str                    – implementation name shown in header
    """
    positions = np.asarray(positions)
    N = len(positions)
    palette = _CHARS_COLOUR if _HAS_COLOUR else _CHARS_PLAIN
 
    xmin, xmax = domain_x
    ymin, ymax = domain_y
    dx = xmax - xmin or 1.0
    dy = ymax - ymin or 1.0
 
    grid = np.zeros((height, width), dtype=np.int32)
    for pos in positions:
        col = int((pos[0] - xmin) / dx * width)
        row = int((1.0 - (pos[1] - ymin) / dy) * height)
        if 0 <= col < width and 0 <= row < height:
            grid[row, col] += 1
 
    max_count = int(grid.max()) or 1
 
    centroid = positions.mean(axis=0) if N else np.zeros(2)
    if velocities is not None and len(velocities):
        speeds   = np.linalg.norm(np.asarray(velocities), axis=1)
        max_spd  = speeds.max()
        mean_spd = speeds.mean()
    else:
        max_spd = mean_spd = 0.0
 
    total_w = width + 2
    impl_tag = f" {label} " if label else ""
    step_tag = f" step={step} "
    n_tag    = f" N={N} "
    title    = f"SPH Fluid{impl_tag}"
    top_fill  = width - len(title) - len(step_tag) - len(n_tag)
    top_left  = max(0, top_fill // 2)
    top_right = max(0, top_fill - top_left)
 
    top_border = (
        "╔"
        + "═" * top_left
        + _bold(title)
        + "═" * top_right
        + _dim(step_tag)
        + _dim(n_tag)
        + "╗"
    )
 
    stats = (
        f" cx={centroid[0]:.3f} cy={centroid[1]:.3f}"
        f"  vmax={max_spd:.3f}  vmean={mean_spd:.3f}"
        f"  peak={max_count}p/cell "
    )
    stats_padded = stats[:width].ljust(width)
    bot_border   = "╚" + stats_padded + "╝"
 
    lines = [top_border]
    for r in range(height):
        row_chars = []
        for c in range(width):
            cnt  = grid[r, c]
            ch   = _density_char(cnt, max_count, palette)
            if _HAS_COLOUR and cnt > 0:
                ch = _fg(_colour_for(cnt, max_count), ch)
            row_chars.append(ch)
        lines.append("║" + "".join(row_chars) + "║")
 
    lines.append(bot_border)
    return "\n".join(lines)
 
 
def clear_screen():
    """Clear terminal for live animation."""
    if os.name == "nt":
        os.system("cls")
    else:
        sys.stdout.write("\033[H")
        sys.stdout.flush()