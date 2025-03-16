import numpy as np

def fire_transition(marcado, incidence, vector_disparo):
    nuevo_marcado = marcado + np.dot(incidence, vector_disparo)
    # Restauramos las plazas no acotadas: donde el marcado original es -1 se mantiene -1.
    nuevo_marcado[marcado == -1] = -1
    return nuevo_marcado

def get_enabled_transitions(incidencia_negativa: np.ndarray, marcado: np.ndarray) -> np.ndarray:
    """
    Determina qué transiciones están habilitadas en una red de Petri.
    
    Parámetros:
      matriz_neg : numpy.array de tamaño (n_plazas, n_transiciones)
                   Cada elemento representa los tokens requeridos de una plaza para que se dispare la transición.
      marcado    : numpy.array de tamaño (n_plazas,)
                   Representa el número de tokens en cada plaza. 
                   Se usa el valor -1 para indicar que la plaza es no acotada.
                   
    Retorna:
      numpy.array de tamaño (n_transiciones,), donde cada elemento es 1 si la transición está habilitada,
      o 0 en caso contrario.
      
    Nota:
      Para cada transición, si en una plaza el marcado es -1 se considera que cumple el requisito.
      Además, en el marcado final (en caso de que se actualice) las plazas con -1 se mantienen con -1.
    """
    # Para cada plaza y transición se verifica:
    #    si la plaza es no acotada (marcado == -1) o si tiene tokens suficientes (marcado >= matriz_neg)
    cond = np.logical_or(marcado.reshape(-1, 1) == -1, marcado.reshape(-1, 1) >= incidencia_negativa)
    
    # La transición está habilitada si se cumple la condición en TODAS las plazas.
    enabled = np.all(cond, axis=0)
    
    return enabled.astype(int)
