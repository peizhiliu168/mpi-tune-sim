#   ---------
#   | input | --
#   ---------
# An input node to represent the inputs of the 
# computation graph

from sim.node import Node

class Input_Op(Node):
    def __init__(self, name: str, val: float = 0.0) -> None:
        super().__init__(name, [])
        self.val = val
        
    def compute(self) -> None:
        self.output = self.val