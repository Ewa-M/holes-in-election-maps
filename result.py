
class Result:
    def __init__(self, parameters=None, matrix_only=False):
        self.matrix = None
        self.election = None
        self.score = None
        self.partial_results = {}
        self.matrix_only = matrix_only

        if parameters is None:
            parameters = {}
        self.parameters = parameters

    def set_result(self, score, election=None, matrix=None):
        if not election and not self.matrix_only:
            raise Exception("Election needed")

        if election:
            self.election = election

        if matrix:
            self.matrix = matrix
        else:
            self.matrix = election.get_frequency_matrix()

        self.score = score



    def set_parameters(self, parameters):
        self.parameters = parameters

    def add_partial_result(self, iteration, score, value, time=None):
        self.partial_results[iteration] = {'score': score, 'value': value}

        if time is not None:
            self.partial_results[iteration]['time'] = time
