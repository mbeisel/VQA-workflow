from qiskit.circuit.quantumcircuit import QuantumCircuit


class BasisEncoding:
    # returns binary string for basis encoding
    # leading 0 for positive and leading 1 for negative values
    @classmethod
    def basis_encode_number(cls, number, n_integralbits, n_fractional_part):
        """
        Computes the Encoding String for a number depending on the set precision
        :param number: Input decimal number as int or float
        :param n_integralbits: Precision of the integral part of the number
        :param n_fractional_part: Precision of the fractional part of the number
        :return: String that represents the basis encoding;
                 Leading 0/1 for positive/negative number, followed by the integral and the fractional part
        """
        prefix = "1" if number < 0 else "0"
        integral_part = cls.get_integral_part(int(number), n_integralbits)
        fractional_part = cls.get_fractional_part(
            number - int(number), n_fractional_part
        )
        return prefix + integral_part + fractional_part

    @classmethod
    def basis_encode_list(cls, list, n_integralbits, n_fractional_part):
        """
        Computes the Encoding Strings for a list of number depending on the set precision
        :param list: List of int or float decimal numbers that should be encoded
        :param n_integralbits: Precision of the integral part of the number
        :param n_fractional_part: Precision of the fractional part of the number
        :return: List of Strings that represents the basis encoding;
                 Leading 0/1 for positive/negative number, followed by the integral and the fractional part
        """
        list = [
            cls.basis_encode_number(i, n_integralbits, n_fractional_part) for i in list
        ]
        return list

    @classmethod
    def get_fractional_part(cls, fractionalPart, precision):
        """
        Computes the fractional part of a number in [0,1] as a binary string
        :param fractionalPart: A decimal number in [0,1] that will get binary encoded
        :param precision: Precision of the fractional part of the number
        :return: String of the binary encoding of a number in [0,1]
        """
        fractionalString = ""
        for i in range(0, precision):
            fractionalPart *= 2
            if fractionalPart >= 1:
                fractionalString += "1"
                fractionalPart -= 1
            else:
                fractionalString += "0"
        return fractionalString

    @classmethod
    def get_integral_part(cls, integralPart, precision):
        """
        Computes the integral Part of a Integer as a binary string
        :param integralPart: A decimal int that will get binary encoded
        :param precision: Precision of the integral part of the number
        :return: String of the binary encoding of a integer
        """
        integralString = (
            "0" * precision if integralPart == 0 else "{0:b}".format(abs(integralPart))
        )
        if len(integralString) < precision:
            integralString = "0" * (precision - len(integralString)) + integralString
        elif len(integralString) > precision:
            integralString = "1" * precision
        return integralString

    @classmethod
    def basis_encode_list_subcircuit(cls, list, n_integralbits, n_fractional_part):
        """
        Generates the circuit for the basis encoding of a list of number with given precision
        :param number: List of decimal number as int or float
        :param n_integralbits: Precision of the integral part of the number
        :param n_fractional_part: Precision of the fractional part of the number
        :return: QisQit QuantumCircuit that basisencodes the inputlist at give precision
        """
        listAsString = cls.basis_encode_list(list, n_integralbits, n_fractional_part)
        numberArray = [
            cls.convert_bitstring_to_intarray(listAsString[i])
            for i in range(len(listAsString))
        ]
        n_qubits = (1 + n_integralbits + n_fractional_part) * len(numberArray)

        encoding_subcircuit = QuantumCircuit(n_qubits, name="basisencode numberlist")
        for j in range(0, len(numberArray)):
            [
                (
                    encoding_subcircuit.x(i + (j * len(numberArray[j])))
                    if numberArray[j][i] == 1
                    else 0
                )
                for i in range(len(numberArray[j]))
            ]

        return encoding_subcircuit

    @classmethod
    def convert_bitstring_to_intarray(cls, bitstring):
        """
        Converts Bistring into an Array of 0 & 1s
        :param bitstring:
        :return: int[] representing the bitstring
        """
        numberArray = []
        [numberArray.append(int(i)) for i in bitstring]
        return numberArray
