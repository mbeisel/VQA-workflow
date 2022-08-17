from abc import ABC, abstractmethod
from ..helperfunctions import *
import numpy as np
from api.services.costFunctions import TspFunction, MaxCutFunction

class objectiveFunction(ABC):
    def __init__(self, cost_function):
        if cost_function.lower() == "tsp":
            self.cost_function = TspFunction()
        elif cost_function.lower() == "maxcut":
            self.cost_function = MaxCutFunction()
        pass

    @abstractmethod
    def evaluate(self, counts, problem_instance):
        pass


class F_EE(objectiveFunction):
    def __init__(self, cost_function):
        super().__init__(cost_function=cost_function)
        pass

    def evaluate(self, counts, problem_instance):
        z = self.cost_function.computeCosts(counts, problem_instance)
        print(z)
        n_samples = np.sum(list(counts.values()))
        if n_samples > 0:
            total_objective_value = (np.sum(np.array([z[i][2] * z[i][1] for i in range(len(z))])) / n_samples)
        else:
            return 0
        return total_objective_value


class F_CVaR(objectiveFunction):
    def __init__(self, cost_function, alpha):
        super().__init__(cost_function=cost_function)
        self.alpha = alpha

    def evaluate(self, counts, problem_instance):
        z = self.cost_function.computeCosts(counts, problem_instance)
        z.sort(key=takeThird, reverse=True)
        total_objective_value = 0
        alphaRemaining = np.ceil(self.alpha * np.sum(list(counts.values())))
        n_considered = alphaRemaining
        for i in range(len(z)):
            if z[i][1] < alphaRemaining:
                total_objective_value += z[i][1] * z[i][2]
                alphaRemaining -= z[i][1]
            else:
                total_objective_value += alphaRemaining * z[i][2]
                break
        if n_considered > 0:
            total_objective_value /= n_considered
        else:
            return 0
        return total_objective_value


class F_Gibbs(objectiveFunction):
    def __init__(self, cost_function, eta):
        super().__init__(cost_function=cost_function)
        self.eta = eta

    def evaluate(self, counts, problem_instance):
        z = self.cost_function.computeCosts(counts, problem_instance)
        n_samples = np.sum(list(counts.values()))
        z = np.array(z, dtype=object)
        if n_samples > 0:
            total_objective_value = np.log(np.sum((np.e ** (self.eta * z[:, 2])) * z[:, 1]) / n_samples)
        else:
            return 0
        return total_objective_value