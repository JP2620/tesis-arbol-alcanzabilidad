import json
import pytest
import os
from common.parsing.json_parser import parse_input

# Sample JSON data
sample_data = {
    "incidence_positiva": [[1, 0], [0, 1]],
    "incidence_negativa": [[0, 1], [1, 0]],
    "marcado_inicial": [1, 0]
}

@pytest.fixture
def sample_json_file(tmp_path):
    """Creates a temporary JSON file with sample Petri net data."""
    file_path = tmp_path / "sample_input.json"
    with open(file_path, "w") as f:
        json.dump(sample_data, f)
    return file_path

def test_parse_input(sample_json_file):
    """Test if parse_input correctly extracts Petri net components."""
    incidence_positiva, incidence_negativa, marcado_inicial = parse_input(sample_json_file)

    assert incidence_positiva == [[1, 0], [0, 1]], "Incorrect positive incidence matrix"
    assert incidence_negativa == [[0, 1], [1, 0]], "Incorrect negative incidence matrix"
    assert marcado_inicial == [1, 0], "Incorrect initial marking"
