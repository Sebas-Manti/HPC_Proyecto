<<<<<<< HEAD
```markdown
# HPC SPH — Parallel Fluid Simulation with ARM NEON on Apple M3

> Proyecto de grado — Seminario de Computación Científica II  
> Universidad Konrad Lorenz · 8vo semestre · 2026-1

Implementación de un simulador de fluidos basado en **Smoothed Particle Hydrodynamics (SPH)** con optimizaciones de alto rendimiento: paralelismo de datos mediante **ARM NEON SIMD intrinsics** y paralelismo de tareas con **OpenMP**, expuesto a Python a través de **pybind11**.

---

## Contenido

- [Descripción](#descripción)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Requisitos](#requisitos)
- [Compilación](#compilación)
- [Uso](#uso)
- [Benchmarks](#benchmarks)
- [Tests](#tests)
- [Resultados y visualizaciones](#resultados-y-visualizaciones)

---

## Descripción

SPH es un método numérico sin malla para simular mecánica de fluidos. Cada partícula lleva masa, posición, velocidad y presión; las cantidades físicas se interpolan mediante un kernel de suavizado sobre partículas vecinas.

Este proyecto explora cómo las capacidades SIMD del chip **Apple M3** (arquitectura ARM) permiten vectorizar los cálculos de densidad y fuerzas sobre grupos de partículas, reduciendo el tiempo de pared respecto a una implementación escalar equivalente.

### Características

- Núcleo SPH en C++17 con intrínsecos ARM NEON (`arm_neon.h`)
- Bindings Python via **pybind11** para scripting, benchmarking y visualización
- Soporte opcional **OpenMP** para paralelismo multi-hilo
- Suite de benchmarks con `pytest-benchmark`
- Condiciones iniciales configurables en `data/initial_conditions/`

---

## Estructura del repositorio

```
HPC_Proyecto/
├── src/
│   ├── cpp/            # Núcleo C++: simulador SPH + bindings pybind11
│   └── python/         # Helpers Python, scripts de análisis
├── data/
│   └── initial_conditions/   # Archivos de condiciones iniciales (.npy / .csv)
├── bench/              # Scripts de benchmark
├── tests/              # Tests unitarios (pytest)
├── viz/                # Scripts de visualización ASCII en terminal con curses
├── report/             # Informe del proyecto (LaTeX / PDF)
├── CMakeLists.txt      # Build del módulo C++
└── pyproject.toml      # Metadata del paquete Python
```

---

## Requisitos

| Herramienta | Versión mínima |
|-------------|---------------|
| macOS (Apple Silicon) | 13 Ventura |
| Clang / Apple Clang | 15+ |
| CMake | 3.20+ |
| Python | 3.10+ |
| pybind11 | 2.11+ |
| numpy | 1.24+ |

Instalar dependencias Python:

```bash
pip install -e ".[dev]"
```

---

## Compilación

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --parallel
```

El módulo compilado (`hpc_sph.*.so`) queda en `build/` y puede importarse directamente desde Python.

Para habilitar OpenMP (si está disponible en el toolchain):

```bash
cmake .. -DCMAKE_BUILD_TYPE=Release -DUSE_OPENMP=ON
```

---

## Uso

```python
import sys
sys.path.insert(0, "build/")
import hpc_sph

# Inicializar simulación
sim = hpc_sph.SPHSimulator(n_particles=10_000, dt=0.001)
sim.load_initial_conditions("data/initial_conditions/dam_break.npy")

# Avanzar N pasos
for step in range(500):
    sim.step()

# Extraer estado
positions = sim.get_positions()   # numpy array (N, 2)
velocities = sim.get_velocities() # numpy array (N, 2)
```

---

## Benchmarks

Los benchmarks comparan la implementación **scalar**, **NEON SIMD** y, opcionalmente, **NEON + OpenMP**:

```bash
pytest bench/ -v --benchmark-sort=mean
```

Los resultados se guardan en `bench/` como JSON para graficar con los scripts de `viz/`.

---

## Tests

```bash
pytest tests/ -v
```

Los tests verifican conservación de masa, condición de suma de densidades y estabilidad numérica básica.

---

## Resultados y visualizaciones

Los scripts de `viz/` generan:

- ASCII en terminal con curses
- Gráficas de speedup SIMD vs. escalar
- Perfiles de densidad y presión en el tiempo

El informe completo del proyecto se encuentra en `report/`.

---

## Autor

**John Sebastian Mantilla** — johns.mantillam@konradlorenz.edu.co  
Universidad Konrad Lorenz · Programa de Matemáticas
```
=======
# HPC_Proyecto
>>>>>>> efe828105e9c73b841c3cca7c2b31f0715b2f000
