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

    result = Result(parameters)

    start = timer()
    initial_elections = [mapof.generate_ordinal_election(
        culture_id='impartial',
        num_voters=num_voters,
        num_candidates=experiment.default_num_candidates) for _ in range(population_size)]

    population = [{'election': election, 'score': utils.score_election(election, experiment)} for election in initial_elections]
    half = population_size // 2
    for i in range(max_generations):
        population.sort(key=lambda e: e['score'], reverse=True)
        population = population[:half]

        for a, b in zip(random.sample(range(half), half), random.sample(range(half), half)):
            offspring = combine(population[a]['election'], population[b]['election'])
            population.append({'election': offspring, 'score': utils.score_election(offspring, experiment)})

        best = max(population, key=lambda e: e['score'])
        if i in check_generations:
            result.add_partial_result(i, best['score'], best['election'], timer() - start)

    best = max(population, key=lambda e: e['score'])
    result.set_result(score=best['score'], election=best['election'])

    return result


def combine(e1, e2):
    new_votes = []

    for v1, v2 in zip(e1.votes, e2.votes):
        prob = random.random()

        if prob < 0.45:
            new_votes.append(v1)
        elif prob < 0.9:
            new_votes.append(v2)
        else:
            new_votes.append(utils.random_vote(e1.num_candidates))

    return mapof.generate_ordinal_election_from_votes(new_votes)



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
