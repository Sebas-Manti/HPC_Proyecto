import numpy as np
def render(positions, width=80, height=40):
    """
    Renderiza la función en un grid de 80x40

    Args:
        positions (np.ndarray (N,2)): posiciones de la partícula
        width (int): ancho del grid
        height (int): alto del grid

    Returns (String):
    Retorna la lista de caracteres para simular
    """

    grid = np.zeros((height,width), dtype=int)

    for pos in positions:
        col = int(pos[0] * width)
        row = int((1 - pos[1]) * height)
        if 0 <= col < width and 0 <= row < height:
            grid[row, col] += 1
    
    chars = ' .:−=+*#%@'
    lines = []

    for fila in grid:
        row_chars = []
        for count in fila:
            idx = min(count, len(chars)-1)
            row_chars.append(chars[idx])
        lines.append(''.join(row_chars))

    return '\n'.join(lines)