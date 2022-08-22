from flask_smorest import Blueprint
from flask import request
from api.services import objective_service
from ...model.objective_response import ObjectiveResponseSchema
from ...model.objective_request import (
    TSPObjectiveFunctionRequest,
    TSPObjectiveFunctionRequestSchema,
    MaxCutObjectiveFunctionRequest,
    MaxCutObjectiveFunctionRequestSchema,
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
                 objFun="Expectation",
                 visualization=True
                 )
)
@blp.response(200, ObjectiveResponseSchema)
def tsp(json: TSPObjectiveFunctionRequest):
    print(json)
    if json:
        return objective_service.generate_tsp_objective_response(json)


@blp.route("/max-cut", methods=["POST"])
@blp.arguments(
    MaxCutObjectiveFunctionRequestSchema,
    example=dict(adj_matrix=[[0, 1, 1, 0], [1, 0, 1, 1], [1, 1, 0, 1], [0, 1, 1, 0]],
                 counts={"1"*16:100,"0"*16:100},
                 objFun="Expectation",
                 visualization=True
                 ),
)
@blp.response(200, ObjectiveResponseSchema)
def max_cut(json: MaxCutObjectiveFunctionRequest):
    print(json)
    if json:
        return objective_service.generate_max_cut_objective_response(json)


