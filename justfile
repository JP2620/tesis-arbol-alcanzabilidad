# Define directory paths
NETS_DIR := "data/nets"
TMP_DIR := "data/tmp"
SCRIPTS_DIR := "scripts"


# Define script paths
PNML_TO_JSON_SCRIPT := "scripts/pnml_to_json.py"

get_tree name:
    {{SCRIPTS_DIR}}/tina {{NETS_DIR}}/{{name}}.pnml > {{TMP_DIR}}/tina_out_{{name}}.txt

get_tree_graph name:
    python {{SCRIPTS_DIR}}/tina_to_dot_graph.py \
        {{TMP_DIR}}/tina_out_{{name}}.txt {{TMP_DIR}}/tina_graph_{{name}}.dot

tina_process name:
    just get_tree {{name}}
    just get_tree_graph {{name}}

# Cleanup all temporary JSON files
clean_tmp:
    rm -f {{TMP_DIR}}/*

