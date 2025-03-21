import copy
import math
import random
from collections import defaultdict
from timeit import default_timer as timer

import mapof.elections as mapof
from result import Result
import utils

def anneal(
    experiment: mapof.OrdinalElectionExperiment,
    max_temperature: int,
    alpha: float,
    max_iterations: int,
    neighbor_weight: float = 1,
    neighbor_strategy: str = 'constant',
    cooling_schedule: str = 'linear',
    result_id: str = ''
) -> Result:
    parameters = {
        'experiment': experiment.experiment_id,
        'method_name': 'simulated_annealing_matrix',
        'max_temperature': str(max_temperature),
        'alpha': str(alpha),
        'neighbor_weight': str(neighbor_weight),
        'neighbour_strategy': neighbor_strategy,
        'cooling_schedule': cooling_schedule
    }

    neighbor_weight_function = get_neighbor_weight_function(neighbor_strategy, neighbor_weight)
    cooling_schedule_function = get_cooling_schedule_function(cooling_schedule, max_temperature, alpha)
    result = Result(result_id, parameters)

    dataset = [election.get_frequency_matrix() for election in experiment.elections.values()]
    start = timer()
    matrix = utils.ic_matrix(experiment.default_num_candidates, experiment.default_num_voters)
    temperature = max_temperature
    distance = utils.score_matrix(matrix, dataset)

    for i in range(max_iterations):
        result.add_partial_result(i, distance, matrix, timer() - start)

        m_new = neighbor(matrix, neighbor_weight_function(temperature, max_temperature))
        d_new = utils.score_matrix(matrix, dataset)
        delta = d_new - distance

        if delta > 0 or math.exp(delta / temperature) >= random.random():
            matrix = m_new
            distance = d_new

        temperature = cooling_schedule_function(i)

    result.add_partial_result(max_iterations, distance, matrix)
    result.set_result(matrix=matrix, score=distance)

    return result


def get_cooling_schedule_function(cooling_schedule, max_temperature, alpha):
    if cooling_schedule == 'linear':
        return lambda iteration: max_temperature - alpha * iteration
    elif cooling_schedule == 'exponential':
        return lambda iteration: max_temperature * (alpha ** iteration)
    elif cooling_schedule == 'logarithmic':
        return lambda iteration: max_temperature / math.log(iteration + 1)
    else:
        raise ValueError('Invalid cooling schedule')


def get_neighbor_weight_function(neighbor_strategy, weight):
    if neighbor_strategy == 'adaptive':
        return lambda temperature, max_temperature: temperature / max_temperature
    elif neighbor_strategy == 'constant' and weight:
        return lambda temperature, max_temperature: weight
    else:
        raise ValueError('Invalid neighbor strategy')


def neighbor(matrix, neighbour_weight):
    result = copy.deepcopy(matrix)
    permutation = utils.ic_matrix(len(matrix), 1)
    return utils.combine_matrices(result, permutation, 1, neighbour_weight)
