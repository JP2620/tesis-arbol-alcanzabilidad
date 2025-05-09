from typing import List, Tuple, Dict, Any
import threading
import queue
import argparse
import json
import numpy as np
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common.petri_net.engine import get_enabled_transitions, fire_transition, update_marking

def extract_subnet_matrices(
    global_I_minus: np.ndarray,
    global_I_plus: np.ndarray,
    place_indices: List[int],
    trans_indices: List[int]
) -> Tuple[np.ndarray, np.ndarray, Dict[int, int]]:
    """Extract local incidence matrices for a subnet."""
    # Extract local matrices
    local_I_minus = global_I_minus[place_indices, :][:, trans_indices]
    local_I_plus = global_I_plus[place_indices, :][:, trans_indices]
    
    # Map global transition -> local index
    global_to_local_t = {t: i for i, t in enumerate(trans_indices)}
    
    return local_I_minus, local_I_plus, global_to_local_t

def subnet_fire(
    global_marking: np.ndarray,
    transition: int,
    place_indices: List[int],
    trans_indices: List[int],
    local_I_minus: np.ndarray,
    local_I_plus: np.ndarray,
    global_to_local_t: Dict[int, int]
) -> np.ndarray:
    """Fire a transition in a subnet and return the updated local marking."""
    # Compute current local marking
    local_marking = global_marking[place_indices].copy()
    
    # Skip if transition not in this subnet
    if transition not in global_to_local_t:
        return local_marking
        
    # Get local transition index
    local_t = global_to_local_t[transition]
    
    # Create firing vector (one-hot encoded)
    firing_vector = np.zeros(len(trans_indices), dtype=int)
    firing_vector[local_t] = 1
    
    # Calculate local incidence matrix
    local_incidence = local_I_plus - local_I_minus
    
    # Fire transition using provided function
    return fire_transition(local_marking, local_incidence, firing_vector)

def petri_reachability_tree(
    M0: List[int],
    I_minus: List[List[int]],
    I_plus: List[List[int]],
    subnet_definitions: List[Dict]
) -> List[Dict]:
    """Build reachability tree for a Petri net composed of subnets."""
    # Convert inputs to numpy arrays
    M0_np = np.array(M0, dtype=int)
    I_minus_np = np.array(I_minus, dtype=int)
    I_plus_np = np.array(I_plus, dtype=int)
    
    # Get dimensions
    num_places = len(M0_np)
    num_transitions = I_minus_np.shape[1] if num_places > 0 else 0
    num_subnets = len(subnet_definitions)
    
    # Process subnet definitions
    subnet_data = []
    for s_def in subnet_definitions:
        place_indices = np.array(s_def["place_indices"], dtype=int)
        trans_indices = np.array(s_def["trans_indices"], dtype=int)
        local_I_minus, local_I_plus, global_to_local_t = extract_subnet_matrices(
            I_minus_np, I_plus_np, place_indices, trans_indices
        )
        subnet_data.append({
            "id": s_def["id"],
            "place_indices": place_indices,
            "trans_indices": trans_indices,
            "local_I_minus": local_I_minus,
            "local_I_plus": local_I_plus,
            "global_to_local_t": global_to_local_t
        })
    
    # Map transitions to subnets
    transition_subnets = {}
    for t in range(num_transitions):
        transition_subnets[t] = [
            s["id"] for s in subnet_data if t in s["trans_indices"]
        ]
    
    # Communication queues
    input_queues = [queue.Queue() for _ in range(num_subnets)]
    result_queue = queue.Queue()
    
    tasks_in_flight = 0
    tasks_lock = threading.Lock()
    
    nodes = []
    visited = set()
    known_markings = [M0_np]  # For omega substitution
    
    def enqueue(marking, transition):
        nonlocal tasks_in_flight
        for sid in range(num_subnets):
            input_queues[sid].put((marking.copy(), transition))
            with tasks_lock:
                tasks_in_flight += 1
    
    def worker(subnet_id):
        """Worker thread for subnet processing."""
        subnet = subnet_data[subnet_id]
        while True:
            marking, transition = input_queues[subnet_id].get()
            if marking is None and transition is None:
                break
                
            local_result = subnet_fire(
                marking,
                transition,
                subnet["place_indices"],
                subnet["trans_indices"],
                subnet["local_I_minus"],
                subnet["local_I_plus"],
                subnet["global_to_local_t"]
            )
            
            result_queue.put((marking, transition, subnet_id, local_result))
    
    # Start worker threads
    threads = []
    for sid in range(num_subnets):
        thread = threading.Thread(target=worker, args=(sid,), daemon=True)
        thread.start()
        threads.append(thread)
    
    # Initialize root node
    nodes.append({
        "name": "m_0",
        "label": f"m_0\n{M0_np.tolist()}",
        "value": M0_np,
        "from": None
    })
    visited.add(tuple(M0_np.tolist()))  # Convert to tuple of Python ints for hashability
    
    # Find initial enabled transitions
    enabled = get_enabled_transitions(I_minus_np, M0_np)
    enabled_indices = np.where(enabled == 1)[0]
    
    # Seed initial transitions
    for t in enabled_indices:
        enqueue(M0_np, int(t))
    
    pending = {}
    counter = 1
    
    # Coordinator loop
    while True:
        orig_marking, transition, subnet_id, local_marking = result_queue.get()
        
        # Use tuple of marking as key for dictionary
        marking_tuple = tuple(orig_marking.tolist())
        key = (marking_tuple, transition)
        
        # Initialize dictionary for this key if needed
        if key not in pending:
            pending[key] = {}
            
        pending[key][subnet_id] = local_marking
        
        # If all required subnets have responded
        if len(pending[key]) == len(transition_subnets[transition]):
            # Merge local results into a new global marking
            new_marking = orig_marking.copy()
            for sid, local_m in pending[key].items():
                subnet = subnet_data[sid]
                for idx, p_idx in enumerate(subnet["place_indices"]):
                    new_marking[p_idx] = local_m[idx]
            
            # Apply omega substitution using known markings
            known_markings_np = np.array(known_markings)
            updated_marking = update_marking(new_marking, known_markings_np)
            
            # Convert to tuple for set comparison
            new_marking_tuple = tuple(updated_marking.tolist())
            
            # Clean up
            del pending[key]
            
            # Process if new marking
            if new_marking_tuple not in visited:
                visited.add(new_marking_tuple)
                known_markings.append(updated_marking.copy())
                
                name = f"m_{counter}"
                parent = next(n["name"] for n in nodes if tuple(n["value"].tolist()) == marking_tuple)
                
                nodes.append({
                    "name": name,
                    "label": f"{name}\n{updated_marking.tolist()}",
                    "value": updated_marking,
                    "from": parent,
                    "trans": transition
                })
                
                counter += 1
                
                # Find newly enabled transitions
                enabled = get_enabled_transitions(I_minus_np, updated_marking)
                enabled_indices = np.where(enabled == 1)[0]
                
                # Queue new enabled transitions
                for new_t in enabled_indices:
                    enqueue(updated_marking, int(new_t))
        
        # Update task counter
        with tasks_lock:
            tasks_in_flight -= 1
            if tasks_in_flight == 0:
                break
    
    # Shutdown worker threads
    for q in input_queues:
        q.put((None, None))
    for thread in threads:
        thread.join()
    
    return nodes

def nodes_to_dot(nodes: List[Dict]) -> str:
    """Convert reachability nodes to DOT graph format."""
    lines = ["digraph G {"]
    
    for node in nodes:
        # Convert numpy array to list for display
        if isinstance(node["value"], np.ndarray):
            label = f"{node['name']}\n{node['value'].tolist()}"
        else:
            label = node["label"]
        lines.append(f'{node["name"]} [label="{label}"];')
    
    for node in nodes:
        if node.get("from"):
            lines.append(f'{node["from"]} -> {node["name"]} [label="t{node["trans"]}"];')
    
    lines.append("}")
    return "\n".join(lines)

def fix_numpy_serialization(data):
    """Fix NumPy serialization issues in JSON data."""
    if isinstance(data, list):
        return [fix_numpy_serialization(item) for item in data]
    elif isinstance(data, dict):
        return {k: fix_numpy_serialization(v) for k, v in data.items()}
    elif "numpy" in str(type(data)):
        # Convert NumPy types to native Python types
        return data.item() if hasattr(data, 'item') else float(data)
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate Petri net reachability tree from JSON input."
    )
    parser.add_argument(
        "json_file", help="Path to the JSON file containing Petri net inputs."
    )
    args = parser.parse_args()
    
    try:
        with open(args.json_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {args.json_file}")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {args.json_file}")
        exit(1)
    
    # Fix any NumPy serialization issues
    data = fix_numpy_serialization(data)
    
    M0 = data["M0"]
    I_minus = data["I_minus"]
    I_plus = data["I_plus"]
    subnet_definitions = data["subnet_definitions"]
    
    nodes = petri_reachability_tree(M0, I_minus, I_plus, subnet_definitions)
    dot_output = nodes_to_dot(nodes)
    print("\nGenerated DOT output:")
    print(dot_output)
