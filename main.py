from collections import defaultdict

import mapof.elections as mapof

import genetic_algorithm_matrix
import genetic_algorithm_votes
import simulated_annealing_matrix
import simulated_annealing_votes
import utils


def simulated_annealing_votes_test():
    experiment_id = '10x50'
    distance_id = 'emd-positionwise'
    embedding_id = 'fr'

    experiment = mapof.prepare_offline_ordinal_experiment(
        experiment_id=experiment_id,
        distance_id=distance_id,
        embedding_id=embedding_id,
    )

    iterations = 1000
    checkpoints = [i for i in range(iterations)]
    cooling_schedule = 'exponential'

    for neighbor_strategy in ['random', 'batch', 'mallows_random', "mallows_adaptive"]:
        for changing_votes in [1, 2, 5, 10]:
            mean = 0
            print("\n\n\n", neighbor_strategy, changing_votes)
            for i in range(5):
                s = simulated_annealing_votes.anneal(
                    experiment=experiment,
                    max_temperature=1000,
                    alpha=0.95,
                    max_iterations=250,
                    num_voters=experiment.default_num_voters,
                    checkpoints=[],
                    changing_votes=changing_votes,
                    neighbor_strategy=neighbor_strategy,
                    cooling_schedule=cooling_schedule).score
                print(s)
                mean += s
            print("mean", mean)


def simulated_annealing_matrix():
    experiment_id = '10x50'
    distance_id = 'emd-positionwise'
    embedding_id = 'fr'

    experiment = mapof.prepare_offline_ordinal_experiment(
        experiment_id=experiment_id,
        distance_id=distance_id,
        embedding_id=embedding_id
    )
    for a in ["constant", 'adaptive']:
        mean = 0
        for i in range(5):
            s = simulated_annealing_matrix.anneal(experiment, 1000, 0.95,
                                                  utils.ic_matrix(experiment.default_num_candidates,
                                                                  experiment.default_num_voters), 250, 1, [], a).score
            print(s)
            mean += s
        print(a, mean)


if __name__ == "__main__":
    simulated_annealing_votes_test()
    # simulated_annealing_matrix()
