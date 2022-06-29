import qiskit
from itertools import product, combinations


class TSPQAOAAlgorithm:
    @classmethod
    def create_circuit(cls, adj_matrix, p, beta, gamma):

        """
        Creates a parametrized qaoa circuit

        Args:
            adj_matrix: Adjacency matrix as numpy array
            p: int
               Number of repetitions of unitaries

        Returns:
            qc: qiskit circuit
        """

        # TODO: Implement get_commutative_mapping, then remove this assertion. Everything else
        # works for arbitrary TSP instance sizes
        assert len(adj_matrix) <= 4, "Only works for problem size at most 4 atm"
        assert (
            p == len(beta) == len(gamma)
        ), "Need to provide correct number of p parameter values for beta and gamma"

        n_qubits = len(adj_matrix) ** 2

        mapping = cls.get_commutative_mapping(len(adj_matrix))

        qc = qiskit.QuantumCircuit(n_qubits)

        # initial_state
        for i in range(0, n_qubits, len(adj_matrix) + 1):
            qc.x(i)

        for i in range(p):
            cls.build_phase_separator(qc, adj_matrix, gamma[i], mapping)
            cls.build_mixer(qc, beta[i], mapping, len(adj_matrix))

        qc.measure_all()

        return qiskit.transpile(qc, optimization_level=3)  # , beta, gamma

    @classmethod
    def C3RXGate(cls, theta):
        qc = qiskit.QuantumCircuit(4)
        qc.h(3)
        qc.p(theta / 8, [0, 1, 2, 3])
        qc.cx(0, 1)
        qc.p(-theta / 8, 1)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.p(-theta / 8, 2)
        qc.cx(0, 2)
        qc.p(theta / 8, 2)
        qc.cx(1, 2)
        qc.p(-theta / 8, 2)
        qc.cx(0, 2)
        qc.cx(2, 3)
        qc.p(-theta / 8, 3)
        qc.cx(1, 3)
        qc.p(theta / 8, 3)
        qc.cx(2, 3)
        qc.p(-theta / 8, 3)
        qc.cx(0, 3)
        qc.p(theta / 8, 3)
        qc.cx(2, 3)
        qc.p(-theta / 8, 3)
        qc.cx(1, 3)
        qc.p(theta / 8, 3)
        qc.cx(2, 3)
        qc.p(-theta / 8, 3)
        qc.cx(0, 3)
        qc.h(3)
        return qc.to_gate()

    @classmethod
    def qubit_timestep_to_index(cls, qubit, timestep, n_qubits):
        qubit = qubit % n_qubits
        timestep = timestep % n_qubits
        return qubit * n_qubits + timestep

    @classmethod
    def build_phase_separator(cls, qc, adj_matrix, parameter, mapping):
        """
        Phase separator for a single iteration, hence only a single parameter is used
        """
        n_qubits = len(adj_matrix)
        for layer in mapping:
            # This should all happen in depth 1
            for timestep, qubits in product(layer[0], layer[1]):
                qs = tuple(qubits)

                id1 = cls.qubit_timestep_to_index(qs[0], timestep, n_qubits)
                id2 = cls.qubit_timestep_to_index(qs[1], timestep + 1, n_qubits)
                qc.rzz(2 * parameter * adj_matrix[qs[0], qs[1]], id1, id2)

                id1 = cls.qubit_timestep_to_index(qs[1], timestep, n_qubits)
                id2 = cls.qubit_timestep_to_index(qs[0], timestep + 1, n_qubits)
                qc.rzz(2 * parameter * adj_matrix[qs[1], qs[0]], id1, id2)

    @classmethod
    def build_mixer(cls, qc, parameter, mapping, n_qubits):
        """
        Mixer for a single iteration, hence only a single parameter is used
        """

        def four_qubit_swap_gate(parameter):
            # TODO: This gate could probably be optimized further
            gate = qiskit.QuantumCircuit(4)
            gate.cx(2, 3)
            gate.cx(2, 0)
            gate.cx(1, 2)
            gate.x(2)
            gate.append(cls.C3RXGate(theta=2 * parameter), (0, 2, 3, 1))
            gate.x(2)
            gate.cx(1, 2)
            gate.cx(2, 0)
            gate.cx(2, 3)
            transpiled = qiskit.transpile(gate, optimization_level=3)
            return transpiled.to_gate()

        def four_qubit_swap(u, v, t):
            i = t
            ip1 = t + 1
            ui = cls.qubit_timestep_to_index(u, i, n_qubits)
            uip1 = cls.qubit_timestep_to_index(u, ip1, n_qubits)
            vi = cls.qubit_timestep_to_index(v, i, n_qubits)
            vip1 = cls.qubit_timestep_to_index(v, ip1, n_qubits)
            qc.append(swap_gate, (ui, vi, uip1, vip1))

        swap_gate = four_qubit_swap_gate(parameter)
        for layer in mapping:
            # This should all happen in depth 1
            for timestep, qubits in product(layer[0], layer[1]):
                qs = tuple(qubits)
                four_qubit_swap(qs[0], qs[1], timestep)

    @classmethod
    def get_commutative_mapping(cls, n_vertices):
        # edge coloring, sodass nodes zueinander gemapped werden, deren gates kommutieren
        # für n <= 4 was statisches ausgeben
        if n_vertices == 3:
            p_col = (
                frozenset((frozenset((0, 1)),)),
                frozenset((frozenset((0, 2)),)),
                frozenset((frozenset((1, 2)),)),
            )
            p_par = (frozenset((0,)), frozenset((1,)), frozenset((2,)))

            return list(product(p_par, p_col))
        elif n_vertices == 4:
            p_col = (
                frozenset((frozenset((0, 1)), frozenset((2, 3)))),
                frozenset((frozenset((0, 2)), frozenset((1, 3)))),
                frozenset((frozenset((0, 3)), frozenset((1, 2)))),
            )
            p_par = (frozenset((0, 2)), frozenset((1, 3)))

            return list(product(p_par, p_col))
        else:
            # TODO: Solve edge coloring problem
            raise Exception("Pls say n_vertices<=4 thx")
