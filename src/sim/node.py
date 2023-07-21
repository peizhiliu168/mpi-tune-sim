# Abstract Node class of a computation graph
from typing import List, Self

class Node:
    def __init__(self, name: str, input_nodes: List[Self] = []) -> None:
        self.input_nodes = input_nodes
        self.output_nodes = []
        self.output = None
        self.name = name
        
        for node in self.input_nodes:
            node.output_nodes.append(self)
            
            
    def compute(self, output=None) -> None:
        raise NotImplementedError
            
            
            