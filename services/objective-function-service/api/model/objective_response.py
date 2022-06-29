from datetime import datetime
import marshmallow as ma
from .objective_request import TSPObjectiveFunctionRequestSchema


class ObjectiveResponse:
    def __init__(self, objective_value, input):
        super().__init__()
        self.objective_value = objective_value
        self.input = input
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def to_json(self):
        json_objective_response = {
            "objective_value": self.objective_value,
            "input": self.input,
            "timestamp": self.timestamp,
        }
        return json_objective_response


class ObjectiveResponseSchema(ma.Schema):
    objective_value = ma.fields.Float()
    input = ma.fields.Nested(TSPObjectiveFunctionRequestSchema)
    timestamp = ma.fields.String()
