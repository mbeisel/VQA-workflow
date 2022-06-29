import qiskit
from flask import jsonify
from qiskit.providers.ibmq import IBMQ


def getCircuitCharacteristics(circuit, backend=None):
    if not backend:
        provider = IBMQ.get_provider(hub="ibm-q")
        backend = provider.get_backend("ibmq_qasm_simulator")
        backend = provider.get_backend("ibmq_lima")
    transpiled = qiskit.compiler.transpile(circuit, backend=backend)
    return transpiled.width(), transpiled.depth()


def bad_request(message):
    response = jsonify({"code": 400, "error": "bad request", "message": message})
    response.status_code = 400
    return response
