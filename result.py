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
        self.partial_results[iteration]['time'] = time

    def save(self, filename: str):
        if not filename:
            filename = self.name
        file = open("results\\" + filename + ".txt", "w")
        file.write(self.name + "\n")

        names = ""
        values = ""
        for parameter in self.parameters:
            names += parameter
            names += ","
            values += str(self.parameters[parameter])
            values += ","

        names = names[:-1] + '\n'
        values = values[:-1] + '\n'
        file.write(names)
        file.write(values)

        if self.partial_results:
            file.write('iteration, score, time\n')
            for iteration in self.partial_results:
                file.write(str(iteration) + ",")
                file.write(str(self.partial_results[iteration]['score']) + ',')
                file.write(str(self.partial_results[iteration]['time']) + '\n')

        file.close()
