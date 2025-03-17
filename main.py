from collections import defaultdict

import mapof.elections as mapof

import genetic_algorithm_matrix
import genetic_algorithm_votes

if __name__ == "__main__":
    experiment_id = 'mallows_triangle'
    distance_id = 'emd-positionwise'
    embedding_id = 'fr'
    anneal_count = 20

    experiment = mapof.prepare_offline_ordinal_experiment(
        experiment_id=experiment_id,
        distance_id=distance_id,
        embedding_id=embedding_id,
    )

    result = genetic_algorithm_matrix.genetic_algorithm(experiment, 20, 20, 10, [])
    print(result.score)
    result.save("xd")
