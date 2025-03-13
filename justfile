# Define directory paths
NETS_DIR := "data/nets"
TMP_DIR := "data/tmp"

# Define script paths
TRANSLATE_SCRIPT := "scripts/pflow_to_json.py"

# Recipe to translate a .pflow file to .json
translate name:
    python3 {{TRANSLATE_SCRIPT}} {{NETS_DIR}}/{{name}}.pflow {{TMP_DIR}}/{{name}}.json

clear:
  rm {{TMP_DIR}}/*

