#!/usr/bin/env python3
import sys
import re

def parse_tina_output(lines):
    """
    Parses the Tina output file lines.
    Returns:
      - places: sorted list of place names (using union from input net and markings)
      - markings: dict mapping marking id (string) to dict of {place: token_count}
      - edges: list of tuples (source_marking, transition, dest_marking)
    """
    # Remove empty lines.
    lines = [line.strip() for line in lines if line.strip()]

    input_net_index = None
    markings_index = None
    reachability_index = None

    # Find indices for sections.
    for i, line in enumerate(lines):
        if line.startswith("INPUT NET"):
            input_net_index = i
        elif line.startswith("MARKINGS:"):
            markings_index = i
        elif line.startswith("REACHABILITY GRAPH:"):
            reachability_index = i

    # --- Extract place names ---
    # Try to get places from the INPUT NET section (lines starting with "pl ")
    places_set = set()
    if input_net_index is not None:
        i = input_net_index
        # Process until reaching the next section header (e.g., "REACHABILITY ANALYSIS")
        while i < len(lines) and not lines[i].startswith("REACHABILITY ANALYSIS"):
            if lines[i].startswith("pl "):
                # Expecting lines like: "pl P1 (1)"
                parts = lines[i].split()
                if len(parts) >= 2:
                    places_set.add(parts[1])
            i += 1

    # --- Parse MARKINGS ---
    # Each marking is given as:  "0 : P1 P4*2 P5"
    markings = {}
    if markings_index is not None:
        i = markings_index + 1
        while i < len(lines) and not lines[i].startswith("REACHABILITY GRAPH:"):
            m = re.match(r'(\d+)\s*:\s*(.*)', lines[i])
            if m:
                mark_id = m.group(1)
                marking_str = m.group(2)
                tokens = {}
                # Each token is either "P1" (one token) or "P4*2" (multiple tokens).
                for token in marking_str.split():
                    if '*' in token:
                        place, count = token.split('*')
                        tokens[place] = int(count)
                    else:
                        tokens[token] = 1
                    places_set.add(token.split('*')[0])
                markings[mark_id] = tokens
            i += 1

    # Use the union of places found; if some places never appear in the input net section,
    # they will be added from the markings.
    places = sorted(list(places_set), key=lambda x: int(x[1:]) if x[1:].isdigit() else x)

    # Ensure every marking has an entry for every place (filling missing ones with 0)
    for mark_id, tokens in markings.items():
        for p in places:
            if p not in tokens:
                tokens[p] = 0

    # --- Parse REACHABILITY GRAPH ---
    # Lines look like: "0 -> T1/1, T4/2"
    edges = []
    if reachability_index is not None:
        i = reachability_index + 1
        while i < len(lines):
            line = lines[i]
            m = re.match(r'(\d+)\s*->\s*(.*)', line)
            if m:
                src = m.group(1)
                transitions_part = m.group(2)
                # Split transitions on comma.
                for trans in transitions_part.split(','):
                    trans = trans.strip()
                    if trans:
                        # Each transition is like "T1/1": transition label and destination marking.
                        parts = trans.split('/')
                        if len(parts) == 2:
                            tr_label = parts[0]
                            dest = parts[1]
                            edges.append((src, tr_label, dest))
            i += 1

    return places, markings, edges

def build_tree(initial, edges):
    """
    Given the reachability edges, builds a tree (avoiding loops).
    Starting from the initial marking (string), we perform a DFS.
    Only add an edge if the destination marking hasn't been visited yet.
    Returns a list of tree edges: (source, transition, destination)
    """
    tree_edges = []
    visited = set()

    # Build an adjacency list for quick look-up.
    adj = {}
    for src, tr, dest in edges:
        if src not in adj:
            adj[src] = []
        adj[src].append((tr, dest))

    def dfs(current):
        visited.add(current)
        if current in adj:
            for tr, dest in adj[current]:
                if dest not in visited:
                    tree_edges.append((current, tr, dest))
                    dfs(dest)
    dfs(initial)
    return tree_edges

def write_dot(places, markings, tree_edges, output_file):
    """
    Writes the DOT file.
    Each node is labeled with the marking (one line per place as "P: count").
    Tree edges are added with their transition label.
    """
    dot_lines = []
    dot_lines.append("digraph ReachabilityTree {")
    # Create nodes with labels.
    for mark_id, tokens in markings.items():
        # Create a label string with each place's token count (one per line).
        label = "[" + ", ".join([str(tokens[p]) for p in places]) + "]"
        dot_lines.append(f'    "{mark_id}" [label="{label}"];')
    # Create tree edges.
    for src, tr, dest in tree_edges:
        dot_lines.append(f'    "{src}" -> "{dest}" [label="{tr}"];')
    dot_lines.append("}")

    with open(output_file, "w") as f:
        for line in dot_lines:
            f.write(line + "\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python tina_to_dot.py <input_tina_output_file> <output_dot_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, "r") as f:
        lines = f.readlines()

    places, markings, edges = parse_tina_output(lines)
    # Start from the initial marking "0".
    tree_edges = build_tree("0", edges)
    write_dot(places, markings, tree_edges, output_file)
    print(f"DOT file written to {output_file}")

if __name__ == "__main__":
    main()

