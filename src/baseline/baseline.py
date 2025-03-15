import json
from collections import deque

def parse_input(file_path):
    """
    Lee el archivo JSON de entrada y extrae la matriz de incidencia positiva,
    la matriz de incidencia negativa y el marcado inicial.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    incidence_positiva = data["incidence_positiva"]
    incidence_negativa = data["incidence_negativa"]
    marcado_inicial = data["marcado_inicial"]
    return incidence_positiva, incidence_negativa, marcado_inicial

def is_enabled(marcado, incidence_negativa, t):
    pass

def fire_transition(marcado, incidence_positiva, incidence_negativa, t):
    pass

def execute_petri_net(incidence_positiva, incidence_negativa, marcado_inicial):
    pass


def main():
    import sys
    if len(sys.argv) != 3:
        print("Uso: python baseline_algorithm entrada.json salida.dot")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_path = sys.argv[2]
    incidence_positiva, incidence_negativa, marcado_inicial = parse_input(input_file)

if __name__ == '__main__':
    main()


