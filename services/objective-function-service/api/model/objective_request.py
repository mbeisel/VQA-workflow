import marshmallow as ma
from marshmallow import pre_load, ValidationError
import numpy as np

class TSPObjectiveFunctionRequest:
    def __init__(self, adj_matrix, counts, objFun, visualization=False):
        self.adj_matrix = adj_matrix
        self.counts = counts
        self.objFun = objFun
        self.visualization = visualization


class TSPObjectiveFunctionRequestSchema(ma.Schema):
    adj_matrix = ma.fields.List(ma.fields.List(ma.fields.Float()))
    counts = ma.fields.Dict(keys=ma.fields.Str(), values=ma.fields.Float())
    objFun = ma.fields.Str()
    visualization = ma.fields.Boolean()


class MaxCutObjectiveFunctionRequest:
    def __init__(self, adj_matrix, counts, objFun, visualization=False):
        self.adj_matrix = adj_matrix
        self.counts = counts
        self.objFun = objFun
        self.visualization = visualization


class MaxCutObjectiveFunctionRequestSchema(ma.Schema):
    adj_matrix = ma.fields.List(ma.fields.List(ma.fields.Float()))
    counts = ma.fields.Dict(keys=ma.fields.Str(), values=ma.fields.Float())
    objFun = ma.fields.Str()
    visualization = ma.fields.Boolean()
