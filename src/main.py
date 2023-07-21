from sim.graph import ComputationGraph
from utils.parser import Parser

def main():
    print("Starting simulation")
    
    # Define new computation graph
    cg = ComputationGraph()
    
    print("Ingesting data...")
    
    # Ingest data for each node
    parser = Parser("/home/peizhi/mpi-tune/trace_results/SWFFT/nodes32_ppn1")
    (nodes, ppn) = parser.parse_root_dir()
    output_nodes = []
    
    for proc_idx in range(nodes * ppn):
        print("Updating computation graph with process", proc_idx)
        output_node = parser.update_proc_computation_graph(proc_idx, cg)
        output_nodes.append(output_node)
        # break
    
        
    # With new computation graph, perform a topological sort to determine traversal order
    print("Sorting computation graph topologically")
    cg.topological_sort()
    # cg.draw("cg.png")
    
    # Then perform computation from input to output of computation graph
    print("Evaluating computation graph")
    cg.compute()
    
    # Computed results should now be stored in output nodes
    print([node.output for node in output_nodes])
    
        




if __name__ == "__main__":
    main()