import mapof.elections as mapof
import random
from timeit import default_timer as timer
import utils
from result import Result


def genetic_algorithm(experiment: mapof.OrdinalElectionExperiment,
                      population_size: int,
                      max_generations: int,
                      num_voters=None,
                      ) -> Result:

    if num_voters is None:
        num_voters = experiment.default_num_voters

    parameters = {
        'experiment': experiment.experiment_id,
        'method_name': 'genetic_algorithm_votes',
        'population_size': str(population_size),
        'num_voters': str(num_voters),
        'generations': str(max_generations)
    }

    result = Result("genetic_algorithm_votes", parameters)

    start = timer()
    initial_elections = [mapof.generate_ordinal_election(
        culture_id='impartial',
        num_voters=num_voters,
        num_candidates=experiment.default_num_candidates) for _ in range(population_size)]

    population = [{'election': election, 'score': utils.score_election(election, experiment)} for election in
                  initial_elections]
    half = population_size // 2
    for i in range(max_generations):
        result.add_partial_result(i, best['score'], best['election'], timer() - start)

        population.sort(key=lambda e: e['score'], reverse=True)
        population = population[:half]

        for a, b in zip(random.sample(range(half), half), random.sample(range(half), half)):
            offspring = combine(population[a]['election'], population[b]['election'])
            population.append({'election': offspring, 'score': utils.score_election(offspring, experiment)})

        best = max(population, key=lambda e: e['score'])

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

