import uuid
import mapof.elections as mapof
import json
import genetic_algorithm_votes
import simulated_annealing_votes
import simulated_annealing_matrix
import genetic_algorithm_matrix
import os
from argparse import ArgumentParser


def run(parameters):
    algorithm_name = parameters.algorithm
    experiment = get_10x50_experiment()
    if algorithm_name in ['simulated_annealing_votes', 'sav']:
        algorithm = lambda: simulated_annealing_votes.anneal(
            experiment=experiment,
            max_temperature=parameters.max_temperature,
            alpha=parameters.alpha,
            max_iterations=parameters.max_iterations,
            num_voters=parameters.num_voters,
            changing_votes=parameters.changing_votes,
            neighbor_strategy=parameters.neighbor_strategy,
            cooling_schedule=parameters.cooling_schedule
        )
    elif algorithm_name in ['simulated_annealing_matrix', 'sam']:
        algorithm = lambda: simulated_annealing_matrix.anneal(
            experiment=experiment,
            max_temperature=parameters.max_temperature,
            alpha=parameters.alpha,
            max_iterations=parameters.max_iterations,
            neighbor_weight=parameters.neighbor_weight,
            neighbor_strategy=parameters.neighbor_strategy,
            cooling_schedule=parameters.cooling_schedule
        )
    elif algorithm_name in ['genetic_algorithm_votes', 'genv']:
        algorithm = lambda: genetic_algorithm_votes.genetic_algorithm(
            experiment=experiment,
            population_size=parameters.population_size,
            max_generations=parameters.max_iterations,
            num_voters=parameters.num_vo)
    elif algorithm_name in ['genetic_algorithm_matrix', 'genm']:
        algorithm = lambda: genetic_algorithm_matrix.genetic_algorithm(
            experiment=experiment,
            population_size=parameters.population_size,
            max_generations=parameters.max_iterations,
            num_voters=parameters.num_voters
        )
    else:
        raise ValueError("""Algorithm type not supported. Try:
                         simulated_annealing_votes sav
                         simulated_annealing_matrix sam
                         genetic_algorithm_votes genv
                         genetic_algorithm_matrix genm""")
    name = parameters.name
    repetitions = parameters.reps
    path = './results/' + name
    print(path)

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        save_parameters(parameters, path)

    for i in range(repetitions):
        algorithm().save_partial(path + "/scores_" + str(uuid.uuid4()) + '.csv')


def save_parameters(parameters, path):
    with open(path + '/parameters.json', 'w') as json_file:
        json.dump(vars(parameters), json_file, indent=4)


def get_10x50_experiment():
    experiment_id = '10x50'
    distance_id = 'emd-positionwise'
    embedding_id = 'fr'

    return mapof.prepare_offline_ordinal_experiment(
        experiment_id=experiment_id,
        distance_id=distance_id,
        embedding_id=embedding_id
    )


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("name", type=str,
                        help=""""Name of destination folder""")
    parser.add_argument("reps", type=int,
                        help=""""Number of experiments to run""")
    parser.add_argument("algorithm", type=str,
                        help=""""Supported algorithm types:\n
                         simulated_annealing_votes sav\n
                         simulated_annealing_matrix sam\n
                         genetic_algorithm_votes genv\n
                         genetic_algorithm_matrix genm""")
    parser.add_argument("--max_temperature", "--t", type=float, default=None)
    parser.add_argument("--alpha", "--a", type=float, default=None)
    parser.add_argument("--max_iterations", "--i", type=int, default=None)
    parser.add_argument("--num_voters", "--v", type=int, default=None)
    parser.add_argument("--changing_votes", "--c", type=int, default=None)
    parser.add_argument("--neighbor_strategy", "--n", type=str, default=None)
    parser.add_argument("--cooling_schedule", "--s", type=str, default=None)
    parser.add_argument("--neighbor_weight", "--w", type=float, default=None)
    parser.add_argument("--population_size", "--p", type=int, default=None)

    return parser.parse_args()


if __name__ == '__main__':
    arg_dict = parse_arguments()
    print(arg_dict)
    run(arg_dict)
