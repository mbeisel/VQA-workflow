import marshmallow as ma
from marshmallow import pre_load, ValidationError
import numpy as np


class HHLAlgorithmRequest:
    def __init__(self, matrix, vector):
        self.matrix = matrix
        self.vector = vector


class HHLAlgorithmRequestSchema(ma.Schema):
    matrix = ma.fields.List(ma.fields.List(ma.fields.Float()))
    vector = ma.fields.List(ma.fields.Float())


class QAOAAlgorithmRequest:
    def __init__(self, matrix, beta, gamma):
        self.adj_matrix = adj_matrix
        self.beta = beta
        self.gamma = gamma


class QAOAAlgorithmRequestSchema(ma.Schema):
    adj_matrix = ma.fields.List(ma.fields.List(ma.fields.Float()))
    beta = ma.fields.Float()
    gamma = ma.fields.Float()


class TSPQAOAAlgorithmRequest:
    def __init__(self, adj_matrix, p, betas, gammas):
        self.adj_matrix = adj_matrix
        self.p = p
        self.betas = betas
        self.gammas = gammas


class TSPQAOAAlgorithmRequestSchema(ma.Schema):
    adj_matrix = ma.fields.List(ma.fields.List(ma.fields.Float()))
    p = ma.fields.Integer()
    betas = ma.fields.List(ma.fields.Float())
    gammas = ma.fields.List(ma.fields.Float())
