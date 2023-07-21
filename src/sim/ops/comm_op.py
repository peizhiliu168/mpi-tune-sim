#       --------
#  0 -- |      | 
#  1 -- |      | 
#  .    | comm | -- out
#  .    |      | 
#  .    |      | 
#  N -- |      | 
#       ---------
# An input node to represent the inputs of the 
# computation graph

from mpi.communicator import Communicator
from sim.node import Node
from typing import List, Self


class Comm_Op(Node):
    def __init__(self, name: str, comm: Communicator, 
                 input_nodes: List[Node] = []) -> None:
        super().__init__(name, input_nodes)
        self.comm = comm
        
    def compute(self) -> None:
        # We're assuming there is no overlap between computation and 
        # collective operation
        # print("nodes", self.comm.nodes, "output", [node.output for node in self.input_nodes])        
        start = max([node.output for node in self.input_nodes]) 
        self.output = start + self.comm.evaluate()
    
    def add_input_node(self, node: Node) -> None:
        node.output_nodes.append(self)
        self.input_nodes.append(node)