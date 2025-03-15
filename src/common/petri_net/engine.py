import numpy as np

def fire_transition(marcado, incidence, vector_disparo):
    return marcado + np.dot(incidence, vector_disparo)
