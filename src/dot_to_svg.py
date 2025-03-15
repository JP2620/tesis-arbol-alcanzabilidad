import sys
import pydot

def main():
    if len(sys.argv) != 3:
        print("Usage: dot_to_svg.py <input_dot_file> <output_svg_file>")
        sys.exit(1)
    
    input_dot_file = sys.argv[1]
    output_svg_file = sys.argv[2]
    
    try:
        # Load graphs from the dot file
        graphs = pydot.graph_from_dot_file(input_dot_file)
        if not graphs:
            print("Error: No graphs found in the dot file.")
            sys.exit(1)
        graph = graphs[0]
    except Exception as e:
        print(f"Error reading dot file: {e}")
        sys.exit(1)
    
    try:
        # Write the SVG file
        graph.write_svg(output_svg_file)
        print(f"SVG file generated successfully: {output_svg_file}")
    except Exception as e:
        print(f"Error writing svg file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
