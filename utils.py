import math
import random
from mapof.core.distances.inner_distances import emd
from mapof.elections.distances.main_ordinal_distances import positionwise_distance
import mapof.core.distances.inner_distances as inner_distances
import mapof.core.matchings as matchings

distance_id = 'emd-positionwise'


def random_vote(num_candidates: int) -> list[int]:
    return random.sample(range(num_candidates), num_candidates)


def ic_matrix(num_candidates: int, num_voters: int) -> list[list[int]]:
    matrix = [[0 for _ in range(num_candidates)] for _ in range(num_candidates)]

    permutation = [i for i in range(num_candidates)]
    random.shuffle(permutation)

    for _ in range(num_voters):
        random.shuffle(permutation)
        for i, j in enumerate(permutation):
            matrix[i][j] += 1

    return __normalize_matrix(matrix)


def __normalize_matrix(matrix: list[list]) -> list[list]:
    denominator = sum(matrix[0])

    size = len(matrix)
    for i in range(size):
        for j in range(size):
            matrix[i][j] /= denominator

    return matrix

def get_cooling_schedule_function(cooling_schedule, max_temperature, alpha):
    if cooling_schedule in ['linear', 'lin']:
        return lambda iteration: max_temperature - alpha * iteration
    elif cooling_schedule in ['exponential', 'exp']:
        return lambda iteration: max_temperature * (alpha ** iteration)
    elif cooling_schedule in ['logarithmic', 'log']:
        return lambda iteration: max_temperature / math.log(iteration + 1)
    else:
        raise ValueError('Invalid cooling schedule')


def score_election(election, experiment):
    return min(positionwise_distance(election, e2, emd)[0] for e2 in experiment.elections.values())


def distance_between_matrices(matrix1, matrix2) -> float:
    size = len(matrix1)
    cost_table = [[inner_distances.emd(matrix1[i], matrix2[j]) for i in range(size)] for j in range(size)]
    return matchings.solve_matching_vectors(cost_table)[0]


def score_matrix(matrix, dataset):
    return min(distance_between_matrices(matrix, m) for m in dataset)


def combine_matrices(matrix1, matrix2, weight1=1, weight2=1):
    new_matrix = []
    for row1, row2 in zip(matrix1, matrix2):
        new_matrix.append([])
        for val1, val2 in zip(row1, row2):
            new_matrix[-1].append((val1*weight1 + val2*weight2)/(weight1+weight2))

    return new_matrix
