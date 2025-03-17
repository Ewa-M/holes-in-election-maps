import copy
import math
import random
from collections import defaultdict
from timeit import default_timer as timer

import mapof.elections as mapof
from result import Result
import utils

def anneal(experiment, T_max, alpha, initial_matrix, iterations, neighbour_distance=1, checkpoints=[]):
    parameters = {
        'max_temperature': T_max,
        'alpha': alpha,
        'iterations': iterations,
        'initial_matrix': initial_matrix
    }
    result = Result(parameters=parameters,
                    matrix_only=True)

    dataset = [election.get_frequency_matrix() for election in experiment.elections.values()]
    start = timer()
    matrix = copy.deepcopy(initial_matrix)
    temp = T_max
    distance = utils.score_matrix(matrix, dataset)

    for i in range(iterations):
        m_new = neighbour(matrix, neighbour_distance)
        d_new = utils.score_matrix(matrix, dataset)
        delta = d_new - distance

        if delta > 0 or math.exp(delta / temp) >= random.random():
            matrix = m_new
            distance = d_new

        temp = temp / alpha

        if i in checkpoints:
            result.add_partial_result(i, distance, matrix, timer() - start)

    result.add_partial_result(iterations, distance, matrix)
    result.set_result(matrix=matrix, score=distance)

    return result


def neighbour(matrix, neighbour_distance):
    result = copy.deepcopy(matrix)
    permutation = utils.ic_matrix(len(matrix), 1)

    return utils.combine_matrices(result, permutation, 1, neighbour_distance)


if __name__ == "__main__":
    experiment_id = 'mallows_triangle_clean'
    distance_id = 'emd-positionwise'
    embedding_id = 'fr'
    anneal_count = 20

    experiment = mapof.prepare_offline_ordinal_experiment(
        experiment_id=experiment_id,
        distance_id=distance_id,
        embedding_id=embedding_id,
    )

    checkpoints = [1, 50, 100, 150, 200, 250]
    for max_temperature in [1000, 2000, 3000]:
        for alpha in [1.05, 1.025, 1.075]:
            for num_voters in [20, 50, 100]:
                time_sum = defaultdict(int)
                score_sum = defaultdict(int)
                for i in range(4):
                    initial_matrix = mapof.generate_ordinal_election(
                        culture_id='impartial',
                        num_voters=num_voters,
                        num_candidates=experiment.default_num_candidates
                    ).get_frequency_matrix()
                    results = anneal(experiment, max_temperature, alpha, initial_matrix, 250, 1, checkpoints)
                    for iteration in results:
                        time_sum[iteration] += results[iteration]['time']
                        score_sum[iteration] += results[iteration]['score']
                for checkpoint in checkpoints:
                    print("{} & {} & {} & {} & {} & {}".format(max_temperature, alpha, num_voters, checkpoint,
                                                               score_sum[checkpoint] / 4, time_sum[checkpoint] / 4))
