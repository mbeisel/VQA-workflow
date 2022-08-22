from abc import ABC, abstractmethod
from api.helperfunctions import takeSecond, takeFirst, figureToBase64
from api.services.costFunctions import TspFunction
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from itertools import product

class Visualization(ABC):
    @abstractmethod
    def visualize(self, counts, problem_instance, **kwargs):
        pass


class MaxCutVisualization(Visualization):
    def __init__(self):
        pass

    def visualize(self, counts, problem_instance, **kwargs):
        pass

class TspVisualization(Visualization):
    class TSPVisualization:
        def __init__(self):
            self.instance = None
            self.adj_matrix = None
            self.solutions = []

        def generate_tsp_instance(self, instance_size, area_ratio=1, scale=10):
            """
            Generate uniformly distributed random TSP instance

            Parameters:

            instance_size : Number of nodes in the TSP instance
            area_ratio : Ratio of width/length of the smalles rectangle
                that covers all nodes
            scale : Scale of the positions of all nodes
            """
            ratio = area_ratio / 2
            if np.random.randint(2) == 0:
                size_x = scale * ratio
                size_y = scale / ratio
            else:
                size_x = scale / ratio
                size_y = scale * ratio

            positions = tuple((x, y) for x, y in zip(np.random.rand(instance_size) * 2 * scale - scale,
                                                     np.random.rand(instance_size) * 2 * scale - scale))
            positions = np.array(positions)

            adj_matrix = cdist(positions, positions)

            return positions, adj_matrix

        def generate_instance(self, size, return_adj_matrix=True):
            self.instance, adj_matrix = self.generate_tsp_instance(size)
            if return_adj_matrix:
                return adj_matrix

        def set_instance(self, instance):
            self.instance = instance

        def get_instance(self):
            return self.instance

        def add_solution(self, path, color="orange", line_width=5):
            self.solutions.append((path, color, line_width))

        def draw_solution(self,
                          full_graph=False,
                          full_graph_color="black",
                          full_graph_alpha=0.3,
                          full_graph_width=2,
                          xlim=(-11, 11),
                          ylim=(-11, 11),
                          figsize=(12, 12),
                          dot_size=120):
            figure = plt.figure(figsize=figsize)
            plt.xlim(xlim)
            plt.ylim(ylim)
            plt.scatter([x for x, _ in self.instance], [y for _, y in self.instance], color="black", s=dot_size)

            if full_graph:
                for p1, p2 in product(self.instance, self.instance):
                    if not np.array_equal(p1, p2):
                        plt.plot((p1[0], p2[0]), (p1[1], p2[1]), color=full_graph_color, alpha=full_graph_alpha,
                                 linewidth=full_graph_width)

            for path, color, line_width in self.solutions:
                for p1, p2 in zip(path[:-1], path[1:]):
                    plt.plot((self.instance[p1][0], self.instance[p2][0]), (self.instance[p1][1], self.instance[p2][1]),
                             color=color, linewidth=line_width)

            plt.axis("off")
            plt.close(figure)
            return figure


    def __init__(self):
        pass

    def visualize(self, counts, problem_instance, **kwargs):
        cost_function = TspFunction()
        vis = self.TSPVisualization()
        n = len(problem_instance)
        vis.generate_instance(n)

        solution = max(counts, key=takeSecond)
        solution_string = takeFirst(solution)
        solution_path = cost_function.path_from_string(solution_string, n)
        # add last node as first to complete round trip
        solution_path = (solution_path[-1],) + tuple(solution_path)
        vis.add_solution(solution_path)

        figure = vis.draw_solution(full_graph=True)
        figure_base64 = figureToBase64(figure)
        return figure_base64





