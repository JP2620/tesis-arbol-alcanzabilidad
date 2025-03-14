# -------------------------------------------------------------------
# Directory Configuration
# -------------------------------------------------------------------
NETS_DIR := "data/nets"
TMP_DIR := "data/tmp"
SCRIPTS_DIR := "scripts"

# -------------------------------------------------------------------
# TINA Pipeline: Ground Truth Reachability Tree Generation
# -------------------------------------------------------------------

# Step 1: Generate the reachability tree for a given PNML file using TINA.
get_tree name:
	{{SCRIPTS_DIR}}/tina {{NETS_DIR}}/{{name}}.pnml > {{TMP_DIR}}/tina_out_{{name}}.txt

# Step 2: Convert TINA's output to a DOT graph for debugging purposes.
get_tree_graph name:
	python {{SCRIPTS_DIR}}/tina_to_dot_graph.py \
	    {{TMP_DIR}}/tina_out_{{name}}.txt {{TMP_DIR}}/tina_graph_{{name}}.dot

# Step 3: Convert the DOT graph to an SVG file for browser visualization.
dot_to_svg name:
	python {{SCRIPTS_DIR}}/dot_to_svg.py \
	    {{TMP_DIR}}/tina_graph_{{name}}.dot {{TMP_DIR}}/tina_graph_{{name}}.svg

# Composite Task: Run the full TINA pipeline.
tina_process name:
	just get_tree {{name}}
	just get_tree_graph {{name}}
	just dot_to_svg {{name}}

# -------------------------------------------------------------------
# Custom Algorithm Pipeline
# -------------------------------------------------------------------

# Step 1: Convert the PNML file into a JSON file containing algorithm arguments.
pnml_to_json_args name:
	python {{SCRIPTS_DIR}}/pnml_to_json.py {{NETS_DIR}}/{{name}}.pnml {{NETS_DIR}}/{{name}}.json

# Step 2: Run the custom algorithm using the JSON file, outputting a DOT file.
our_algorithm name:
	python {{SCRIPTS_DIR}}/baseline_algorithm.py {{NETS_DIR}}/{{name}}.json {{TMP_DIR}}/our_graph_{{name}}.dot

# Step 3: Convert the algorithm's DOT output to an SVG for visualization.
our_dot_to_svg name:
	python {{SCRIPTS_DIR}}/dot_to_svg.py \
	    {{TMP_DIR}}/our_graph_{{name}}.dot {{TMP_DIR}}/our_graph_{{name}}.svg

# Composite Task: Run the full pipeline for the custom algorithm.
our_process name:
	just pnml_to_json_args {{name}}
	just our_algorithm {{name}}
	just our_dot_to_svg {{name}}

# -------------------------------------------------------------------
# Utility: Clean Up Temporary Files
# -------------------------------------------------------------------

# Remove all files in the temporary directory.
clean_tmp:
	rm -f {{TMP_DIR}}/*

