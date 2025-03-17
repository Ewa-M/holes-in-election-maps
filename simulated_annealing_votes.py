import copy
import random
import math

import prefsampling.ordinal

import utils

import mapof.elections as mapof
from timeit import default_timer as timer
from result import Result



def anneal(experiment, T_max, alpha, max_iterations, num_voters=20, checkpoints=[], changing_votes=1, neigbor_type=None):
    parameters = {
        'max_temperature': T_max,
        'alpha': alpha,
        'num_voters': num_voters,
        'changing_votes': changing_votes,
        'iterations': max_iterations
    }
    result = Result("simulated_annealing_votes", parameters)

    neighbor_function = neighbor_random_votes
    if neigbor_type == 'batch':
        neighbor_function = neighbor_batch_votes
    elif neigbor_type == 'mallows':
        neighbor_function = neighbor_mallows_votes

    start = timer()
    temp = T_max
    election = mapof.generate_ordinal_election(
        culture_id='impartial',
        num_voters=num_voters,
        num_candidates=experiment.default_num_candidates)
    distance = utils.score_election(election, experiment)

    for i in range(max_iterations):
        new_election = neighbor_function(election, changing_votes)
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

    return result


def neighbor_random_votes(election, change_votes):
    new_votes = copy.deepcopy(election.votes)

    for i in random.sample(range(election.num_voters), change_votes):
        new_votes[i] = utils.random_vote(election.num_candidates)
    return mapof.generate_ordinal_election_from_votes(new_votes)


def neighbor_mallows_votes(election, change_votes):
    new_votes = copy.deepcopy(election.votes)

    for i in random.sample(range(election.num_voters), change_votes):
        new_votes[i] = prefsampling.ordinal.mallows(election.num_voters,
                                                    election.num_candidates,
                                                    random.random(),
                                                    election.votes[i])[0]
    return mapof.generate_ordinal_election_from_votes(new_votes)


def neighbor_batch_votes(election, change_votes):
    new_votes = copy.deepcopy(election.votes)
    vote = utils.random_vote(election.num_candidates)

    for i in random.sample(range(election.num_voters), change_votes):
        new_votes[i] = vote
    return mapof.generate_ordinal_election_from_votes(new_votes)
