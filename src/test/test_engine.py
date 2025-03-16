import pytest
import numpy as np
from common.petri_net.engine import fire_transition, get_enabled_transitions




def test_fire_transition():
    marking = np.array([1, 0])
    incidence = np.array([[-1, 1], [2, -1]])
    firing_vector = np.array([1, 0])

    result = fire_transition(marking, incidence, firing_vector)
    assert np.array_equal(result, np.array([0, 2]))
        
def test_fire_transition_with_omega():
    marking = np.array([0, -1])
    incidence = np.array([[-1, 1], [2, -1]])
    firing_vector = np.array([0, 1])

    result = fire_transition(marking, incidence, firing_vector)
    assert np.array_equal(result, np.array([1, -1]))

def test_get_enabled_transitions_multiple():

    marking = np.array([1, 1])
    negative_incidence = np.array([[1, 0], [0, 1]])

    result = get_enabled_transitions(negative_incidence, marking)

    assert np.array_equal(result, np.array([1, 1]))


def test_get_enabled_transitions_single():

    marking = np.array([1, 0])
    negative_incidence = np.array([[1, 0], [0, 1]])

    result = get_enabled_transitions(negative_incidence, marking)

    assert np.array_equal(result, np.array([1, 0]))

def test_get_enabled_transitions_omega():

    marking = np.array([0, -1])
    negative_incidence = np.array([[1, 0], [0, 1]])

    result = get_enabled_transitions(negative_incidence, marking)

    assert np.array_equal(result, np.array([0, 1]))

