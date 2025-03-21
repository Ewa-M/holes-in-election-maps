import uuid

import mapof.elections as mapof
import json
import genetic_algorithm_votes
import simulated_annealing_votes
import simulated_annealing_matrix
import genetic_algorithm_matrix
import os


def run(**kwargs):
    algorithm_name = kwargs['algorithm']
    experiment = get_10x50_experiment()

    if algorithm_name in ['simulated_annealing_votes', 'sav']:
        algorithm = lambda: simulated_annealing_votes.anneal(
            experiment=experiment,
            max_temperature=kwargs.get('max_temperature'),
            alpha=kwargs.get('alpha'),
            max_iterations=kwargs.get('max_iterations'),
            num_voters=kwargs.get('num_voters'),
            changing_votes=kwargs.get('changing_votes'),
            neighbor_strategy=kwargs.get('neighbor_strategy'),
            cooling_schedule=kwargs.get('cooling_schedule')
        )
    elif algorithm_name in ['simulated_annealing_matrix', 'sam']:
        algorithm = lambda: simulated_annealing_matrix.anneal(
            experiment=experiment,
            max_temperature=kwargs.get('max_temperature'),
            alpha=kwargs.get('alpha'),
            max_iterations=kwargs.get('max_iterations'),
            neighbor_weight=kwargs.get('neighbor_weight', 1),
            neighbor_strategy=kwargs.get('neighbor_strategy'),
            cooling_schedule=kwargs.get('cooling_schedule')
        )
    elif algorithm_name in ['genetic_algorithm_votes', 'genv']:
        algorithm = lambda: genetic_algorithm_votes.genetic_algorithm(
            experiment=experiment,
            population_size=kwargs.get('population_size'),
            max_generations=kwargs.get('max_generations'),
            num_voters=kwargs.get('num_voters', None)
        )
    elif algorithm_name in ['genetic_algorithm_matrix', 'genm']:
        algorithm = lambda: genetic_algorithm_matrix.genetic_algorithm(
            experiment=experiment,
            population_size=kwargs.get('population_size'),
            max_generations=kwargs.get('max_generations'),
            num_voters=kwargs.get('num_voters', 20)
        )
    else:
        raise ValueError("""Algorithm type not supported. Try:
                         simulated_annealing_votes sav
                         simulated_annealing_matrix sam
                         genetic_algorithm_votes genv
                         genetic_algorithm_matrix genm""")

    name = kwargs['name']
    repetitions = kwargs['reps']
    path = './results/' + name
    computed_count = 0

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        save_parameters(kwargs, path)
    else:
        computed_count = sum(1 for i in os.listdir(path) if i[:7] == 'scores_')

    for _ in range(repetitions - computed_count):
        result = algorithm()
        result.save_partial(path + "/scores_" + str(uuid.uuid4()) + '.csv')


def save_parameters(parameters, path):
    with open(path + '/parameters.json', 'w') as json_file:
        json.dump(parameters, json_file, indent=4)


def get_10x50_experiment():
    experiment_id = '10x50'
    distance_id = 'emd-positionwise'
    embedding_id = 'fr'

    return mapof.prepare_offline_ordinal_experiment(
        experiment_id=experiment_id,
        distance_id=distance_id,
        embedding_id=embedding_id
    )


if __name__ == '__main__':
    run(
        name='xd',
        algorithm='genm',
        reps=5,
        population_size=4,
        num_voters=5,
        max_generations=3
    )
