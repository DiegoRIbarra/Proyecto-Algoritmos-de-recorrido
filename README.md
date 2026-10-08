# Pathfinder

Aplicacion de escritorio en Python para visualizar el camino mas corto entre dos nodos de un grafo ponderado.

## Ejecutar

Requiere Python 3.10 o superior. Tkinter forma parte de la instalacion estandar de Python en Windows.

```powershell
python main.py
```

## Uso

1. Elige los nodos de inicio y destino en el panel derecho.
2. Selecciona Dijkstra, Bellman-Ford, Floyd-Warshall o A*.
3. Pulsa `EJECUTAR` para iniciar la animacion.
4. Pulsa `PAUSAR` para detenerla y selecciona cualquier paso de la traza para inspeccionarlo.
5. La ruta final se muestra en verde y su costo aparece en el resumen.

El grafo inicial esta basado en el bosquejo proporcionado y es no dirigido. Los pesos se muestran sobre cada arista.

El selector `Grafo` permite alternar entre `Grafo 1`, que conserva los pesos positivos originales, y `Grafo 2`, que contiene la versión actualizada de la fotografía con pesos negativos. Para `Grafo 2`, usa principalmente Bellman-Ford: Dijkstra y A* no garantizan resultados correctos con pesos negativos. Al ser un grafo no dirigido, una arista negativa puede producir un ciclo negativo de ida y vuelta, por lo que en ese caso no existe un camino mínimo finito.

## Estructura

- `main.py`: punto de entrada minimo.
- `ui.py`: ventana, controles, lienzo y animacion.
- `algorithms.py`: pasos y algoritmos de caminos minimos.
- `graph_data.py`: nodos, coordenadas y aristas del grafo.