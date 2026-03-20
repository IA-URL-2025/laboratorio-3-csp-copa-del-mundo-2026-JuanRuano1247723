[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/yrAdZ_9h)
# Laboratorio: Sorteo Copa del Mundo 2026 como CSP

Este proyecto es un laboratorio didáctico en Python que modela el sorteo de grupos de la Copa del Mundo 2026 como un Problema de Satisfacción de Restricciones (CSP).

## Introducción a CSP

Un Problema de Satisfacción de Restricciones (CSP por sus siglas en inglés, Constraint Satisfaction Problem) se define por un conjunto de variables, un dominio de valores posibles para cada variable y un conjunto de restricciones que limitan las combinaciones de valores que estas variables pueden tomar simultáneamente.

En este laboratorio, las variables son los equipos a asignar, los dominios son los grupos disponibles (A-L) y las restricciones se basan en las reglas del sorteo del Mundial de la FIFA:
1. Máximo 1 equipo por confederación en cada grupo.
2. Excepción: UEFA puede tener hasta 2 equipos por grupo.
3. Cada grupo debe tener exactamente 4 equipos, uno de cada bombo.

## Objetivo del Laboratorio

Tu tarea es implementar las partes clave del algoritmo CSP para resolver este problema.

Deberás completar los siguientes métodos en el archivo `src/world_cup_csp.py`, donde encontrarás los comentarios `TODO`:

1. `is_valid_assignment`: Verifica si asignar un equipo a un grupo viola las restricciones de confederación.
2. `forward_check`: Implementa la propagación de restricciones eliminando valores inconsistentes en dominios futuros.
3. `select_unassigned_variable`: Implementa la heurística MRV (Minimum Remaining Values) para seleccionar el próximo equipo a asignar.
4. `backtrack`: Implementa la búsqueda de backtracking con forward checking y MRV para resolver el CSP.

## Cómo ejecutar el proyecto

Para ejecutar el algoritmo y ver las trazas de ejecución en la consola (útil para el análisis y responder preguntas teóricas):

```bash
python main.py
```

En `main.py` puedes ajustar el parámetro `debug=True` al instanciar `WorldCupCSP` para habilitar el modo de depuración y ver detalladamente cómo el algoritmo intenta asignar equipos y realiza *backtracking*.

## Cómo ejecutar las pruebas (Tests)

Este repositorio incluye un conjunto de pruebas automáticas (tests) escritas con `pytest`. Tu calificación dependerá de cuántos de estos tests pasen exitosamente.

Primero, instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

Luego, ejecuta los tests con el siguiente comando:

```bash
pytest -v
```

Cada vez que hagas un *push* a tu repositorio en GitHub, las pruebas se ejecutarán automáticamente en GitHub Actions para autocalificar tu entrega.
