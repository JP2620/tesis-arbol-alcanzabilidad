import time
import sys
import os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from collections import deque
from common.parsing.json_parser import parse_input
from common.petri_net.engine import fire_transition, get_enabled_transitions, update_marking
import numpy as np

def get_vectores_disparo_from_enabled_transitions(enabled_transitions):
    indices = np.where(enabled_transitions == 1)[0]
    result = []
    for idx in indices:
        new_arr = np.zeros_like(enabled_transitions)
        new_arr[idx] = 1
        result.append(new_arr)
        
    return result

def execute_petri_net(incidence_positiva, incidence_negativa, marcado_inicial):
    marcado_inicial = np.array(marcado_inicial)
    incidence_positiva = np.array(incidence_positiva)
    incidence_negativa = np.array(incidence_negativa)
    incidence = incidence_positiva - incidence_negativa

    marcados_visitados = set()
    marcados_visitados.add(tuple(marcado_inicial.tolist()))
    marcados_visitados_arr = np.array(marcado_inicial)

    firing_queue = deque()
    [
        firing_queue.append((marcado_inicial, vector_disparo))
        for vector_disparo in get_vectores_disparo_from_enabled_transitions(
            get_enabled_transitions(incidence_negativa, marcado_inicial)
        )
    ]

    tree_nodes = []
    tree_edges = []

    while not (len(firing_queue) == 0):
        marcado, vector_disparo = firing_queue.popleft()
        nuevo_marcado = update_marking(fire_transition(marcado, incidence, vector_disparo), marcados_visitados_arr)
        nuevo_marcado_tuple = tuple(nuevo_marcado.tolist())
        if nuevo_marcado_tuple not in marcados_visitados:
            marcados_visitados.add(nuevo_marcado_tuple)
            marcados_visitados_arr = np.vstack((marcados_visitados_arr, nuevo_marcado))
            tree_edges.append({
                "from": tuple(marcado.tolist())
                , "transition": int(np.nonzero(vector_disparo)[0][0]) + 1
                , "to": nuevo_marcado_tuple
            })
            nuevas_transiciones_enabled = get_enabled_transitions(incidence_negativa, nuevo_marcado)
            [firing_queue.append((nuevo_marcado, vector_disparo)) for vector_disparo in get_vectores_disparo_from_enabled_transitions(nuevas_transiciones_enabled)]
    tree_nodes = marcados_visitados

    return {
        "nodes": tree_nodes,
        "edges": tree_edges
    }

def write_to_dot(graph, output_path):
    """
    Writes a graph to a DOT file.
    
    Parameters:
        graph (dict): A dictionary with two keys:
                      - 'nodes': a set of nodes (e.g., {(-1, -1), (1, -1), (0, 2), ...})
                      - 'edges': a list of edge dictionaries, each with keys 'from', 'transition', and 'to'
        output_path (str): The file path where the DOT file will be written.
    """
    with open(output_path, "w") as file:
        # Start a directed graph
        file.write("digraph G {\n")
        
        # Write out each node.
        for node in graph['nodes']:
            # Represent the node as a string; you might choose a different label if needed.
            file.write(f'    "{node}" [label="[{", ".join([str(node) if node >= 0 else 'w' for node in list(node)])}]"];\n')
        
        # Write out each edge with its transition as a label.
        for edge in graph['edges']:
            src = edge['from']
            dst = edge['to']
            transition = edge['transition']
            file.write(f'    "{src}" -> "{dst}" [label="T{transition}"];\n')
        
        # Close the graph.
        file.write("}\n")


def main():
    import sys
    if len(sys.argv) != 3:
        print("Uso: python baseline_algorithm entrada.json salida.dot")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_path = sys.argv[2]

    incidence_positiva, incidence_negativa, marcado_inicial = parse_input(input_file)
    
    start_time = time.time()
    graph = execute_petri_net(incidence_positiva, incidence_negativa, marcado_inicial)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.4f} seconds")

    write_to_dot(graph, output_path)

if __name__ == '__main__':
    main()


