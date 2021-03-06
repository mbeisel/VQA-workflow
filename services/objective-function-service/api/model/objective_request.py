import marshmallow as ma
from marshmallow import pre_load, ValidationError
import numpy as np

class TSPObjectiveFunctionRequest:
    def __init__(self, adj_matrix, counts, objFun):
        self.adj_matrix = adj_matrix
        self.counts = counts
        self.objFun = objFun


class TSPObjectiveFunctionRequestSchema(ma.Schema):
    adj_matrix = ma.fields.List(ma.fields.List(ma.fields.Float()))
    counts = ma.fields.Dict(keys=ma.fields.Str(), values=ma.fields.Float())
    objFun = ma.fields.Str()
