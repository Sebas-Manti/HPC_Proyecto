## Fase 0 — Andamiaje
**Fecha: Mayo 15**

**Qué hice:**
- Realicé la estructura inicial del proyecto. 
- Escribí la documentación inicial (Readme.md, Listas de requisitos, documentos no visibles)
- Construí el esqueleto de las funciones para calcular SPH con python.
- Hice el binding de python a C++
- Hice mi primer reporte

**Qué aprendí:**

- Aprendí la estructura de convenciones de commits estándar de git (chore)
- Aprendí a hacer cuál es el esqueleto del binding
- Aprendí a nombrar las librerias correctamente

**Qué me costó / qué no entendí bien:**
- El binding es nuevo para mí
- Las convenciones de docstring


**Preguntas que quedaron abiertas:**
- La lista final de librerías 

## Fase 1 — Python naïve
**Fecha: Mayo 17**

**Qué hice:**
- Implementé las funciones físicas para calculos Naive en python
- Creé tests pytest para verificar las funciones
- Creé la primera simulación para verificar que la fisica estuviera funcionando

**Qué aprendí:**
- pytest que no había usado antes
- diferencia entre normalización 3D y 2D del kernel 


**Qué me costó / qué no entendí bien:**
- importe de modulos correctamente

**Preguntas que quedaron abiertas:**
- Visualización de la simulación dam break

## Fase 2 — Python hashed
**Fecha: Mayo 17**

**Qué hice:**
- Implementé las funciones físicas para calculos hashed en python
- Creé benchmark para comparar naive vs hashed

**Qué aprendí:**
- defaultdict(list) no había usado antes de collections


**Qué me costó / qué no entendí bien:**
- un poco entender la vectorización en este contexto 

**Preguntas que quedaron abiertas:**
- Visualización de la simulación dam break en hashed 