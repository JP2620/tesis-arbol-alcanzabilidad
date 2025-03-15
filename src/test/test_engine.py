import pytest
import numpy as np
from common.petri_net.engine import fire_transition




def test_fire_transition():
    marking = np.array([1, 0])
    incidence = np.array([[-1, 1], [2, -1]])
    firing_vector = np.array([1, 0])

    result = fire_transition(marking, incidence, firing_vector)
    assert np.array_equal(result, np.array([0, 2]))
        


