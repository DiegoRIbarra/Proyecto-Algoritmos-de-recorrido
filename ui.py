"""Interfaz Tkinter y animación de la búsqueda."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from algorithms import GraphAlgorithms, Step
from graph_data import build_graph

BG, PANEL, PANEL_2 = "#0b1220", "#111c2e", "#17253a"
TEXT, MUTED, CYAN = "#eef4ff", "#8fa4c2", "#51d5d5"
ORANGE, GREEN, RED = "#ffb454", "#6ee7a8", "#ff7187"
GRID = "#1a2b43"


class ShortestPathApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pathfinder · Algoritmos de recorrido")
        self.geometry("1420x860")
        self.minsize(1100, 700)
        self.configure(bg=BG)
        self.graph_name = "Grafo 1"
        self.nodes, self.edges = build_graph(self.graph_name)
        self.graph = GraphAlgorithms(self.nodes, self.edges)
        self.steps: list[Step] = []
        self.path: list[int] = []
        self.current_step = -1
        self.running = False
        self.animation_job = None
        self.updating_selection = False
        self.node_radius = 22
        self.setup_style()
        self.build_ui()
        self.draw_graph()

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=PANEL_2, background=PANEL_2, foreground=TEXT, arrowcolor=CYAN, borderwidth=0)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL_2)], foreground=[("readonly", TEXT)])
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=38, borderwidth=0)
        style.map("Treeview", background=[("selected", "#244569")], foreground=[("selected", TEXT)])
        style.configure("TScrollbar", troughcolor=PANEL, background="#29445f", arrowcolor=MUTED)

    def build_ui(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=28, pady=(24, 12))
        tk.Label(header, text="PATHFINDER", font=("Segoe UI", 11, "bold"), fg=CYAN, bg=BG).pack(anchor="w")
        tk.Label(header, text="Encuentra la ruta más corta", font=("Segoe UI", 26, "bold"), fg=TEXT, bg=BG).pack(anchor="w", pady=(4, 0))
        tk.Label(header, text="Visualiza cómo piensan cuatro algoritmos clásicos, paso a paso.", font=("Segoe UI", 11), fg=MUTED, bg=BG).pack(anchor="w", pady=(5, 0))
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=(4, 24))
        graph_panel = tk.Frame(body, bg=PANEL, highlightthickness=1, highlightbackground="#203652")
        graph_panel.pack(side="left", fill="both", expand=True, padx=(0, 16))
        self.canvas = tk.Canvas(graph_panel, bg="#0e192a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=1, pady=1)
        self.canvas.bind("<Configure>", lambda _: self.draw_graph())
        side = tk.Frame(body, bg=PANEL, width=390)
        side.pack(side="right", fill="y")
        side.pack_propagate(False)
        self.build_controls(side)
        self.build_steps(side)

    def build_controls(self, parent):
        controls = tk.Frame(parent, bg=PANEL)
        controls.pack(fill="x", padx=22, pady=22)
        tk.Label(controls, text="CONFIGURAR RECORRIDO", font=("Segoe UI", 10, "bold"), fg=CYAN, bg=PANEL).pack(anchor="w")
        tk.Label(controls, text="Define los puntos y observa el algoritmo en acción.", font=("Segoe UI", 10), fg=MUTED, bg=PANEL).pack(anchor="w", pady=(4, 16))
        tk.Label(controls, text="GRAFO", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=PANEL).pack(anchor="w", pady=(0, 6))
        self.graph_var = tk.StringVar(value=self.graph_name)
        graph_selector = ttk.Combobox(controls, textvariable=self.graph_var, values=["Grafo 1", "Grafo 2"], state="readonly")
        graph_selector.pack(fill="x", pady=(0, 16))
        graph_selector.bind("<<ComboboxSelected>>", self.change_graph)
        fields = tk.Frame(controls, bg=PANEL)
        fields.pack(fill="x")
        self.start_var = tk.StringVar(value="29")
        self.goal_var = tk.StringVar(value="70")
        self.algorithm_var = tk.StringVar(value="Dijkstra")
        for column, label, variable in ((0, "INICIO", self.start_var), (1, "DESTINO", self.goal_var)):
            field = tk.Frame(fields, bg=PANEL)
            field.grid(row=0, column=column, sticky="ew", padx=(0, 8) if column == 0 else (8, 0))
            tk.Label(field, text=label, font=("Segoe UI", 8, "bold"), fg=MUTED, bg=PANEL).pack(anchor="w", pady=(0, 6))
            ttk.Combobox(field, textvariable=variable, values=[str(node) for node in self.nodes], state="readonly").pack(fill="x")
        fields.columnconfigure(0, weight=1)
        fields.columnconfigure(1, weight=1)
        tk.Label(controls, text="ALGORITMO", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=PANEL).pack(anchor="w", pady=(18, 6))
        ttk.Combobox(controls, textvariable=self.algorithm_var, values=["Dijkstra", "Bellman-Ford", "Floyd-Warshall", "A*"], state="readonly").pack(fill="x")
        buttons = tk.Frame(controls, bg=PANEL)
        buttons.pack(fill="x", pady=(18, 0))
        self.play_button = tk.Button(buttons, text="▶  EJECUTAR", command=self.run_search, font=("Segoe UI", 10, "bold"), fg=BG, bg=CYAN, activebackground="#87eeee", relief="flat", cursor="hand2", padx=14, pady=10)
        self.play_button.pack(side="left", fill="x", expand=True)
        tk.Button(buttons, text="↺", command=self.reset, font=("Segoe UI", 15), fg=TEXT, bg=PANEL_2, activebackground="#244569", relief="flat", cursor="hand2", width=4, pady=5).pack(side="left", padx=(8, 0))
        self.summary = tk.Label(controls, text="Listo para explorar", font=("Segoe UI", 10), fg=MUTED, bg=PANEL, anchor="w")
        self.summary.pack(fill="x", pady=(16, 0))

    def change_graph(self, _event=None):
        self.graph_name = self.graph_var.get()
        self.nodes, self.edges = build_graph(self.graph_name)
        self.graph = GraphAlgorithms(self.nodes, self.edges)
        self.start_var.set(str(next(iter(self.nodes))))
        self.goal_var.set(str(next(reversed(self.nodes))))
        self.reset()
        self.summary.configure(text=f"{self.graph_name} cargado", fg=CYAN)

    def build_steps(self, parent):
        tk.Frame(parent, bg="#203652", height=1).pack(fill="x")
        heading = tk.Frame(parent, bg=PANEL)
        heading.pack(fill="x", padx=22, pady=(18, 10))
        tk.Label(heading, text="TRAZA DE EJECUCIÓN", font=("Segoe UI", 10, "bold"), fg=CYAN, bg=PANEL).pack(side="left")
        self.step_count = tk.Label(heading, text="0 pasos", font=("Segoe UI", 9), fg=MUTED, bg=PANEL)
        self.step_count.pack(side="right")
        tree_frame = tk.Frame(parent, bg=PANEL)
        tree_frame.pack(fill="both", expand=True, padx=16, pady=(0, 18))
        self.step_list = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
        self.step_list.column("#0", width=330, stretch=True)
        self.step_list.heading("#0", text="Selecciona un paso para inspeccionarlo", anchor="w")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.step_list.yview)
        self.step_list.configure(yscrollcommand=scrollbar.set)
        self.step_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.step_list.bind("<<TreeviewSelect>>", self.select_step)

    def scaled(self, node):
        width = max(self.canvas.winfo_width(), 600)
        height = max(self.canvas.winfo_height(), 500)
        x, y = self.nodes[node]
        return 48 + x * (width - 96), 42 + y * (height - 84)

    def draw_graph(self, active_nodes=(), active_edge=None, final_path=(), current_node=None):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        for x in range(0, width, 44):
            self.canvas.create_line(x, 0, x, height, fill=GRID)
        for y in range(0, height, 44):
            self.canvas.create_line(0, y, width, y, fill=GRID)
        final_pairs = {frozenset((final_path[i], final_path[i + 1])) for i in range(len(final_path) - 1)}
        active_pair = frozenset(active_edge) if active_edge else None
        for left, right, weight in self.edges:
            start, end = self.scaled(left), self.scaled(right)
            pair = frozenset((left, right))
            color, line_width = "#2f4b68", 1
            if pair in final_pairs:
                color, line_width = GREEN, 5
            elif pair == active_pair:
                color, line_width = ORANGE, 4
            self.canvas.create_line(*start, *end, fill=color, width=line_width)
            mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
            self.canvas.create_rectangle(mx - 12, my - 9, mx + 12, my + 9, fill="#122238", outline="#2e5270")
            self.canvas.create_text(mx, my, text=str(weight), fill=ORANGE if pair == active_pair else MUTED, font=("Segoe UI", 8, "bold"))
        for node in self.nodes:
            x, y = self.scaled(node)
            fill, outline, outline_width = "#1c3554", "#3b6b98", 2
            if node in final_path:
                fill, outline, outline_width = "#176b59", GREEN, 3
            if node in active_nodes:
                fill, outline, outline_width = "#8a5520", ORANGE, 3
            if node == current_node:
                fill, outline, outline_width = "#1e7290", CYAN, 4
            if node == int(self.start_var.get()) if self.start_var.get().isdigit() else False:
                outline = CYAN
            if node == int(self.goal_var.get()) if self.goal_var.get().isdigit() else False:
                outline = RED
            self.canvas.create_oval(x - self.node_radius, y - self.node_radius, x + self.node_radius, y + self.node_radius, fill=fill, outline=outline, width=outline_width)
            self.canvas.create_text(x, y, text=str(node), fill=TEXT, font=("Segoe UI", 10, "bold"))
        self.canvas.create_text(24, height - 20, anchor="w", text="● inicio    ● destino    ● exploración    ● ruta óptima", fill=MUTED, font=("Segoe UI", 9))

    def run_search(self):
        if self.running:
            self.running = False
            if self.animation_job:
                self.after_cancel(self.animation_job)
            self.play_button.configure(text="▶  CONTINUAR")
            return
        try:
            start, goal = int(self.start_var.get()), int(self.goal_var.get())
        except ValueError:
            messagebox.showerror("Entrada inválida", "Selecciona nodos válidos.")
            return
        if start == goal:
            messagebox.showinfo("Mismos nodos", "El inicio y el destino deben ser distintos.")
            return
        algorithms: dict[str, Callable] = {"Dijkstra": self.graph.dijkstra, "Bellman-Ford": self.graph.bellman_ford, "Floyd-Warshall": self.graph.floyd_warshall, "A*": self.graph.a_star}
        self.steps, self.path, _ = algorithms[self.algorithm_var.get()](start, goal)
        self.current_step, self.running = -1, True
        self.play_button.configure(text="Ⅱ  PAUSAR")
        self.summary.configure(text=f"{self.algorithm_var.get()} · preparando ejecución", fg=CYAN)
        self.step_list.delete(*self.step_list.get_children())
        self.step_count.configure(text=f"{len(self.steps)} pasos")
        for index, step in enumerate(self.steps):
            icon = "◆" if step.kind == "path" else "•"
            self.step_list.insert("", "end", iid=str(index), text=f"{icon}  {index + 1:02d}   {step.title}\n      {step.detail}")
        self.animate()

    def animate(self):
        if not self.running:
            return
        self.current_step += 1
        if self.current_step >= len(self.steps):
            self.running = False
            self.play_button.configure(text="↺  REINICIAR")
            self.summary.configure(text=f"Ruta encontrada · costo {self.path_cost()}" if self.path else "No se encontró una ruta", fg=GREEN if self.path else RED)
            return
        self.render_step(self.current_step)
        self.animation_job = self.after(170, self.animate)

    def path_cost(self):
        return sum(next(weight for a, b, weight in self.edges if {a, b} == {left, right}) for left, right in zip(self.path, self.path[1:]))

    def render_step(self, index):
        step = self.steps[index]
        if self.step_list.selection() != (str(index),):
            self.updating_selection = True
            try:
                self.step_list.selection_set(str(index))
                self.step_list.see(str(index))
            finally:
                self.updating_selection = False
        else:
            self.step_list.see(str(index))
        self.draw_graph(step.nodes, step.edge, self.path if step.kind == "path" else (), step.nodes[0] if step.kind == "active" and step.nodes else None)
        self.summary.configure(text=f"Paso {index + 1} de {len(self.steps)} · {step.title}", fg=GREEN if step.kind == "path" else ORANGE)

    def select_step(self, _event=None):
        if self.updating_selection:
            return
        selected = self.step_list.selection()
        if not selected or self.running:
            return
        self.current_step = int(selected[0])
        self.render_step(self.current_step)

    def reset(self):
        self.running = False
        if self.animation_job:
            self.after_cancel(self.animation_job)
        self.steps, self.path, self.current_step = [], [], -1
        self.step_list.delete(*self.step_list.get_children())
        self.step_count.configure(text="0 pasos")
        self.summary.configure(text="Listo para explorar", fg=MUTED)
        self.play_button.configure(text="▶  EJECUTAR")
        self.draw_graph()
