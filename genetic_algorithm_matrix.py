from collections import defaultdict

import mapof.elections as mapof
import random
from timeit import default_timer as timer
import utils
from result import Result

def genetic_algorithm(experiment, population_size, max_generations, num_voters=20, check_generations=[]):
    parameters = {
        'population_size': population_size,
        'num_voters': num_voters,
        'generations': max_generations
        }

    result = Result("genetic_algorithm_matrix",parameters)

    start = timer()
    initial_matrices = [utils.ic_matrix(experiment.default_num_candidates, experiment.default_num_candidates) for _ in range(population_size)]
    dataset = [election.get_frequency_matrix() for election in experiment.elections.values()]

    population = [{'matrix': matrix, 'score': utils.score_matrix(matrix, dataset)} for matrix in initial_matrices]
    half = population_size // 2

    for i in range(max_generations):
        population.sort(key=lambda e: e['score'], reverse=True)
        population = population[:half]

        for a, b in zip(random.sample(range(half), half), random.sample(range(half), half)):
            offspring = generate_offspring(population[a]['matrix'], population[b]['matrix'])
            population.append({'matrix': offspring, 'score': utils.score_matrix(offspring, dataset)})

        best = max(population, key=lambda e: e['score'])

        if i in check_generations:
            result.add_partial_result(i, best['score'], best['matrix'], timer() - start)

    best = max(population, key=lambda e: e['score'])
    result.set_result(score=best['score'], matrix=best['matrix'])

    return result

def generate_offspring(m1, m2):
    combined = utils.combine_matrices(m1, m2)

    if random.random() < 0.9:
        return combined
    else:
        return utils.combine_matrices(combined, utils.ic_matrix(len(m1), 1), 1, 0.5)
