# A simulated communicator that corresponds to MPI comm

from typing import List

class Communicator:
    def __init__(self, ctx_id: int, nodes: List[int]) -> None:
        self.ctx_id = ctx_id
        self.nodes = nodes
        self.id = hash((ctx_id, tuple(nodes)))
        self.comm_ops = []
        
    def add_comm_op(self, op) -> None:
        self.comm_ops.append(op)
    
    def evaluate(self) -> float:
        return 0.0