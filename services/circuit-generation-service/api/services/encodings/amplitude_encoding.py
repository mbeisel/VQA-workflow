from qiskit import QuantumRegister
from qiskit.circuit.quantumcircuit import QuantumCircuit
import numpy as np


class AmplitudeEncoding:
    @classmethod
    def preprocess(cls, vector, n_qubits, fill_up_with=None):
        """Preprocess data
        Fill up with "fill_up_with" to match dimension of n_qubits ** 2
        Normalize data to length |a| ** 2 = 1
        """
        if fill_up_with is not None and len(vector) < 2 ** n_qubits:
            filler = [fill_up_with] * (2 ** n_qubits - len(vector))
            vector = vector + filler

        # normalize
        norm = np.sum(np.abs(vector) ** 2)
        vector = vector / np.sqrt(norm)
        return vector

    @classmethod
    def amplitude_encode_vector(cls, vector):
        """
        :param vector: input vector containing floats to encode
        :return: OpenQASM Circuit
        """

        n_qubits = (
            int(np.log2(len(vector)))
            if np.log2(len(vector)) % 1 == 0
            else int(np.log2(len(vector))) + 1
        )
        vector = cls.preprocess(vector=vector, n_qubits=n_qubits, fill_up_with=0)

        q = QuantumRegister(n_qubits)
        encoding_subcircuit = QuantumCircuit(q)
        encoding_subcircuit.initialize(vector, [q[i] for i in range(n_qubits)])

        return encoding_subcircuit
