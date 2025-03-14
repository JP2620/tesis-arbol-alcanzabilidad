# Define directory paths
NETS_DIR := "data/nets"
TMP_DIR := "data/tmp"
SCRIPTS_DIR := "scripts"

# We get the verified result for the petri net with tina
get_tree name:
	{{SCRIPTS_DIR}}/tina {{NETS_DIR}}/{{name}}.pnml > {{TMP_DIR}}/tina_out_{{name}}.txt

# We have to visualize it to debug it so we create a dot file with the result
get_tree_graph name:
	python {{SCRIPTS_DIR}}/tina_to_dot_graph.py \
	    {{TMP_DIR}}/tina_out_{{name}}.txt {{TMP_DIR}}/tina_graph_{{name}}.dot

# We convert it to a svg to be able to open it in our browser
dot_to_svg name:
	python {{SCRIPTS_DIR}}/dot_to_svg.py \
	    {{TMP_DIR}}/tina_graph_{{name}}.dot {{TMP_DIR}}/tina_graph_{{name}}.svg

# pnml to algorithm args json
pnml_to_json_args name:
	python {{SCRIPTS_DIR}}/pnml_to_json.py {{NETS_DIR}}/{{name}}.pnml {{NETS_DIR}}/{{name}}.json

# We run our algorithm
our_algorithm name:
	python {{SCRIPTS_DIR}}/baseline_algorithm.py {{NETS_DIR}}/{{name}}.json {{TMP_DIR}}/our_graph_{{name}}.dot

our_dot_to_svg name:
	python {{SCRIPTS_DIR}}/dot_to_svg.py \
	    {{TMP_DIR}}/our_graph_{{name}}.dot {{TMP_DIR}}/our_graph_{{name}}.svg

our_process name:
	just pnml_to_json_args {{name}}
	just our_algorithm {{name}}
	just our_dot_to_svg {{name}}

tina_process name:
	just get_tree {{name}}
	just get_tree_graph {{name}}
	just dot_to_svg {{name}}

# Cleanup all temporary files
clean_tmp:
	rm -f {{TMP_DIR}}/*
