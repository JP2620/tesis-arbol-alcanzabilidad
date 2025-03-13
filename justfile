# Define directory paths
NETS_DIR := "data/nets"
TMP_DIR := "data/tmp"
SCRIPTS_DIR := "scripts"

get_tree name:
	{{SCRIPTS_DIR}}/tina {{NETS_DIR}}/{{name}}.pnml > {{TMP_DIR}}/tina_out_{{name}}.txt

get_tree_graph name:
	python {{SCRIPTS_DIR}}/tina_to_dot_graph.py \
	    {{TMP_DIR}}/tina_out_{{name}}.txt {{TMP_DIR}}/tina_graph_{{name}}.dot

dot_to_svg name:
	python {{SCRIPTS_DIR}}/dot_to_svg.py \
	    {{TMP_DIR}}/tina_graph_{{name}}.dot {{TMP_DIR}}/tina_graph_{{name}}.svg

tina_process name:
	just get_tree {{name}}
	just get_tree_graph {{name}}
	just dot_to_svg {{name}}

# Cleanup all temporary files
clean_tmp:
	rm -f {{TMP_DIR}}/*
