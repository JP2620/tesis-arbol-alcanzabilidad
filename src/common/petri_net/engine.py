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

def fire_transition(marcado, incidence, vector_disparo):
    nuevo_marcado = marcado + np.dot(incidence, vector_disparo)
    # Restauramos las plazas no acotadas: donde el marcado original es -1 se mantiene -1.
    nuevo_marcado[marcado == -1] = -1
    return nuevo_marcado

def update_marking(marcado, marcados_conocidos):
    """
    Actualiza el 'marcado' nuevo basándose en un conjunto de 'marcados_conocidos'.
    
    Para cada marcado conocido, si en todas las plazas se cumple que:
        nuevo_marcado[j] >= marcado_conocido[j]    (tratando -1 como infinito)
    y existe al menos una plaza en la que nuevo_marcado[j] > marcado_conocido[j],
    se asigna -1 a aquellas plazas donde se da la desigualdad estricta.
    
    Parámetros:
      marcado: numpy array (1D) con el marcado nuevo.
      marcados_conocidos: numpy array (2D) con los marcados ya conocidos.
      
    Retorna:
      numpy array actualizado, donde en cada plaza se asigna -1 si se determina que es no acotada.
    """
    # Convertir -1 a infinito para realizar las comparaciones correctamente
    marcado_inf = np.where(marcado == -1, np.inf, marcado)            # Shape: (n_plazas,)
    conocidos_inf = np.where(marcados_conocidos == -1, np.inf, marcados_conocidos)  # Shape: (n_marcados, n_plazas)
    
    # Para cada marcado conocido, se verifica si en todas las plazas se cumple que:
    #   marcado_inf[j] >= conocidos_inf[i, j]
    cumple_condicion = np.all(marcado_inf[None, :] >= conocidos_inf, axis=1)  # Shape: (n_marcados,)
    
    # Inicializamos una máscara booleana para las plazas a actualizar
    update_mask = np.zeros(marcado.shape, dtype=bool)
    
    # Para cada marcado conocido que cumpla la condición, marcamos las plazas en las que:
    #   marcado_inf[j] > conocidos_inf[i, j]
    for i in range(conocidos_inf.shape[0]):
        if cumple_condicion[i]:
            update_mask |= (marcado_inf > conocidos_inf[i])
    
    # En las plazas donde la máscara es True, se asigna -1; el resto se mantiene igual.
    nuevo_marcado = np.where(update_mask, -1, marcado)
    return nuevo_marcado










