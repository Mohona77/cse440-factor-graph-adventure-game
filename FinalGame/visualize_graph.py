import matplotlib.pyplot as plt
import networkx as nx


def draw_factor_graph():
    G = nx.DiGraph()

    # Nodes with layer info
    G.add_node("Forest", layer=0)
    G.add_node("Cave", layer=1)
    G.add_node("River", layer=1)
    G.add_node("Enemy", layer=2)
    G.add_node("Cross River", layer=2)
    G.add_node("Treasure", layer=3)

    # Edges
    G.add_edges_from([
        ("Forest", "Cave"),
        ("Forest", "River"),
        ("Cave", "Enemy"),
        ("River", "Cross River"),
        ("Enemy", "Treasure"),
        ("Cross River", "Treasure"),
    ])

    # Layout (hierarchy)
    pos = nx.multipartite_layout(G, subset_key="layer")

    # Thematic colors
    color_map = {
        "Forest": "green",
        "Cave": "saddlebrown",
        "River": "royalblue",
        "Enemy": "crimson",
        "Cross River": "purple",
        "Treasure": "gold"
    }

    node_colors = [color_map.get(node, "lightgray") for node in G.nodes()]

    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        edge_color="black",
        width=2,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=20
    )

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        node_size=3500,
        node_color=node_colors,
        edgecolors="black", linewidths=2
    )

    # Labels
    nx.draw_networkx_labels(
        G, pos,
        font_size=11,
        font_weight="bold",
        font_color="black"
    )

    plt.title("🌲 Adventure Game Decision Graph 🗺️",
              fontsize=16, fontweight="bold", pad=20)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    draw_factor_graph()
