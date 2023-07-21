
from enum import Enum

class EventType(Enum):
    PROC_STEP = 0
    PROC_DONE = 1
    COMM_START = 2
    COMM_END = 3

coll2val = {
    "AllGather": 0,
    "AllReduce": 1,
    "AlltoAlll": 2,
    "Bcast": 3,
    "Other": 4
}

val2coll = {v: k for k, v in coll2val.items()}

def overlap(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    return min(a_end, b_end) - max(a_start, b_start)

def str_2_list(s: str) -> list:
    return [int(node_val) for node_val in s.strip('][\"').split(',')]
