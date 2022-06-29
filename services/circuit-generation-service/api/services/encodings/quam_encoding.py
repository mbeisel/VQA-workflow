# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 08:33:26 2020

@author: mariu

Implementation of a quantum associative memory as defined in [Ventura et. all 2000]
"""
import pennylane as qml
from pennylane import numpy as np

import matplotlib.pyplot as plt

import qiskit

# Verify IBMQ Account with saved Token
qiskit.IBMQ.load_account()


def normalize_patterns(patterns):
    """
    Method to clean up a set of existing patterns.
    This Method brings all pattern to the same length which is the maximum
    occuring length of an existing pattern

    Parameters
    ----------
    patterns : List of Patterns (One Pattern is Bit-List e.g. [1,0,1,0,0])


    Returns
    -------
    new_patterns : List of Patterns
        Returns a new List with the same Patterns as in the parameter patterns
        but all with the same length (add zeroes from the left)

    """
    max_len = 0
    for pattern in patterns:
        if len(pattern) > max_len:
            max_len = len(pattern)

    new_patterns = []
    for pattern in patterns:
        temp_len = len(pattern)
        temp_pattern = []

        # Add zeroes for length
        for i in range(max_len - temp_len):
            temp_pattern.append(0)

        # Add rest of pattern
        for i in range(temp_len):
            temp_pattern.append(pattern[i])

        new_patterns.append(temp_pattern)
    return new_patterns


def load(patterns):
    """
    Loads the patterns given in "patterns" into a equal superposition and returns
    "n_samples" (specidfied in quantum device) Observations of this state

    Parameters
    ----------
    patterns : List of Patterns

    Returns
    -------
    result : "n_samples" (specidfied in quantum device) Observations of the first n_ Qbits


    """
    patterns = normalize_patterns(patterns)
    m = len(patterns)  # Amount of patterns
    n = len(patterns[0])  # Amount of Bits per Pattern

    # Create QBit Device with needed amount of qbits (2n+1)
    # dev_qubit = qml.device("default.qubit", wires=2*n+1,shots=100)
    dev_qubit = qml.device(
        "qiskit.ibmq", backend="ibmq_qasm_simulator", wires=2 * n + 1, shots=8000
    )

    def comp_basis_measurement(n_wires):
        """
        Returns Hermetian Matrix to measure the state of "n_wires" many QBits
        """
        wires = []
        for i in range(0, n_wires):
            wires.append(i)
        return qml.Hermitian(np.diag(range(2 ** n_wires)), wires=wires)

    def Sp(p):
        """
        Returns the Matrix Sp as defined in [Ventura et. all 2000]
        """
        val_1 = np.sqrt((p - 1) / p)
        val_2 = 1 / np.sqrt(p)
        return np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, val_1, -val_2], [0, 0, val_2, val_1]]
        )

    def A_Operator(controls, wires):
        """
        Implementation of the A Operator as defined in [Ventura et. all 2000]

        Parameters
        ----------
        controls : list of 2 control Q-Bits for the A operator
        wires : list of the 3 qbit wires the operator works on

        """
        if controls[0] == 0:
            qml.PauliX(wires[0])
        if controls[1] == 0:
            qml.PauliX(wires[1])

        qml.Toffoli(wires=wires)

        if controls[0] == 0:
            qml.PauliX(wires[0])
        if controls[1] == 0:
            qml.PauliX(wires[1])

    def F_Operator(control, wires):
        """
        Implementation of the F Operator as defined in [Ventura et. all 2000]

        Parameters
        ----------
        controls : control Q-Bits for the A operator
        wires : list of the 2 qbit wires the operator works on

        """
        if control == 0:
            qml.PauliX(wires=wires[0])

        qml.CNOT(wires=[wires[0], wires[1]])

        if control == 0:
            qml.PauliX(wires=wires[0])

    def Sp_Operator(p, wires):
        """
        Implementation of the SP Operator as defined in [Ventura et. all 2000]

        Parameters
        ----------
        p : Parameter p of the Sp Operator
        wires : list of the 2 qbit wires the operator works on

        """
        qml.QubitUnitary(Sp(p), wires=wires)

    @qml.qnode(dev_qubit)
    def load_circuit(patterns_=None, n_=None, m_=None):
        """
        Quntum Circuit to load the given patterns in equal superposition

        Parameters
        ----------
        patterns_ : List of Patterns to be loaded to superposition
        n_ : int, number of bits one pattern uses
        m_ : int, number of patterns

        Returns
        -------
        samples : "n_samples" (specidfied in quantum device) Observations of the first n_ Qbits

        """
        all_ranges = np.arange(0, 2 * n_ + 1, dtype=int)
        x_range = all_ranges[
            0:n_
        ]  # To directly address x[i] as defined in [Ventura et. all 2000]
        g_range = all_ranges[
            n_ : (n_ + n_ - 1)
        ]  # To directly address g[i] as defined in [Ventura et. all 2000]
        c_range = all_ranges[
            (2 * n_ - 1) :
        ]  # To directly address c[i] as defined in [Ventura et. all 2000]

        patterns.append(
            list(np.zeros(n_, dtype=int))
        )  # Append one zero pattern which is not loaded into the uperposition, but used for initialization of the first pattern

        # The following Code is mainly the Quantum algorithm for storing patterns as defined in Fig. 2 of [Ventura et. all 2000]
        # The indices are shifted by 1 because [Ventura et. all 2000] starts counting at 1 and python starts at 0
        for p in np.arange(m - 1, -1, -1):
            for i in range(0, n):
                if patterns_[p][i] != patterns_[p + 1][i]:
                    F_Operator(control=0, wires=[int(c_range[1]), int(x_range[i])])
            F_Operator(control=0, wires=[int(c_range[1]), int(c_range[0])])

            Sp_Operator(p + 1, wires=[int(c_range[0]), int(c_range[1])])
            A_Operator(
                controls=[int(patterns_[p][0]), int(patterns_[p][1])],
                wires=[int(x_range[0]), int(x_range[1]), int(g_range[0])],
            )

            for k in range(2, n):
                A_Operator(
                    controls=[int(patterns_[p][k]), 1],
                    wires=[int(x_range[k]), int(g_range[k - 2]), int(g_range[k - 1])],
                )
            F_Operator(1, wires=[int(g_range[n - 2]), int(c_range[0])])

            for k in np.arange(n - 1, 1, -1):
                A_Operator(
                    controls=[int(patterns_[p][k]), 1],
                    wires=[int(x_range[k]), int(g_range[k - 2]), int(g_range[k - 1])],
                )
            A_Operator(
                controls=[int(patterns_[p][0]), int(patterns_[p][1])],
                wires=[int(x_range[0]), int(x_range[1]), int(g_range[0])],
            )

        return qml.sample(comp_basis_measurement(n_))

    result = load_circuit(patterns_=patterns, n_=n)

    # Plot of the measurement freuquencys for all measured patterns
    xticks = range(0, 2 ** n)
    xtick_labels = list(map(lambda x: format(x, "04b"), xticks))
    bins = np.arange(0, 2 ** n + 1) - 0.5

    plt.figure()
    plt.title("Measurement frequency for all patterns")
    plt.xlabel("bitstrings")
    plt.ylabel("freq.")
    plt.xticks(xticks, xtick_labels, rotation="vertical")
    plt.hist(result, bins=bins)
    plt.show()
    return result


result = load([[1, 0], [1, 1, 1, 1], [1, 0, 1], [0], [1, 0, 1, 0]])
