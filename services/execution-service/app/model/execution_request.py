import marshmallow as ma

class ExecutionRequest:
    def __init__(self, circuit, provider, qpu, credentials, shots=1000, noiseModel=None):
        self.circuit = circuit
        self.provider = provider
        self.qpu = qpu
        self.credentials = credentials
        self.shots = shots
        self.noise_model = noiseModel



class ExecutionRequestSchema(ma.Schema):
    circuit = ma.fields.Str()
    provider = ma.fields.Str()
    qpu = ma.fields.Str()
    credentials = ma.fields.Dict(keys=ma.fields.Str(), values=ma.fields.Str())
    shots = ma.fields.Int()
    noiseModel = ma.fields.Str()

