# Parallel SPH Fluid Simulation — ARM NEON on Apple M3

Simulación 2D de fluidos por el método SPH (*Smoothed Particle Hydrodynamics*) con cuatro implementaciones progresivas: desde Python puro hasta C++ con SIMD ARM NEON, alcanzando un speedup de **4192×**.

<!-- PLACEHOLDER: gif del dam break en tiempo real (viz-live neon) -->
<!-- ![Dam Break](docs/dambreak.gif) -->

---

## Resultados principales

| Implementación | Tiempo (100 pasos, 450p) | ms / paso | Speedup vs. Naïve |
|:---|---:|---:|---:|
| Python Naïve   | 62.878 s | 628.78 | 1× |
| Python Hashed  | 13.994 s | 139.94 | **4.5×** |
| C++ Escalar    |  0.092 s |   0.92 | **683×** |
| C++ NEON       |  0.015 s |   0.15 | **4192×** |

<!-- PLACEHOLDER: gráfica de speedup (barras o líneas log) -->
<!-- ![Speedup Chart](docs/speedup.png) -->

---

## Estructura del proyecto

```
HPC_Proyecto/
├── src/
│   ├── python/
│   │   ├── kernels.py          # Kernels SPH: Poly6, Spiky, Laplaciano
│   │   ├── sph_naive.py        # Solver O(N²) — referencia
│   │   ├── sph_hashed.py       # Solver O(N) — hashing espacial
│   │   └── run_simulation.py   # Runner con visualización ASCII
│   └── cpp/
│       ├── kernels.h / kernels.cpp   # Kernels compilados
│       ├── sph_scalar.cpp            # Solver C++ escalar
│       ├── sph_neon.cpp              # Solver C++ ARM NEON
│       ├── sph_neon_omp.cpp          # Solver NEON + OpenMP
│       └── bindings.cpp              # Bindings pybind11
├── bench/
│   └── run_cases.py            # Benchmark comparativo
├── viz/
│   └── ascii_renderer.py       # Renderer ASCII en tiempo real (curses)
├── tests/
│   └── test_kernels.py         # Tests de normalización del kernel
├── report/
│   └── final_report.tex        # Reporte final en LaTeX
└── CMakeLists.txt
```

---

## Instalación y compilación

### Requisitos

- macOS (Apple Silicon M1/M2/M3)
- Python ≥ 3.10
- CMake ≥ 3.20
- pybind11, numpy, rich, scipy

```bash
# Dependencias Python
pip install numpy pybind11 rich scipy

# Dependencias sistema (Homebrew)
brew install cmake libomp
```

### Compilar el módulo C++

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(sysctl -n hw.ncpu)
```

El módulo `hpc_sph.so` queda en `build/`.

---

## Uso

### Visualización en tiempo real (ASCII)

```bash
# Dam break con Python hashed
python -m src.python.run_simulation viz-live hashed

# Dam break con C++ NEON (más rápido)
python -m src.python.run_simulation viz-live neon

# Presiona 'q' para salir
```

<!-- PLACEHOLDER: screenshot del renderer ASCII en terminal -->
<!-- ![ASCII Renderer](docs/ascii_renderer.png) -->

### Benchmark comparativo

```bash
# Todas las implementaciones — 15×30 partículas, 100 pasos
PYTHONPATH=. python bench/run_cases.py --funcs hashed hpc neon --nx 15 --ny 30 --steps 100

# Escalado con distintos tamaños de grid
PYTHONPATH=. python bench/run_cases.py --funcs hashed hpc neon --compare-nx 5 10 15 20

# Solo C++ (benchmarks rápidos)
PYTHONPATH=. python bench/run_cases.py --funcs hpc neon --nx 20 --ny 40 --steps 500
```

### Tests

```bash
PYTHONPATH=. pytest tests/ -v
```

---

## Implementaciones

### Fase 1 — Python Naïve · O(N²)

Doble bucle sobre todos los pares de partículas. Sirve como baseline de referencia.  
**62.878 s** para 450 partículas, 100 pasos.

### Fase 2 — Python Hashed · O(N)

Tabla hash espacial uniforme con celdas de tamaño `2h`. Cada partícula consulta solo las 9 celdas vecinas (3×3), reduciendo la búsqueda a O(1) por partícula.  
**13.994 s** — **4.5× más rápido** que Naïve.

<!-- PLACEHOLDER: diagrama de la tabla hash espacial -->
<!-- ![Spatial Hash](docs/spatial_hash.png) -->

### Fase 3 — C++ Escalar · pybind11

Kernels reescritos en C++17 con layout **Structure of Arrays (SoA)** para máxima localidad de caché. Expuesto a Python vía pybind11 con paso de arrays NumPy como vistas zero-copy (`py::array_t<float>`).  
**0.092 s** — **683× más rápido** que Naïve, **152× más rápido** que Hashed.

### Fase 4 — C++ ARM NEON · SIMD 128-bit

El bucle interno de densidad procesa **4 partículas simultáneamente** con registros NEON de 128 bits (`float32x4_t`).

```cpp
float32x4_t vix = vdupq_n_f32(pos_x[i]);   // broadcast xi a 4 lanes
float32x4_t acc = vdupq_n_f32(0.0f);
for (int j = 0; j + 4 <= N; j += 4) {
    float32x4_t dx  = vsubq_f32(vix, vld1q_f32(&pos_x[j]));
    float32x4_t r2  = vmlaq_f32(vmulq_f32(dx,dx), dy, dy);
    // ... kernel Poly6 vectorizado + máscara ...
    acc = vaddq_f32(acc, w_val);
}
rho[i] = vaddvq_f32(acc) * mass;  // reducción horizontal
```

**0.015 s** — **4192× más rápido** que Naïve, **6× más rápido** que C++ Escalar.

<!-- PLACEHOLDER: diagrama del pipeline NEON (4 floats por ciclo) -->
<!-- ![NEON Pipeline](docs/neon_pipeline.png) -->

---

## Escalado con número de partículas

| N partículas | Python Hashed | C++ Escalar | C++ NEON | Speedup (Hashed→NEON) |
|---:|---:|---:|---:|---:|
| 150 | 3.001 s | 0.011 s | 0.002 s | **1605×** |
| 300 | 6.567 s | 0.042 s | 0.007 s | **1002×** |
| 450 | 14.305 s | 0.098 s | 0.015 s | **975×** |
| 600 | 24.863 s | 0.174 s | 0.025 s | **1009×** |

<!-- PLACEHOLDER: gráfica de escalado (tiempo vs N, escala log) -->
<!-- ![Scaling](docs/scaling.png) -->

---

## Fundamentos físicos

Las ecuaciones de Navier-Stokes discretizadas via SPH (Müller et al. 2003):

| Cantidad | Ecuación |
|:---|:---|
| Densidad | `ρᵢ = Σⱼ m · W(‖rᵢ−rⱼ‖, h)` |
| Presión | `pᵢ = k · (ρᵢ − ρ₀)` |
| Fuerza de presión | `Fᵢ_press = −m · (pᵢ+pⱼ)/(2ρⱼ) · ∇W_spiky` |
| Fuerza viscosa | `Fᵢ_visc = μ · m · (vⱼ−vᵢ)/ρⱼ · ∇²W` |
| Gravedad | `Fᵢ_grav = ρᵢ · g` |

Kernels utilizados:

| Kernel | Uso | Soporte |
|:---|:---|:---|
| **Poly6** | Densidad | r ≤ h |
| **Spiky** (Desbrun 1996) | Gradiente de presión | 0 < r ≤ h |
| **Laplaciano** | Viscosidad | r ≤ h |

---

## Parámetros de simulación

| Parámetro | Valor | Descripción |
|:---|:---|:---|
| `h` | 0.05 | Longitud de suavizado |
| `dt` | 0.001 s | Paso temporal |
| `k` | 10.0 | Coeficiente de rigidez |
| `μ` | 0.1 | Viscosidad dinámica |
| `m` | 1.0 | Masa de partícula |
| `g` | (0, −9.8) | Gravedad |
| `ρ₀` | auto-calibrado | `mean(compute_density)` en t=0 |

---

## Plataforma

| Componente | Detalle |
|:---|:---|
| Procesador | Apple M3 — 4P + 4E cores |
| SIMD | ARM NEON 128-bit — 4× float32/ciclo |
| Memoria | Unificada CPU/GPU |
| Compilador | Clang/LLVM, C++17 |
| Python | 3.12 |
| pybind11 | 2.13 |

---

## Autor

**John Sebastian Mantilla Manzano**  
johns.mantillam@konradlorenz.edu.co  
Scientific Computing 2 — 2026-I · Universidad Konrad Lorenz
