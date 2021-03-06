import random


def generate_random_matrix(n, m, max_value=1000):
    """
    Generates a random matrix

    :param n: first dimension
    :param m: second dimension
    :param max_value the maximum value of an element

    """
    return [[random.random()*max_value for x in range(m)] for e in range(n)]
