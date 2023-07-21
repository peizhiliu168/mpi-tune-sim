# Computation graph representing the simulation execution
import networkx as nx
from typing import Generator
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


from sim.node import Node


class ComputationGraph:
    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.sorted = False
        self.node_gen: Generator[Node] = None
        self.int_to_node: dict[int, Node] = {}
    
    def insert_node(self, node: Node) -> None:
        self.sorted = False
        self.graph.add_node(node.name, data=node)
        if node.input_nodes:
            self.graph.add_edges_from([(u.name, node.name) for u in node.input_nodes])
            
    def insert_edge(self, node: Node, prev_node: Node) -> None:
        self.graph.add_edge(prev_node.name, node.name)
    
    def topological_sort(self) -> None:
        self.node_gen = nx.topological_sort(self.graph)
        self.sorted = True
        
    def compute(self) -> None:
        if not self.sorted or self.node_gen == None:
            self.topological_sort()
            
        for node in self.node_gen:
            computation_node = self.graph.nodes[node]['data']
            computation_node.compute()
    
    def draw(self, path: str) -> None:
        # nx.draw(self.graph)
        pos=graphviz_layout(self.graph, prog='dot')
        nx.draw(self.graph, pos)
        plt.savefig(path)
        