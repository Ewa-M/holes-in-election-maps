import copy
import random
import math

import prefsampling.ordinal

import utils

import mapof.elections as mapof
from timeit import default_timer as timer
from result import Result


def anneal(experiment: mapof.OrdinalElectionExperiment,
           max_temperature: float,
           alpha: float,
           max_iterations: int,
           num_voters: int = 20,
           checkpoints: list[int] = [],
           changing_votes: int = 1,
           neighbor_strategy: str = 'random',
           cooling_schedule='linear'):
    neighbor_function = get_neighbor_function(neighbor_strategy)
    cooling_schedule_function = get_cooling_schedule_function(cooling_schedule)

    parameters = {
        'max_temperature': max_temperature,
        'alpha': alpha,
        'num_voters': num_voters,
        'changing_votes': changing_votes,
        'iterations': max_iterations,
        'neighbor_strategy': neighbor_strategy,
        'cooling_schedule': cooling_schedule
    }

    result = Result("simulated_annealing_votes", parameters)
    start = timer()
    temperature = max_temperature
    election = mapof.generate_ordinal_election(
        culture_id='impartial',
        num_voters=num_voters,
        num_candidates=experiment.default_num_candidates)
    distance = utils.score_election(election, experiment)

    for i in range(max_iterations):
        new_election = neighbor_function(election, changing_votes, temperature / max_temperature)
        d_new = utils.score_election(new_election, experiment)
        delta = d_new - distance

        if delta > 0 or math.exp(delta / temperature) >= random.random():
            election = new_election
            distance = d_new

        temperature = cooling_schedule_function(temperature, alpha)

        if i in checkpoints:
            result.add_partial_result(i, distance, election, timer() - start)

    result.add_partial_result(max_iterations, distance, election)
    result.set_result(election=election, score=distance)

    return result


def get_cooling_schedule_function(cooling_schedule):
    if cooling_schedule == 'linear':
        return lambda temperature, alpha: temperature - alpha
    elif cooling_schedule == 'exponential':
        return lambda temperature, alpha: temperature * alpha
    else:
        raise ValueError('Invalid cooling schedule')


def get_neighbor_function(neighbor_strategy):
    if neighbor_strategy == 'random':
        return neighbor_random
    elif neighbor_strategy == 'batch':
        return neighbor_batch
    elif neighbor_strategy == 'mallows_random':
        return neighbor_mallows_random
    elif neighbor_strategy == 'mallows_adaptive':
        return neighbor_mallows_adaptive
    else:
        raise ValueError('Invalid neighbor strategy')


def neighbor_random(election, change_votes, placeholder):
    new_votes = copy.deepcopy(election.votes)

    for i in random.sample(range(election.num_voters), change_votes):
        new_votes[i] = utils.random_vote(election.num_candidates)
    return mapof.generate_ordinal_election_from_votes(new_votes)


def neighbor_batch(election, change_votes, placeholder):
    new_votes = copy.deepcopy(election.votes)
    vote = utils.random_vote(election.num_candidates)

    for i in random.sample(range(election.num_voters), change_votes):
        new_votes[i] = vote
    return mapof.generate_ordinal_election_from_votes(new_votes)


def neighbor_mallows_random(election, change_votes, placeholder):
    new_votes = copy.deepcopy(election.votes)

    for i in random.sample(range(election.num_voters), change_votes):
        new_votes[i] = prefsampling.ordinal.mallows(num_voters=election.num_voters,
                                                    num_candidates=election.num_candidates,
                                                    phi=random.random(),
                                                    central_vote=election.votes[i])[0]
    return mapof.generate_ordinal_election_from_votes(new_votes)


def neighbor_mallows_adaptive(election, change_votes, phi):
    new_votes = copy.deepcopy(election.votes)

    for i in random.sample(range(election.num_voters), change_votes):
        new_votes[i] = prefsampling.ordinal.mallows(num_voters=election.num_voters,
                                                    num_candidates=election.num_candidates,
                                                    phi=phi,
                                                   central_vote=election.votes[i])[0]
    return mapof.generate_ordinal_election_from_votes(new_votes)


def cooling_schedule_linear(temperature, alpha):
    return temperature - alpha


def cooling_schedule_exponential(temperature, alpha):
    return temperature * alpha
