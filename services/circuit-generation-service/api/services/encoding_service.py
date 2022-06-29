import numpy as np
from flask import jsonify

from api.services.encodings.basis_encoding import BasisEncoding
from api.services.encodings.angle_encoding import AngleEncoding
from api.services.encodings.amplitude_encoding import AmplitudeEncoding
from api.services.encodings.schmidt_decomposition import (
    generate_schmidt_decomposition_from_array,
    Measurement,
)
from api.services.helper_service import getCircuitCharacteristics, bad_request
from api.model.circuit_response import CircuitResponse


def generate_basis_encoding(input):
    vector = input.get("vector")
    n_integral_bits = input.get("integral_bits")
    n_fractional_bits = input.get("fractional_bits")
    if isinstance(vector, list):
        circuit = BasisEncoding.basis_encode_list_subcircuit(
            vector, n_integral_bits, n_fractional_bits
        )
    else:
        circuit = BasisEncoding.basis_encode_number_subcircuit(
            vector, n_integral_bits, n_fractional_bits
        )
    return CircuitResponse(
        circuit.qasm(), "encoding/basis", circuit.num_qubits, circuit.depth(), input
    )


def generate_angle_encoding(input):
    vector = input.get("vector")
    rotation_axis = input.get("rotationaxis")
    circuit = AngleEncoding.angle_encode_vector(vector, rotation_axis)

    return CircuitResponse(
        circuit.qasm(), "encoding/angle", circuit.num_qubits, circuit.depth(), input
    )


def generate_amplitude_encoding(input):
    vector = input.get("vector")
    circuit = AmplitudeEncoding.amplitude_encode_vector(vector)
    # width,depth = getCircuitCharacteristics(circuit) TODO dicuss if this makes more sense
    return CircuitResponse(
        circuit.qasm(), "encoding/amplitude", circuit.num_qubits, circuit.depth(), input
    )


def generate_quam_encoding(input):
    return CircuitResponse(None, "encoding/quam", None, None, None)


def generate_schmidt_decomposition(input):
    vector = input.get("vector")

    if np.log2(len(vector)) % 1 != 0:
        return bad_request("Invalid vector input! Vector must be of length 2^n")

    circuit = generate_schmidt_decomposition_from_array(
        vector, Measurement.noMeasurement
    )
    return CircuitResponse(
        circuit.qasm(), "encoding/schmidt", circuit.num_qubits, circuit.depth(), input
    )
