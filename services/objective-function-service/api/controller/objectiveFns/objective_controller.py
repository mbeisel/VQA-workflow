from flask_smorest import Blueprint
from flask import request
from api.services import objective_service
from ...model.objective_response import ObjectiveResponseSchema
from ...model.objective_request import (
    TSPObjectiveFunctionRequest,
    TSPObjectiveFunctionRequestSchema,
)


blp = Blueprint(
    "objective",
    __name__,
    url_prefix="/objective",
    description="compute objective value from counts",
)


@blp.route("/tsp", methods=["POST"])
@blp.arguments(
    TSPObjectiveFunctionRequestSchema,
    example=dict(adj_matrix=[[0, 1, 1, 0], [1, 0, 1, 1], [1, 1, 0, 1], [0, 1, 1, 0]],
                 counts={"1"*16:100,"0"*16:100},
                 objFun = "Expectation"),
)
@blp.response(200, ObjectiveResponseSchema)
def encoding(json: TSPObjectiveFunctionRequest):
    print(json)
    if json:
        return objective_service.generate_tsp_objective_response(json)


