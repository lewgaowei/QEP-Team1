import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def make_node_shape(node_type, ax, pos, radius=0.2):
    if node_type in ["Hash Join", "Nested Loop", "Merge Join"]:
        shape = FancyBboxPatch((pos[0]-radius, pos[1]-radius), 2*radius, 2*radius, boxstyle="circle", fc="skyblue", ec="black")
    elif node_type in ["Seq Scan", "Index Scan", "Values Scan", "Index Only Scan", "Subquery Scan", "Function Scan"]:
        shape = FancyBboxPatch((pos[0]-1.5*radius, pos[1]-radius/2), 3*radius, radius, boxstyle="round,pad=0.1", fc="lightgreen", ec="black")
    elif node_type in ["Sort", "Aggregate"]:
        shape = FancyBboxPatch((pos[0]-radius, pos[1]-radius), 2*radius, 2*radius, boxstyle="round,pad=0.2", fc="pink", ec="black")
    else:
        shape = FancyBboxPatch((pos[0]-radius, pos[1]-radius), 2*radius, 2*radius, fc="orange", ec="black")
    ax.add_patch(shape)
    return shape

def create_and_draw_graph(query_plan):
    G = nx.DiGraph()
    node_counter = 1

    def add_nodes_and_edges(plan, parent_id=None):
        nonlocal node_counter
        node_id = node_counter
        node_label = (
            f"{plan['Node Type']}\n"
             f"Relation Name: {plan.get('Relation Name', 'N/A')}\n"
            f"Total Cost: {plan.get('Total Cost', 'N/A')}\n"
            f"Actual Total Time: {plan.get('Actual Total Time', 'N/A')}\n"
            f"Startup Cost: {plan.get('Startup Cost', 'N/A')}\n"
            f"Actual Startup Time: {plan.get('Actual Startup Time', 'N/A')}\n"
            f"Buffer Hits: {plan.get('Shared Hit Blocks', 'N/A')}\n"
        )

        
        G.add_node(node_id, label=node_label, type=plan['Node Type'])
        
        if parent_id is not None:
            G.add_edge(node_id, parent_id)  

        node_counter += 1

        if 'Plans' in plan:
            for subplan in plan['Plans']:
                add_nodes_and_edges(subplan, node_id)

    add_nodes_and_edges(query_plan['Plan'])

    pos = nx.spring_layout(G)  

    fig, ax = plt.subplots(figsize=(15, 15))

    for node in G.nodes:
        node_type = G.nodes[node]['type']
        make_node_shape(node_type, ax, pos[node])

    # Draw the edges
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='black', arrows=True)
    nx.draw_networkx_labels(G, pos, ax=ax, labels=nx.get_node_attributes(G, 'label'), font_size=10)

    plt.axis('off')
    plt.show()



if __name__ == "__main__":
    pass



