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

    family_id = "genetic_algorithm"
    experiment.add_empty_family(family_id=family_id, marker='x')
    generations = [1, 50, 100, 150, 200, 250]
    for population_size in [10, 20, 50]:
        for num_voters in [20, 50, 100]:
            time_sum = defaultdict(int)
            score_sum = defaultdict(int)
