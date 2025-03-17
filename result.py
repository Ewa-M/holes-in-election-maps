import mapof.elections as mapof
import json


class Result:
    def __init__(self, name: str, parameters: dict = None):
        self.name = name
        self.matrix = None
        self.election = None
        self.score = None
        self.partial_results = {}

        if parameters is None:
            parameters = {}
        self.parameters = parameters

    def set_result(self, score, election: mapof.OrdinalElection = None, matrix: list[list[float]] = None):
        if not election and not matrix:
            raise Exception("Anything needed")

        if election:
            self.election = election

        if matrix:
            self.matrix = matrix
        else:
            self.matrix = election.get_frequency_matrix()

        self.score = score

    def set_parameters(self, parameters: dict):
        self.parameters = parameters

    def add_partial_result(self, iteration, score: float, value, time: float = None):
        self.partial_results[iteration] = {'score': score, 'value': value}

        if time is not None:
            self.partial_results[iteration]['time'] = time

    def save(self, filename: str):
        if not filename:
            filename = self.name
        file = open(filename + ".txt", "w")
        file.write('name: {}'.format(self.name))
        for parameter in self.parameters:
            file.write('{}: {}\n'.format(parameter, self.parameters[parameter]))

        if self.partial_results:
            file.write('iteration, score, time\n')
            for iteration in self.partial_results:
                file.write('{},{},{}\n'.format(iteration, self.partial_results[iteration]['score'], self.partial_results[iteration]['time']))

        file.close()
