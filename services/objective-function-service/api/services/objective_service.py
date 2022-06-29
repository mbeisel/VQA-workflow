import numpy as np
from flask import jsonify

from api.services.objectiveFns.tsp_objective import TSPObjective

from api.services.helper_service import bad_request
from api.model.objective_response import ObjectiveResponse

def generate_tsp_objective_response(input):
    adj_matrix = input.get("adj_matrix")
    counts = input.get("counts")
    objFun = input.get("objFun")

    objective_value = TSPObjective.calc_objective(adj_matrix, counts, objFun)

    return ObjectiveResponse(
        objective_value, input
    )
