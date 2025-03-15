import sys
import os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.parsing.json_parser import parse_input
from common.petri_net.engine import fire_transition
import numpy as np

def is_enabled(marcado, incidence_negativa, t):
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
    incidence_positiva = np.array(incidence_positiva)
    incidence_negativa = np.array(incidence_negativa)
    marcado_inicial = np.array(marcado_inicial)
    incidence = incidence_positiva - incidence_negativa


    print(fire_transition(marcado_inicial, incidence, [1, 0]))

if __name__ == '__main__':
    main()


