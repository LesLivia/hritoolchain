from graphviz import Digraph

from domain.hafeatures import HybridAutomaton

SAVE_PATH = 'resources/learned_ha/'


def plot_ha(ha: HybridAutomaton, name: str):
    f = Digraph('hybrid_automaton', filename=SAVE_PATH + name)
    f.attr(rankdir='LR', size='8,5')
    f.attr('node', shape='circle')

    locations = ha.locations
    edges = ha.edges

    for loc in locations:
        f.node(loc.name)

    for edge in edges:
        f.edge(edge.start.name, edge.dest.name, label=edge.guard)

    f.view()
