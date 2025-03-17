import copy
import random
import math
from collections import defaultdict
import utils

import mapof.elections as mapof
from timeit import default_timer as timer
from result import Result


def anneal(experiment, T_max, alpha, max_iterations, num_voters=20, checkpoints=[], changing_votes=1):
    parameters = {
        'max_temperature': T_max,
        'alpha': alpha,
        'num_voters': num_voters,
        'changing_votes': changing_votes,
        'iterations': max_iterations
    }
    result = Result(parameters=parameters,
                    matrix_only=False)

    start = timer()
    temp = T_max
    election = mapof.generate_ordinal_election(
        culture_id='impartial',
        num_voters=num_voters,
        num_candidates=experiment.default_num_candidates)
    distance = utils.score_election(election, experiment)

    for i in range(max_iterations):
        new_election = neighbour_random_votes(election, changing_votes)
        d_new = utils.score_election(new_election, experiment)
        delta = d_new - distance

        if delta > 0 or math.exp(delta / temp) >= random.random():
            election = new_election
            distance = d_new

        temp = temp / alpha

        if i in checkpoints:
            result.add_partial_result(i, distance, election, timer() - start)

    result.add_partial_result(max_iterations, distance, election)
    result.set_result(election=election, score=distance)

    return results


def neighbour_random_votes(election, change_votes):
    new_votes = copy.deepcopy(election.votes)

    for i in random.sample(range(election.num_voters), change_votes):
        new_votes[i] = utils.random_vote(election.num_candidates)
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

    family_id = "simulated_annealing"
    experiment.add_empty_family(family_id=family_id, marker='x')
    checkpoints = [1, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
    for num_voters, changing_votes in [(20, 1), (100, 1), (100, 5), (20, 2), (100, 10)]:
        time_sum = defaultdict(int)
        score_sum = defaultdict(int)
        for i in range(4):
            results = anneal(experiment, 1000, 1.05, 500, num_voters, checkpoints, changing_votes)
            for iteration in results:
                time_sum[iteration] += results[iteration]['time']
                score_sum[iteration] += results[iteration]['score']
        for checkpoint in checkpoints:
            print("{} & {} & {} & {} & {}".format(num_voters, changing_votes, checkpoint, score_sum[checkpoint] / 4,
                                                  time_sum[checkpoint] / 4))
