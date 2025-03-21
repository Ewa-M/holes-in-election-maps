import copy
import random
import math

import prefsampling.ordinal

import utils

import mapof.elections as mapof
from result import Result


def anneal(experiment: mapof.OrdinalElectionExperiment,
           max_temperature: int,
           alpha: float,
           max_iterations: int,
           num_voters: int = 20,
           changing_votes: int = 1,
           neighbor_strategy: str = 'random',
           cooling_schedule: str = 'linear',
           result_id: str = ""
           ) -> Result:
    print("kurwa")
    parameters = {
        'experiment': experiment.experiment_id,
        'method_name': 'simulated_annealing_voted',
        'max_temperature': str(max_temperature),
        'alpha': str(alpha),
        'num_voters': str(num_voters),
        'neighbour_strategy': neighbor_strategy,
        'cooling_schedule': cooling_schedule
    }

    neighbor_function = get_neighbor_function(neighbor_strategy)
    cooling_schedule_function = utils.get_cooling_schedule_function(cooling_schedule, max_temperature, alpha)
    result = Result(result_id, parameters)

    temperature = max_temperature
    election = mapof.generate_ordinal_election(
        culture_id='impartial',
        num_voters=num_voters,
        num_candidates=experiment.default_num_candidates)
    score = utils.score_election(election, experiment)

    for i in range(max_iterations):
        result.add_partial_result(i, score, election)
        new_election = neighbor_function(election, changing_votes, temperature / max_temperature)
        score_new = utils.score_election(new_election, experiment)
        delta = score_new - score

        if delta > 0 or math.exp(delta / temperature) >= random.random():
            election = new_election
            score = score_new

        temperature = cooling_schedule_function(i)

    result.add_partial_result(max_iterations, score, election)
    result.set_result(election=election, score=score)

    return result

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


def neighbor_mallows_adaptive(election, change_votes, phi):
    new_votes = copy.deepcopy(election.votes)

    for i in random.sample(range(election.num_voters), change_votes):
        new_votes[i] = prefsampling.ordinal.mallows(num_voters=election.num_voters,
                                                    num_candidates=election.num_candidates,
                                                    phi=phi,
                                                    central_vote=election.votes[i])[0]
    return mapof.generate_ordinal_election_from_votes(new_votes)
