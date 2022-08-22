from api.services.objectiveFns.tsp_objective import TSPObjective
from api.model.objective_response import ObjectiveResponse
from api.services.objectiveFunctions import F_CVaR, F_EE, F_Gibbs
from api.services.visualization import TspVisualization, MaxCutVisualization

def generate_tsp_objective_response(input):
    adj_matrix = input.get("adj_matrix")
    counts = input.get("counts")
    objFun = input.get("objFun")
    do_visualization = input.get("visualization")

    objective_function = getObjectiveFunction(objFun, "tsp")
    objective_value = objective_function.evaluate(counts, adj_matrix)

    if do_visualization:
        visualization = TspVisualization().visualize(counts=objective_function.counts_cost, problem_instance=adj_matrix)
        print(visualization)
    else:
        visualization = None

    #legacy function
    #objective_value = TSPObjective.calc_objective(adj_matrix, counts, objFun)
    print("value", objective_value)
    return ObjectiveResponse(
        objective_value, visualization, input
    )

def getObjectiveFunction(objFun, costFun, **kwargs):
    if objFun.lower() == 'expectation':
        return F_EE(costFun)
    elif objFun.lower() == 'gibbs':
        return F_Gibbs(costFun, eta=kwargs['eta'])
    elif objFun.lower() == 'cvar':
        return F_CVaR(costFun, alpha=kwargs['alpha'])

