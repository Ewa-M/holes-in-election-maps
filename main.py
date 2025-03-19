
import mapof.elections as mapof

import result
import simulated_annealing_matrix
import utils

#['random', 'batch', 'mallows_random', "mallows_adaptive"]

def simulated_annealing_matrix_adaptive_linear_test():
    experiment_id = '10x50'
    distance_id = 'emd-positionwise'
    embedding_id = 'fr'

    experiment = mapof.prepare_offline_ordinal_experiment(
        experiment_id=experiment_id,
        distance_id=distance_id,
        embedding_id=embedding_id
    )

    cooling_schedule = 'linear'
    iterations = 3
    checkpoints = [i for i in range(iterations)]

    for max_temperature, alpha in [(1, 0.001), (2, 0.002), (0.5, 0.0005), (1, 0.009)]:
        function = lambda: simulated_annealing_matrix.anneal(experiment,
                                                             max_temperature,
                                                             alpha,
                                                             utils.ic_matrix(experiment.default_num_candidates,
                                                                             experiment.default_num_voters),
                                                             iterations,
                                                             1,
                                                             checkpoints,
                                                             "adaptive",
                                                             cooling_schedule)

        result.experiment(function, "_".join(["sa", str(max_temperature), str(alpha), cooling_schedule, "adaptive"]), 2)


if __name__ == "__main__":
    simulated_annealing_matrix_adaptive_linear_test()
