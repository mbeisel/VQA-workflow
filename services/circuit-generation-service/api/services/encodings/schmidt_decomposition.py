"""
based on: https://github.com/UST-QuAntiL/schmidt-decomposition by Marius Stach
"""

import numpy as np
import qiskit
from enum import Enum

Measurement = Enum("Measurement", "measure stateVector noMeasurement")


# Perform the Schmidt Decomposition for a given Matrix beta (see [BitterTruth])
# returns unitary Matrices u,v and vector a
def getSchmidtDecomp(beta):
    n, m = beta.shape
    u_, a, v_ = np.linalg.svd(beta)
    v = v_.conj().T
    u = u_[:n, :n]
    return u, a, v


# Method to generate a quantum circuit to initialize a state by its schmidt decomposition
# To use this circuit as initialization for another circuit  use measure = Measurement.noMeasurement
# and build the overall circuit with circuit = getSchmidtCircuit + otherCircuit
# To measure directly after the initialization use measure = Measurement.measure
# To be able to output a state vector after the initialization use measure = Measurement.stateVector
def getSchmidtCircuit(u, a, v, measure=Measurement.measure):
    n_1 = int(np.log2(len(u)))
    n_2 = int(np.log2(len(v)))
    n_qubits = n_1 + n_2

    # initialize the quantum circuit and determine the first and second register
    qc = qiskit.QuantumCircuit(n_qubits, n_qubits)
    first_register = list(np.arange(n_2))
    second_register = list(np.arange(n_2, n_qubits))

    # Initilalizte the first register to sum a_i |e_i> in the standard basis
    qc.initialize(a, first_register)

    # Perform the CNOT Operations to copy the initialization of the first to the second register
    for i in range(n_2):
        qc.cnot(i, i + n_2)

    # Perform unitary operations u, v on the respecting register
    qc.unitary(v, first_register)
    qc.unitary(u, second_register)

    if measure == Measurement.stateVector:
        qc.save_statevector()
    elif measure == Measurement.measure:
        qc.measure(qc.qregs[0], qc.cregs[0])
    return qc


# method to compute the matrix beta defining the state with the tensor product
# of two hilbert spaces from the coefficient vector of the standard basis
def coeffToBeta(coeff):
    n_huge = int(np.log2(len(coeff)))
    n = int(np.ceil(n_huge / 2))
    m = n_huge - n
    beta = np.zeros((2 ** n, 2 ** m))
    formatstring = "0" + str(int(np.log2(len(coeff)))) + "b"
    x_labels = []
    for i in range(len(coeff)):
        x_labels.append(format(i, formatstring))
    for i in range(len(coeff)):
        k = int(x_labels[i][:n], 2)
        l = int(x_labels[i][-m:], 2)
        beta[k, l] = coeff[i]
    return beta


# method to generate the schmidt decomposition circuit form an array
def generate_schmidt_decomposition_from_array(
    array, measurement=Measurement.noMeasurement
):
    coeff = np.array(array)
    coeff = coeff / np.linalg.norm(coeff)
    beta = coeffToBeta(coeff)
    u, a, v = getSchmidtDecomp(beta)
    qc = getSchmidtCircuit(u, a, v, measure=measurement)
    return qc
