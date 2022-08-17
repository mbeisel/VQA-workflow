from abc import ABC, abstractmethod
from ..helperfunctions import *
import numpy as np

class costFunction(ABC):
    @abstractmethod
    def evaluate(self, bitstring, problem_instance, **kwargs):
        pass

    def computeCosts(self, counts, problem_instance):
        allCosts = np.array([self.evaluate(x, problem_instance) for x in list(counts.keys())])
        z = zip(list(counts.keys()), list(counts.values()), list(allCosts))
        z = list(z)
        return z

class MaxCutFunction(costFunction):
    def __init__(self):
        self.cached_graph = None
        self.cached_cut_size = {}
        pass

    def evaluate(self,  bitstring, problem_instance, **kwargs):
        n_vertices = problem_instance.shape[0]
        cut_string = ''.join(str(bitstring))
        if cut_string in self.cached_cut_size.keys() and hash(str(problem_instance)) == self.cached_graph:
            return self.cached_cut_size.get(cut_string)
        elif not hash(str(problem_instance)) == self.cached_graph:
            self.cached_graph = hash(str(problem_instance))
            self.cached_cut_size = {}
        C = 0
        for i in range(n_vertices):
            for j in range(i):
                C += problem_instance[i, j] * (not bitstring[i] == bitstring[j])
        self.cached_cut_size[cut_string] = C
        return C

class TspFunction(costFunction):
    def __init__(self):
        pass

    def evaluate(self,  bitstring, problem_instance, **kwargs):
        """
        Args:
        counts: dict
                key as bitstring, val as count

        AdjMatrix: Adjacency matrix as numpy array
        """
        print(bitstring, problem_instance, kwargs)
        n = len(problem_instance)
        path = self.path_from_string(bitstring, n)
        print(path)
        path_length = self.compute_path_length(path + [path[0]], problem_instance)
        return path_length

    def path_from_string(self, string, amount_nodes):
        path = [-1] * amount_nodes
        for i in range(amount_nodes):
            node_string = string[i * amount_nodes:i * amount_nodes + amount_nodes]
            node_position = node_string.find('1')
            path[node_position] = i
        return path

    def compute_path_length(self, path, problem_instance):
        print(path)

        print(list(zip(path[:-1], path[1:])))
        print(problem_instance)
        length = 0
        for i, j in zip(path[:-1], path[1:]):
            print(i,j)
            print(type(i))
            print(type(j))
            length += problem_instance[i][j]
        return length





