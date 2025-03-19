import mapof.elections as mapof
import json
from pathlib import Path
import statistics
import os

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


def experiment(function, name, repetitions):
    if not os.path.exists("./results/{}".format(name)):
        os.makedirs("./results/{}".format(name))

    path = "./results/{}/".format(name)
    result = function()

    parameters_file = open(path + "parameters.txt", "w")
    parameters_file.write(result.name + "\n")
    parameters_file.write(",".join([str(i) for i in result.parameters.keys()]) + "\n")
    parameters_file.write(",".join([str(i) for i in result.parameters.values()]) + "\n")
    parameters_file.close()

    file = open(path + "0.csv", "w")
    file.write('iteration, score\n')

    partial_results = {}

    for iteration in result.partial_results:
        file.write(str(iteration) + ",")
        file.write(str(result.partial_results[iteration]['score']) + '\n')
        partial_results[iteration] = [result.partial_results[iteration]['score']]
    file.close()

    for i in range(1, repetitions):
        result = function()
        file = open(path + str(i) + ".txt", "w")
        file.write('iteration, score\n')

        for iteration in result.partial_results:
            file.write(str(iteration) + ",")
            file.write(str(result.partial_results[iteration]['score']) + '\n')
            partial_results[iteration].append(result.partial_results[iteration]['score'])
        file.close()

    file = open(path + "summary.txt", "w")
    file.write('iteration,min,min_index,max,max_index,mean, \n')

    for iteration in partial_results:
        file.write(str(iteration) + ",")
        values = partial_results[iteration]
        min_v = min(values)
        file.write(str(min_v) + ',')
        file.write(str(values.index(min_v)) + ',')
        max_v = max(values)
        file.write(str(max_v) + ',')
        file.write(str(values.index(max_v)) + ',')
        file.write(str(statistics.stdev(values)) + '\n')
    file.close()




