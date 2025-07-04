# engine/factor_graph_ai.py

from pgmpy.models import FactorGraph
from pgmpy.factors.discrete import DiscreteFactor
from pgmpy.inference import BeliefPropagation
import random
import matplotlib.pyplot as plt
import networkx as nx


class AIDecisionEngine:
    def __init__(self):
        self.graph = FactorGraph()
        self._build_graph()

        # Action mapping for inference
        self.action_map = {"rest": 0, "sneak": 1, "fight": 2}
        self.reverse_map = {v: k for k, v in self.action_map.items()}

    def _build_graph(self):
        self.graph.add_nodes_from(['energy', 'reputation', 'action'])

        # Factor potential: (energy, reputation, action)
        factor = DiscreteFactor(
            ['energy', 'reputation', 'action'],
            [3, 3, 3],  # energy: 0–2, reputation: 0–2, action: 0–2
            [
                # Low energy (0)
                0.7, 0.2, 0.1,   # rep 0 → prefer rest
                0.6, 0.3, 0.1,   # rep 1
                0.5, 0.3, 0.2,   # rep 2

                # Medium energy (1)
                0.4, 0.4, 0.2,
                0.3, 0.5, 0.2,
                0.2, 0.5, 0.3,

                # High energy (2)
                0.1, 0.3, 0.6,
                0.1, 0.2, 0.7,
                0.1, 0.1, 0.8    # rep 2 → prefer fight
            ]
        )

        self.graph.add_factors(factor)
        self.graph.add_edges_from([
            ('energy', factor),
            ('reputation', factor),
            ('action', factor)
        ])

    def suggest(self, energy, reputation, choices):
        # Map energy and rep to [0–2]
        energy = max(0, min(2, energy))
        reputation = max(0, min(2, reputation))

        inference = BeliefPropagation(self.graph)
        result = inference.map_query(
            variables=['action'],
            evidence={'energy': energy, 'reputation': reputation}
        )

        best_action_idx = result['action']
        best_action = self.reverse_map.get(best_action_idx)

        # Try to match the action name in available choices
        for c in choices:
            if best_action in c.lower():
                return c

        # fallback: random
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

