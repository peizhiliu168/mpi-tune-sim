import csv
import glob
import json
import math
import os
from typing import Tuple
import numpy as np

from mpi.communicator import Communicator
from sim.graph import ComputationGraph
from sim.node import Node
from sim.ops.input_op import Input_Op
from sim.ops.comp_op import Comp_Op
from sim.ops.comm_op import Comm_Op
from utils.utils import overlap, str_2_list

class Parser:
    def __init__(self, root_dir: str) -> None:
        self.root_dir = root_dir
        self.comms: dict[int, Communicator] = {}
        
        
    def update_proc_computation_graph(self, proc_idx: int, graph: ComputationGraph) -> Node:
        cg_node_ct = 0
        
        # Obtain all cases of a specific process
        cases = glob.glob("{}/case_*/node_{}_trace.csv".format(self.root_dir, proc_idx))
        traces = [open(case, "r") for case in cases]
        # traces = [csv.reader(open(case, "r"), delimiter=",") for case in cases]
        headers = [trace.readline().strip().split(", ") for trace in traces]
        params = [json.load(open("{}/config.out".format(os.path.dirname(case)), "r"))['env'] for case in cases]
        
        # Get indices
        start_idx = headers[0].index("start (us)")
        end_idx = headers[0].index("end (us)")
        diff_idx = headers[0].index("diff (us)")
        ctx_idx =  headers[0].index("comm_ctx")
        nodes_idx = headers[0].index("nodes")
        coll_idx = headers[0].index("collective")
        
        # Stores number of times a comm has been called with a collective
        comm_cnt: dict[int, int] = {comm_hash: 0 for comm_hash in self.comms.keys()} 
        
        # Iterating through all lines of the trace
        starts = []
        ends = []
        prev_node = None
        for i, lines_str in enumerate(zip(*traces)):
            lines = [line.strip().split(", ") for line in lines_str]
            # The first trace is an initializaiton trace
            if i == 0:
                # Add the input node
                prev_node = Input_Op("{}_{}".format(proc_idx, cg_node_ct), 0.0)
                graph.insert_node(prev_node)
                cg_node_ct += 1
                
                # Add in the start and end
                starts.append([float(line[start_idx]) for line in lines])
                ends.append([float(line[end_idx]) for line in lines])
                
                continue
            
            # If comm is not defined (-1), skip this line
            if -1 in [int(line[coll_idx]) for line in lines]:
                continue
            
            # Create the comp nodes
            # The value of comp nodes indicates the time between collective calls
            # with negative values indicating overlapping collective calls
            start = [float(line[start_idx]) for line in lines]
            end = [float(line[end_idx]) for line in lines]
            
            max_avg_overlap = -math.inf
            for prev_start, prev_end in zip(starts[::-1], ends[::-1]):
                ovlp = [overlap(a_start, a_end, b_start, b_end) for a_start, a_end, b_start, b_end in zip(prev_start, prev_end, start, end)]
                                
                avg_ovlp = sum(ovlp) / len(ovlp)
                if avg_ovlp > max_avg_overlap:
                    max_avg_overlap = avg_ovlp

                    
                # When there is no overlap for any of the nodes, we have now 
                # determined the appropriate max overlap value
                if sum(n > 0 for n in ovlp) == 0:
                    break
                
            # Add in the start and end
            starts.append(start)
            ends.append(end)
            
            # Add comp node to computation graph
            prev_node = Comp_Op("{}_{}".format(proc_idx, cg_node_ct), prev_node, -max_avg_overlap)
            graph.insert_node(prev_node)
            cg_node_ct += 1
                    
                    
            # Validate the comms are all the same
            if (sum(line[ctx_idx] == lines[0][ctx_idx] for line in lines) != len(lines) or 
                sum(line[nodes_idx] == lines[0][nodes_idx] for line in lines) != len(lines)):
                print("Warning: Potentially misaligned collective calls")
                
            
            # Create the comm nodes
            comm_ctx_id = int(lines[0][ctx_idx])
            comm_nodes = str_2_list(lines[0][nodes_idx])
            
            comm_hash = hash((comm_ctx_id, tuple(comm_nodes)))
            if comm_hash in self.comms.keys():
                # Comm already exists in the computation graph
                comm = self.comms[comm_hash]
                
                # Check to see if comm op already exists in the computation graph
                if (len(comm.comm_ops) <= comm_cnt[comm_hash]):
                    # Need new comm node
                    comm_node = Comm_Op("{}_{}".format(proc_idx, cg_node_ct), comm, [prev_node])
                    comm.add_comm_op(comm_node)
                    cg_node_ct += 1
                    
                    # Add comm node to computation graph
                    graph.insert_node(comm_node)
                    
                    
                else:
                    # The comm node already exists
                    comm_node = comm.comm_ops[comm_cnt[comm_hash]]
                    comm_node.add_input_node(prev_node)
                    graph.insert_edge(comm_node, prev_node)
                    
                    
                comm_cnt[comm_hash] += 1
                prev_node = comm_node
                
                
            else:
                # Comm is not in the computation graph
                comm = Communicator(comm_ctx_id, comm_nodes)
                self.comms[comm_hash] = comm
                
                comm_node = Comm_Op("{}_{}".format(proc_idx, cg_node_ct), comm, [prev_node])
                cg_node_ct += 1
                
                comm.add_comm_op(comm_node)
                comm_cnt[comm_hash] = 1
                prev_node = comm_node
                
                # Add comm node to computation graph
                graph.insert_node(prev_node)
                

            
        return prev_node
        

    def parse_root_dir(self) -> Tuple[int, int]:
        root_dir_name = os.path.basename(self.root_dir)
        nodes = None
        ppn = None
        for pair in root_dir_name.split("_"):
            if "node" in pair:
                nodes = int(pair.replace("nodes", ""))
            elif "ppn" in pair:
                ppn = int(pair.replace("ppn", ""))
        
        return (nodes, ppn)