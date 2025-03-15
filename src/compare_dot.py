#!/usr/bin/env python3
import re
import sys

def extract_node_labels(filename):
    """
    Extracts node labels from a DOT file.
    Skips lines that define edges (which contain '->').
    """
    labels = set()
    with open(filename, 'r') as f:
        for line in f:
            # Skip lines that likely define edges.
            if "->" in line:
                continue
            # Look for node definitions with a label attribute.
            match = re.search(r'\[label\s*=\s*"([^"]+)"\]', line)
            if match:
                labels.add(match.group(1))
    return labels

def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_dot.py file1.dot file2.dot")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]
    labels1 = extract_node_labels(file1)
    labels2 = extract_node_labels(file2)
    
    # Print True if the sets of labels are identical, else False.
    print(labels1 == labels2)

if __name__ == "__main__":
    main()

