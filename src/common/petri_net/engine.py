import numpy as np

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
    Actualiza el nuevo marcado teniendo en cuenta los marcados conocidos.
    
    Si existe al menos un marcado conocido 'k' tal que, para cada plaza 'i':
      - Si k[i] es -1, se requiere que nuevo_marcado[i] sea -1 (ω)
      - Si k[i] es un número finito, se requiere que nuevo_marcado[i] >= k[i] 
        (recordando que si nuevo_marcado[i] es -1 se interpreta como ω, que es ≥ cualquier número)
    y además existe al menos una plaza 'i' en la que nuevo_marcado[i] sea estrictamente mayor que k[i]
    (es decir, si k[i] es finito y nuevo_marcado[i] > k[i], o si nuevo_marcado[i] es -1 y k[i] es finito),
    entonces para todas esas plazas 'i' se asigna -1 (representando que son no acotadas).
    
    Parámetros:
      nuevo_marcado       : numpy.array (1D) con el nuevo marcado.
      marcados_conocidos  : numpy.array (2D) donde cada fila es un marcado conocido.
    
    Retorna:
      numpy.array: el marcado actualizado, donde se han reemplazado por -1 las plazas que son
                   estrictamente mayores que alguna de las componentes de un marcado conocido que
                   cumple la condición (en todas las plazas, el nuevo marcado es ≥ que el conocido).
    
    Ejemplo:
      nuevo_marcado = np.array([2, -1])
      marcados_conocidos = np.array([[1,0], [0,2], [1,1], [1,-1], [3,0]])
      
      Al comparar con [1,-1], se tiene que:
         plaza 0: 2 > 1  (estrictamente mayor)
         plaza 1: -1 == -1
      Por lo que se actualiza la plaza 0 a -1 y, al haber otra comparación que también lo determine,
      el resultado final es: [-1, -1].
    """
    # Hacemos una copia para no modificar el array original
    resultado = marcado.copy()
    # Aseguramos que resultado es 1D y marcados_conocidos es 2D (n_marcados x n_plazas)
    nuevo = resultado.reshape(1, -1)  # forma (1, p)
    
    # Para cada marcado conocido (cada fila), se evalúa la condición:
    # Para cada plaza i:
    #   Si el marcado conocido tiene -1, se requiere que nuevo[i] sea -1.
    #   Si el marcado conocido es finito, se requiere que:
    #         nuevo[i] == -1  (ω, cumple siempre)  o  nuevo[i] >= k[i] (si es finito).
    #
    # Esto se implementa de forma vectorizada:
    cond = (nuevo == -1) | ((marcados_conocidos != -1) & (nuevo >= marcados_conocidos))
    # Para cada marcado conocido, la condición se cumple en todas las plazas si:
    cumple_total = np.all(cond, axis=1)  # forma (n_marcados,)
    
    # Ahora, para cada conocido que cumple, definimos la comparación estricta:
    # Se dice que en la plaza i se tiene "estrictamente mayor" si:
    #   - nuevo[i] es -1 y k[i] es finito  (ω > número finito)
    #   - o ambos son finitos y nuevo[i] > k[i]
    estricto = ((nuevo == -1) & (marcados_conocidos != -1)) | \
               ((nuevo != -1) & (marcados_conocidos != -1) & (nuevo > marcados_conocidos))
    
    # Para cada marcado conocido que cumple la condición total, se toman los índices donde la comparación es estricta.
    if np.any(cumple_total):
        # Seleccionamos las filas (marcados) que cumplen
        estricto_sel = estricto[cumple_total]
        # Se toma la unión (OR) a lo largo de los marcados conocidos seleccionados
        uniones = np.any(estricto_sel, axis=0)
        # Para los índices donde se cumple la comparación estricta, actualizamos a -1.
        resultado[uniones] = -1
        
    return resultado
