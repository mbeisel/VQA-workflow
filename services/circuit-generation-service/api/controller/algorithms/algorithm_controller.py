from flask_smorest import Blueprint
from flask import request
from api.services import algorithm_service
from ...model.circuit_response import CircuitResponseSchema
from ...model.algorithm_request import (
    HHLAlgorithmRequestSchema,
    HHLAlgorithmRequest,
    QAOAAlgorithmRequestSchema,
    QAOAAlgorithmRequest,
    TSPQAOAAlgorithmRequest,
    TSPQAOAAlgorithmRequestSchema,
)


blp = Blueprint(
    "algorithms",
    __name__,
    url_prefix="/algorithms",
    description="get quantum circuit algorithms",
)


@blp.route("/hhl", methods=["POST"])
@blp.arguments(
    HHLAlgorithmRequestSchema,
    example=dict(matrix=[[1.5, 0.5], [0.5, 1.5]], vector=[0, 1]),
)
@blp.response(200, CircuitResponseSchema)
def encoding(json: HHLAlgorithmRequest):
    if json:
        return algorithm_service.generate_hhl_algorithm(json)


@blp.route("/qaoa", methods=["POST"])
@blp.etag
@blp.arguments(
    QAOAAlgorithmRequestSchema,
    example=dict(
        adj_matrix=[[0, 1, 1, 0], [1, 0, 1, 1], [1, 1, 0, 1], [0, 1, 1, 0]],
        beta=1.0,
        gamma=1.0,
    ),
)
@blp.response(200, CircuitResponseSchema)
def encoding(json: QAOAAlgorithmRequest):
    if json:
        return algorithm_service.generate_qaoa_circuit(json)


@blp.route("/tspqaoa", methods=["POST"])
@blp.etag
@blp.arguments(
    TSPQAOAAlgorithmRequestSchema,
    example=dict(
        adj_matrix=[[0, 1, 1, 0], [1, 0, 1, 1], [1, 1, 0, 1], [0, 1, 1, 0]],
        p=2,
        betas=[1.0, 2.0],
        gammas=[1.0, 3.0],
    ),
)
@blp.response(200, CircuitResponseSchema)
def encoding(json: TSPQAOAAlgorithmRequest):
    if json:
        return algorithm_service.generate_tsp_qaoa_circuit(json)
