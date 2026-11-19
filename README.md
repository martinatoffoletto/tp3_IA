# TP3 – Algoritmos Genéticos: ¿Quién usa el editor Vim?

**UADE – 3.4.096 Inteligencia Artificial**
Docente: Parkinson, Christian Aníbal

## Integrantes

- Buset, Agustín
- Castro, Martina Morena
- Gantus, Elías
- Toffoletto, Martina Ornella

## El problema

Hay 5 casas. En cada una vive una persona con un color de casa, una profesión, un lenguaje de programación, una base de datos NoSQL y un editor distintos. Con 15 pistas (ver `consigna/`) hay que responder **¿quién usa el editor Vim?**, resolviéndolo con un algoritmo genético.

## Requisitos

- Python 3.8 o superior.
- No hace falta instalar nada: solo se usa la biblioteca estándar.

## Cómo correrlo

Desde la carpeta del proyecto:

```bash
# Resolver el acertijo (población 2000, generación aleatoria, log cada 100 generaciones)
python ga.py

# Corrida reproducible, con población inicial heurística y sin log
python ga.py --seed 1 --init heuristic --quiet
```

> En Windows, si la consola muestra mal los acentos, ejecutá antes `set PYTHONIOENCODING=utf-8` (cmd) o `$env:PYTHONIOENCODING="utf-8"` (PowerShell).

### Opciones de `ga.py`

| Opción | Por defecto | Descripción |
|---|---|---|
| `--poblacion` | 2000 | Tamaño de la población |
| `--generaciones` | 1000 | Máximo de generaciones (condición de corte 2) |
| `--estancamiento` | 150 | Generaciones sin mejora antes de cortar (condición de corte 3) |
| `--seed` | aleatoria | Semilla, para que la corrida sea reproducible |
| `--init` | `random` | Generación de individuos: `random` o `heuristic` |
| `--quiet` | – | No muestra el log por generación |

### Ejemplo de salida

```
Casa | Color  | Profesion     | Lenguaje   | Base de datos | Editor
-----+--------+---------------+------------+---------------+-------------
1    | blue   | Developer     | Java       | Redis         | Vim
2    | yellow | Analyst       | JavaScript | Cassandra     | Atom
3    | red    | Mathematician | C#         | HBase         | Notepad++
4    | white  | Hacker        | Python     | Neo4j         | Sublime Text
5    | green  | Engineer      | C++        | MongoDB       | Brackets

Respuesta: el editor Vim lo usa el Developer.
```

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `ga.py` | El algoritmo genético: clases `Phenotype` (individuo) y `Riddle` (proceso evolutivo) |
| `Informe-TP3-AlgoritmosGeneticos.docx` | Informe con la justificación de cada tarea, los resultados y las conclusiones |
| `dev_ga_base.py` | Estructura base provista por la cátedra (`ga.py` parte de ella) |
| `consigna/` | Enunciado del TP (PDF y DOCX) |

## Resumen de la solución

| Tarea | Decisión |
|---|---|
| 1. Individuo | 25 genes de 3 bits (5 casas × 5 atributos), con el formato de `dev_ga_base.py`. Cada atributo es una permutación: las 5 casas tienen valores distintos y válidos |
| 2. Generación | Aleatoria (`random.sample` por atributo) o heurística (ya ubica las pistas de posición fija: 9, 10 y 15) |
| 3a. Selección | Torneo de 3 individuos, más elitismo del 5% |
| 3b. Cruce | Uniforme por atributo: cada hijo hereda la columna completa de un atributo de uno de los padres (probabilidad 0,8) |
| 3c. Mutación | Intercambia dos casas dentro de un atributo, elegido preferentemente entre las pistas incumplidas (probabilidad 0,8) |
| 4. Corte | (1) se cumplen las 15 pistas, (2) 1000 generaciones, (3) 150 generaciones sin mejora |
| 5. Alternativas | Inmigrantes aleatorios, siembra heurística, elitismo, mutantes de la élite, reinicio parcial, reparación |

**Fitness:** +1 por pista cumplida, −1 por pista incumplida y −1 por gen inválido. El máximo es 14 (pistas 2 a 15).

**Interpretación de la pista 6:** "a la derecha" se toma como *inmediatamente* a la derecha.

## Respuesta

Las pistas no determinan una única solución: hay **14 asignaciones** que cumplen las 15 pistas. Según cuál encuentre el algoritmo, Vim lo usa:

| Usuario de Vim | Soluciones exactas |
|---|---|
| Desarrollador | 6 |
| Matemático | 5 |
| Hacker | 2 |
| Ingeniero | 1 |

El Analista nunca puede usar Vim, porque la pista 5 le asigna Atom. El análisis completo está en el informe.
