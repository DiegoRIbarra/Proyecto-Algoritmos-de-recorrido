"""Implementaciones de los algoritmos de caminos mínimos."""

import heapq
import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class Step:
    title: str
    detail: str
    nodes: tuple[int, ...] = ()
    edge: Optional[tuple[int, int]] = None
    kind: str = "visit"


class GraphAlgorithms:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.adj = {node: [] for node in nodes}
        for left, right, weight in edges:
            self.adj[left].append((right, weight))
            self.adj[right].append((left, weight))

    def dijkstra(self, start, goal):
        distances = {node: math.inf for node in self.nodes}
        previous, visited = {}, set()
        distances[start] = 0
        queue = [(0, start)]
        steps = [Step("Inicio", f"Distancia de {start} = 0. La cola de prioridad queda lista.", (start,), kind="start")]
        while queue:
            distance, current = heapq.heappop(queue)
            if current in visited:
                continue
            visited.add(current)
            steps.append(Step("Extraer mínimo", f"Se selecciona {current} con distancia {self.fmt(distance)}.", (current,), kind="active"))
            if current == goal:
                break
            for neighbor, weight in self.adj[current]:
                candidate = distance + weight
                steps.append(Step("Relajar arista", f"Comprobar {current} -> {neighbor}: {self.fmt(distance)} + {weight} = {self.fmt(candidate)}.", (current, neighbor), (current, neighbor), "relax"))
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    previous[neighbor] = current
                    heapq.heappush(queue, (candidate, neighbor))
                    steps.append(Step("Actualizar distancia", f"d({neighbor}) mejora a {self.fmt(candidate)} vía {current}.", (current, neighbor), (current, neighbor), "update"))
        return self.finish(start, goal, distances, previous, steps)

    def bellman_ford(self, start, goal):
        distances = {node: math.inf for node in self.nodes}
        previous = {}
        distances[start] = 0
        steps = [Step("Inicio", f"Distancia de {start} = 0; el resto comienza en infinito.", (start,), kind="start")]
        directed_edges = self.edges + [(b, a, weight) for a, b, weight in self.edges]
        for iteration in range(len(self.nodes) - 1):
            changed = False
            steps.append(Step(f"Iteración {iteration + 1}", "Se recorren todas las aristas para buscar mejoras.", kind="round"))
            for left, right, weight in directed_edges:
                if distances[left] == math.inf:
                    continue
                candidate = distances[left] + weight
                steps.append(Step("Evaluar arista", f"{left} -> {right}: {self.fmt(distances[left])} + {weight} = {self.fmt(candidate)}.", (left, right), (left, right), "relax"))
                if candidate < distances[right]:
                    distances[right] = candidate
                    previous[right] = left
                    changed = True
                    steps.append(Step("Relajación exitosa", f"d({right}) = {self.fmt(candidate)} gracias a {left}.", (left, right), (left, right), "update"))
            if not changed:
                steps.append(Step("Convergencia", "No hubo cambios: el algoritmo termina antes de completar las rondas.", kind="round"))
                break
        return self.finish(start, goal, distances, previous, steps)

    def floyd_warshall(self, start, goal):
        distances = {left: {right: math.inf for right in self.nodes} for left in self.nodes}
        next_node = {left: {} for left in self.nodes}
        for node in self.nodes:
            distances[node][node] = 0
            next_node[node][node] = node
        for left, right, weight in self.edges:
            distances[left][right] = distances[right][left] = weight
            next_node[left][right] = right
            next_node[right][left] = left
        steps = [Step("Matriz inicial", "Se cargan pesos directos y ceros en la diagonal.", (start,), kind="start")]
        for via in self.nodes:
            steps.append(Step("Nuevo intermediario", f"Se prueba usar {via} como nodo intermedio.", (via,), kind="round"))
            for left in self.nodes:
                for right in self.nodes:
                    candidate = distances[left][via] + distances[via][right]
                    if candidate < distances[left][right]:
                        distances[left][right] = candidate
                        next_node[left][right] = next_node[left][via]
                        steps.append(Step("Mejorar matriz", f"M[{left}][{right}] mejora a {self.fmt(candidate)} pasando por {via}.", (left, via, right), (left, via), "update"))
        previous = {}
        if next_node[start].get(goal) is not None:
            current = start
            while current != goal:
                following = next_node[current].get(goal)
                if following is None:
                    break
                previous[following] = current
                current = following
        return self.finish(start, goal, distances[start], previous, steps)

    def a_star(self, start, goal, heuristic_name="Euclidiana"):
        goal_x, goal_y = self.nodes[goal]
        if heuristic_name == "Manhattan":
            heuristic = lambda node: (abs(self.nodes[node][0] - goal_x) + abs(self.nodes[node][1] - goal_y)) / 16
        else:
            heuristic = lambda node: math.hypot(self.nodes[node][0] - goal_x, self.nodes[node][1] - goal_y) / 16
        distances = {node: math.inf for node in self.nodes}
        previous, closed = {}, set()
        distances[start] = 0
        queue, counter = [(heuristic(start), 0, start)], 0
        steps = [Step("Inicio", f"f({start}) = g(0) + h({self.fmt(heuristic(start))}).", (start,), kind="start")]
        while queue:
            score, _, current = heapq.heappop(queue)
            if current in closed:
                continue
            closed.add(current)
            steps.append(Step("Elegir mejor estimación", f"Se explora {current}: g={self.fmt(distances[current])}, f={self.fmt(score)}.", (current,), kind="active"))
            if current == goal:
                break
            for neighbor, weight in self.adj[current]:
                if neighbor in closed:
                    continue
                candidate = distances[current] + weight
                steps.append(Step("Evaluar vecino", f"{current} -> {neighbor}; g tentativo = {self.fmt(candidate)}.", (current, neighbor), (current, neighbor), "relax"))
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    previous[neighbor] = current
                    counter += 1
                    heapq.heappush(queue, (candidate + heuristic(neighbor), counter, neighbor))
                    steps.append(Step("Actualizar camino", f"g({neighbor}) = {self.fmt(candidate)}, h = {self.fmt(heuristic(neighbor))}.", (current, neighbor), (current, neighbor), "update"))
        return self.finish(start, goal, distances, previous, steps)

    def finish(self, start, goal, distances, previous, steps):
        if distances.get(goal, math.inf) == math.inf:
            steps.append(Step("Sin solución", f"No se encontró un camino desde {start} hasta {goal}.", (start, goal), kind="error"))
            return steps, [], math.inf
        path, current = [], goal
        while True:
            path.append(current)
            if current == start:
                break
            if current not in previous:
                return steps, [], math.inf
            current = previous[current]
        path.reverse()
        steps.append(Step("Camino final", f"Ruta óptima: {'  ->  '.join(map(str, path))} | costo total {self.fmt(distances[goal])}.", tuple(path), kind="path"))
        return steps, path, distances[goal]

    @staticmethod
    def fmt(value):
        return "∞" if value == math.inf else f"{value:g}"
