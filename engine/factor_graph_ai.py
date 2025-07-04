# engine/factor_graph_ai.py
from pgmpy.models import FactorGraph
from pgmpy.factors.discrete import DiscreteFactor
import random
import matplotlib.pyplot as plt
import networkx as nx


class AIDecisionEngine:
    def __init__(self):
        self.graph = FactorGraph()
        self._build_graph()

    def _build_graph(self):
        self.graph.add_nodes_from(['energy', 'reputation', 'action'])
        factor = DiscreteFactor(
            ['energy', 'reputation', 'action'],
            [3, 3, 3],
            [
                0.3, 0.3, 0.4,
                0.2, 0.5, 0.3,
                0.4, 0.3, 0.3,
                0.5, 0.2, 0.3,
                0.3, 0.3, 0.4,
                0.2, 0.4, 0.4,
                0.3, 0.4, 0.3,
                0.4, 0.3, 0.3,
                0.3, 0.2, 0.5
            ]
        )
        self.graph.add_factors(factor)
        self.graph.add_edges_from([
            ('energy', factor),
            ('reputation', factor),
            ('action', factor)
        ])

    def suggest(self, energy, reputation, choices):
        if energy <= 0:
            return min(choices, key=len)
        if reputation > 2 and "fight" in choices:
            return "fight"
        return random.choice(list(choices))

    def show_graph(self):
        G = nx.Graph()
        G.add_node("energy", color='skyblue')
        G.add_node("reputation", color='lightgreen')
        G.add_node("action", color='orange')
        G.add_node("factor", color='gray')

        G.add_edges_from([
            ("energy", "factor"),
            ("reputation", "factor"),
            ("action", "factor")
        ])

        colors = [G.nodes[n].get("color", "white") for n in G.nodes]
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color=colors, node_size=2000)
        plt.title("Factor Graph (AI Decision Engine)")
        plt.show()
