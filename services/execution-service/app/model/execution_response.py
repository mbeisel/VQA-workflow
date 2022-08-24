import marshmallow as ma

class ExecutionResponse:
    def __init__(self, counts, meas_qubits):
        super().__init__()
        self.counts = counts
        self.meas_qubits = meas_qubits

    def to_json(self):
        json_execution_response = {
            "counts": self.counts,
            "meas_qubits": self.meas_qubits
        }
        return json_execution_response


class ExecutionResponseSchema(ma.Schema):
    counts = ma.fields.Dict(keys=ma.fields.Str(), values=ma.fields.Float())
    meas_qubits = ma.fields.List(ma.fields.Int())