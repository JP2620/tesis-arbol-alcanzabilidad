# Define directory paths
NETS_DIR := "data/nets"
TMP_DIR := "data/tmp"

# Define script paths
PFLOW_TO_JSON_SCRIPT := "scripts/pflow_to_json.py"
JSON_TRANSFORM_SCRIPT := "scripts/json_parser.py"

# Convert a .pflow file to a JSON file
pflow_to_json name:
    python3 {{PFLOW_TO_JSON_SCRIPT}} {{NETS_DIR}}/{{name}}.pflow {{TMP_DIR}}/{{name}}.json

# Transform the JSON file to a new schema (overwriting the same file)
transform_json name:
    python3 {{JSON_TRANSFORM_SCRIPT}} {{TMP_DIR}}/{{name}}.json

# Full process: Convert PFlow to JSON and then transform the JSON
process name:
    just pflow_to_json {{name}}
    just transform_json {{name}}

# Cleanup all temporary JSON files
clean_tmp:
    rm -f {{TMP_DIR}}/*

