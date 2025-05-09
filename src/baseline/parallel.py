"""
Module to compute the reachability tree of a Petri net composed of subnets.

Provides:
- Subnet: represents a subnetwork with local incidence matrices
- petri_reachability_tree: builds the global reachability tree
- nodes_to_dot: exports the reachability graph in DOT format
"""
from typing import List, Tuple, Dict, Any
import threading
import queue
import argparse
import json

Marking = Tuple[int, ...]
IncidenceMatrix = List[List[int]]
Node = Dict[str, Any]

class Subnet:
    """
    Represents a subnet within a Petri net, with its own local incidence matrices.

    Attributes:
        id (int): Unique identifier for the subnet.
        place_indices (List[int]): Global indices of places in this subnet.
        trans_indices (List[int]): Global indices of transitions in this subnet.
        I_minus (IncidenceMatrix): Local input incidence matrix.
        I_plus (IncidenceMatrix): Local output incidence matrix.
        global_to_local_t (Dict[int, int]): Mapping from global transition index to local index.
    """
    def __init__(
        self,
        id: int,
        place_indices: List[int],
        trans_indices: List[int],
        I_minus: IncidenceMatrix,
        I_plus: IncidenceMatrix,
    ) -> None:
        """
        Initialize a Subnet, extracting local incidence matrices from global matrices.

        Args:
            id: Unique identifier for this subnet.
            place_indices: Indices of places belonging to this subnet.
            trans_indices: Indices of transitions belonging to this subnet.
            I_minus: Global input incidence matrix (P x T).
            I_plus: Global output incidence matrix (P x T).
        """
        self.id: int = id
        self.place_indices: List[int] = place_indices
        self.trans_indices: List[int] = trans_indices
        # extract local incidence matrices
        self.I_minus: IncidenceMatrix = [
            [I_minus[p][t] for t in trans_indices] for p in place_indices
        ]
        self.I_plus: IncidenceMatrix = [
            [I_plus[p][t] for t in trans_indices] for p in place_indices
        ]
        # map global transition -> local index
        self.global_to_local_t: Dict[int, int] = {
            t: i for i, t in enumerate(trans_indices)
        }

    def fire(self, M_global: List[int], t: int) -> List[int]:
        """
        Fire transition t on the global marking for this subnet, returning the updated local marking.

        Args:
            M_global: The global marking (list of tokens in each place).
            t: Global index of the transition to fire.

        Returns:
            A list representing the new local marking for this subnet.
        """
        # compute current local marking
        local_m: List[int] = [M_global[p] for p in self.place_indices]
        if t not in self.global_to_local_t:
            return local_m
        lt: int = self.global_to_local_t[t]
        for i in range(len(self.place_indices)):
            local_m[i] = local_m[i] - self.I_minus[i][lt] + self.I_plus[i][lt]
        return local_m


def petri_reachability_tree(
    M0: List[int],
    I_minus: IncidenceMatrix,
    I_plus: IncidenceMatrix,
    subnets: List[Subnet],
    transition_subnets: Dict[int, List[int]],
) -> List[Node]:
    """
    Build the reachability tree of a Petri net by exploring enabled transitions from the initial marking.

    Args:
        M0: Initial global marking (list of tokens per place).
        I_minus: Global input incidence matrix.
        I_plus: Global output incidence matrix.
        subnets: List of Subnet objects composing the net.
        transition_subnets: Mapping from each global transition to the list of subnet IDs that include it.

    Returns:
        A list of nodes representing the reachability graph. Each node is a dict with keys:
        - name: unique node name (e.g., 'm_0')
        - label: text label for graph visualization
        - value: the marking tuple
        - from: parent node name or None
        - trans: transition index that led to this marking (for non-root nodes)
    """
    P: int = len(M0)
    T: int = len(I_minus[0]) if P > 0 else 0
    N: int = len(subnets)

    # Queues for communication
    input_queues: List[queue.Queue] = [queue.Queue() for _ in range(N)]
    result_queue: queue.Queue = queue.Queue()

    tasks_in_flight: int = 0
    tasks_lock = threading.Lock()

    nodes: List[Node] = []
    visited: set = set()

    def enqueue(M: List[int], t: int) -> None:
        nonlocal tasks_in_flight
        for sid in range(N):
            input_queues[sid].put((M, t))
            with tasks_lock:
                tasks_in_flight += 1

    def global_enabled(M: List[int]) -> List[int]:
        enabled: List[int] = []
        for t_idx in range(T):
            if all(M[p] >= I_minus[p][t_idx] for p in range(P)):
                enabled.append(t_idx)
        return enabled

    def worker(sid: int) -> None:
        """
        Worker thread for a given subnet ID to process fire requests.
        """
        while True:
            M, t = input_queues[sid].get()
            if M is None and t is None:
                break
            local_res = subnets[sid].fire(M, t)
            result_queue.put((tuple(M), t, sid, local_res))

    # Start worker threads
    threads: List[threading.Thread] = []
    for sid in range(N):
        thread = threading.Thread(target=worker, args=(sid,), daemon=True)
        thread.start()
        threads.append(thread)

    # Initialize root node
    nodes.append({
        "name": "m_0",
        "label": f"m_0\n{M0}",
        "value": tuple(M0),
        "from": None
    })
    visited.add(tuple(M0))

    # Seed initial transitions
    for t in global_enabled(M0):
        enqueue(M0, t)

    pending: Dict[Tuple[Marking, int], Dict[int, List[int]]] = {}
    counter: int = 1

    # Coordinator loop
    while True:
        M_repr, t, sid, local_m = result_queue.get()
        key = (M_repr, t)
        pending.setdefault(key, {})[sid] = local_m
        # If all subnets for this transition have responded
        if len(pending[key]) == len(transition_subnets[t]):
            # Merge local results into a new global marking
            new_M: List[int] = list(M_repr)
            for s_id, lm in pending[key].items():
                for idx, p_idx in enumerate(subnets[s_id].place_indices):
                    new_M[p_idx] = lm[idx]
            new_M_tup: Marking = tuple(new_M)
            del pending[key]

            if new_M_tup not in visited:
                visited.add(new_M_tup)
                name = f"m_{counter}"
                parent = next(n["name"] for n in nodes if n["value"] == M_repr)
                nodes.append({
                    "name": name,
                    "label": f"{name}\n{list(new_M_tup)}",
                    "value": new_M_tup,
                    "from": parent,
                    "trans": t
                })
                counter += 1
                for u in global_enabled(list(new_M_tup)):
                    enqueue(list(new_M_tup), u)

        # Decrement task count and break if done
        with tasks_lock:
            tasks_in_flight -= 1
            if tasks_in_flight == 0:
                break

    # Shutdown workers
    for q in input_queues:
        q.put((None, None))
    for thread in threads:
        thread.join()

    return nodes


def nodes_to_dot(nodes: List[Node]) -> str:
    """
    Convert a list of reachability nodes into a DOT graph representation.

    Args:
        nodes: List of node dictionaries from petri_reachability_tree.

    Returns:
        String containing the graph in DOT format.
    """
    lines: List[str] = ["digraph G {"]
    for n in nodes:
        lines.append(f'{n["name"]} [label="{n["label"]}"];')
    for n in nodes:
        if n.get("from"):
            lines.append(f'{n["from"]} -> {n["name"]} [label="t{n["trans"]}"];')
    lines.append("}")
    return "\n".join(lines)


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

    M0 = data["M0"]
    I_minus = data["I_minus"]
    I_plus = data["I_plus"]
    subnet_definitions_data = data["subnet_definitions"]

    # Reconstruct subnets
    # The Subnet class receives references to the global I_minus and I_plus
    # matrices, as in your original code.
    subnets = []
    for s_def in subnet_definitions_data:
        subnet = Subnet(
            s_def["id"],
            s_def["place_indices"],
            s_def["trans_indices"],
            I_minus,
            I_plus,
        )
        subnets.append(subnet)

    # Determine the number of transitions to correctly map transitions to subnets
    # This assumes I_minus (or I_plus) is not empty and is rectangular.
    num_transitions = 0
    if I_minus and len(I_minus) > 0 and len(I_minus[0]) > 0:
        num_transitions = len(I_minus[0])
    elif I_plus and len(I_plus) > 0 and len(I_plus[0]) > 0:
        num_transitions = len(I_plus[0])
    else:
        # Handle cases with no transitions if necessary, or raise an error.
        # For this example, if there are subnets, there should be transitions.
        if any(s_def["trans_indices"] for s_def in subnet_definitions_data):
            print(
                "Warning: Could not determine number of transitions, "
                "but subnets define transition indices."
            )
        # If no transitions are defined anywhere, 0 is fine.

    transition_subnets = {}
    for t in range(num_transitions):
        transition_subnets[t] = [
            s.id for s in subnets if t in s.trans_indices
        ]

    # Call the main logic using the loaded and reconstructed data
    nodes = petri_reachability_tree(
        M0, I_minus, I_plus, subnets, transition_subnets
    )
    dot_output = nodes_to_dot(nodes)
    print("\nGenerated DOT output:")
    print(dot_output)
