import json

def parse_input(file_path):
    """
    Reads a JSON input file and extracts the positive incidence matrix,
    the negative incidence matrix, and the initial marking.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    incidence_positiva = data["incidence_positiva"]
    incidence_negativa = data["incidence_negativa"]
    marcado_inicial = data["marcado_inicial"]
    return incidence_positiva, incidence_negativa, marcado_inicial
