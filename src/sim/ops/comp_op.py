#        -------
#  in -- | cmp | -- out
#        -------
# A normal compute node for representing simulation
# time between collective calls

from sim.node import Node

class Comp_Op(Node):
    def __init__(self, name: str, input_node: Node, val: float) -> None:
        super().__init__(name, [input_node])
        self.val = val
        
    def compute(self) -> None:
        self.output = self.input_nodes[0].output + self.val