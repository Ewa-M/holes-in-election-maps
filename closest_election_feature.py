
def add_closest_election_feature(experiment, culture_id=None, distance_id='emd-positionwise'):
    experiment.add_feature("closest_election", lambda election: __closest_election(experiment, election, culture_id, distance_id))
    experiment.compute_feature(feature_id='closest_election')


def __closest_election(experiment, election, culture_id, distance_id):
    if not experiment.distances:
        experiment.compute_distances(distance_id=distance_id)

    if not culture_id or election.culture_id == culture_id:
        return min(experiment.distances[election.election_id].values())
    else:
        return None
