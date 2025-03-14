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
    """
    Verifica si la transición t está habilitada en el marcado actual.
    Una transición está habilitada si para cada lugar i se cumple:
      marcado[i] >= incidence_negativa[i][t]
    """
    return all(marcado[i] >= incidence_negativa[i][t] for i in range(len(marcado)))

def fire_transition(marcado, incidence_positiva, incidence_negativa, t):
    """
    Aplica la transición t sobre el marcado actual usando la ecuación de estado:
      M' = M - I^-[:, t] + I^+[:, t]
    Retorna el nuevo marcado.
    """
    nuevo_marcado = [
        marcado[i] - incidence_negativa[i][t] + incidence_positiva[i][t]
        for i in range(len(marcado))
    ]
    return nuevo_marcado

def execute_petri_net(incidence_positiva, incidence_negativa, marcado_inicial):
    """
    Ejecuta la red de Petri explorando todos los marcados alcanzables mediante
    una búsqueda en amplitud (BFS). Registra los nodos (estados) y las aristas
    (transiciones disparadas).
    
    Retorna:
      - visited: diccionario {tuple(marcado): nombre_estado}
      - edges: lista de tuplas (estado_origen, estado_destino, etiqueta_transición)
    """
    if not incidence_positiva or not incidence_positiva[0]:
        raise ValueError("La matriz de incidencia positiva no debe estar vacía")
    num_transiciones = len(incidence_positiva[0])
    
    # Inicialización de la búsqueda en amplitud
    queue = deque()
    visited = {}
    estado_inicial = tuple(marcado_inicial)
    visited[estado_inicial] = "M0"  # Asignamos el nombre "M0" al marcado inicial
    queue.append(estado_inicial)
    
    edges = []  # Aquí se almacenan las aristas: (origen, destino, etiqueta)
    contador_estados = 1
    
    while queue:
        actual = queue.popleft()
        for t in range(num_transiciones):
            if is_enabled(actual, incidence_negativa, t):
                nuevo = fire_transition(actual, incidence_positiva, incidence_negativa, t)
                nuevo_estado = tuple(nuevo)
                if nuevo_estado not in visited:
                    nombre_estado = f"M{contador_estados}"
                    visited[nuevo_estado] = nombre_estado
                    contador_estados += 1
                    queue.append(nuevo_estado)
                else:
                    nombre_estado = visited[nuevo_estado]
                # Registrar la transición disparada
                edges.append((visited[actual], nombre_estado, f"t{t}"))
    
    return visited, edges

def write_dot(visited, edges, output_file):
    """
    Escribe el resultado de la ejecución de la red en un archivo DOT.
    Cada nodo tiene como etiqueta la representación del marcado y cada arista
    indica la transición disparada.
    """
    with open(output_file, 'w') as f:
        f.write("digraph PetriNet {\n")
        # Escribir los nodos con su etiqueta (marcado)
        for marcado, nombre in visited.items():
            f.write(f'    {nombre} [label="{list(marcado)}"];\n')
        # Escribir las aristas con su etiqueta (transición)
        for origen, destino, etiqueta in edges:
            f.write(f'    {origen} -> {destino} [label="{etiqueta}"];\n')
        f.write("}\n")

def main():
    import sys
    if len(sys.argv) != 3:
        print("Uso: python petri_net.py entrada.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_path = sys.argv[2]
    incidence_positiva, incidence_negativa, marcado_inicial = parse_input(input_file)
    visited, edges = execute_petri_net(incidence_positiva, incidence_negativa, marcado_inicial)
    write_dot(visited, edges, output_path)
    print("Archivo DOT generado: petri_net.dot")

if __name__ == '__main__':
    main()

