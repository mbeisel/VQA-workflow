import unittest
import os, sys
import json
import re

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from app import create_app


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        self.app_context.pop()

    def test_basis_encoding(self):
        # Test for single number
        response = self.client.post(
            "/encoding/basis",
            data=json.dumps(
                {"vector": [3.14], "integral_bits": 3, "fractional_bits": 3}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(7, response.get_json().get("n_qubits"))
        self.assertTrue(
            'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[7];\nx q[2];\nx q[3];\nx q[6];\n'
            in response.get_json().values()
        )

        # Test for list of numbers
        response = self.client.post(
            "/encoding/basis",
            data=json.dumps(
                {"vector": [3.14, 2.25], "integral_bits": 3, "fractional_bits": 3}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(14, response.get_json().get("n_qubits"))
        self.assertTrue(
            'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[14];\nx q[2];\nx q[3];\nx q[6];\nx q[9];\nx q[12];\n'
            in response.get_json().values()
        )

    def test_angle_encoding(self):
        # Test x axis
        response = self.client.post(
            "/encoding/angle",
            data=json.dumps({"vector": [3.14, 2.25], "rotationaxis": "x"}),
            content_type="application/json",
        )
        self.assertEqual(2, response.get_json().get("n_qubits"))
        self.assertTrue("rx(6.28)" in response.get_json().get("circuit"))
        self.assertEqual(response.status_code, 200)

        # Test y axis
        response = self.client.post(
            "/encoding/angle",
            data=json.dumps({"vector": [3.14, 2.25], "rotationaxis": "y"}),
            content_type="application/json",
        )
        self.assertEqual(2, response.get_json().get("n_qubits"))
        self.assertTrue("ry(6.28)" in response.get_json().get("circuit"))
        self.assertEqual(response.status_code, 200)

        # Test z axis
        response = self.client.post(
            "/encoding/angle",
            data=json.dumps({"vector": [3.14, 2.25], "rotationaxis": "z"}),
            content_type="application/json",
        )
        self.assertEqual(2, response.get_json().get("n_qubits"))
        self.assertTrue("rz(6.28)" in response.get_json().get("circuit"))
        self.assertEqual(response.status_code, 200)

    def test_amplitude_encoding(self):
        response = self.client.post(
            "/encoding/amplitude",
            data=json.dumps({"vector": [3.14, 2.75, 2.25, 0.1]}),
            content_type="application/json",
        )
        self.assertEqual(2, response.get_json().get("n_qubits"))
        self.assertTrue(
            "initialize(0.66204957,0.57982049,0.47439858,0.021084381)"
            in response.get_json().get("circuit")
        )
        self.assertEqual(response.status_code, 200)

    def quam_encoding(self):
        response = self.client.post(
            "/encoding/quam",
            data=json.dumps({"vector": 3.14}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_schmidt_decomposition(self):
        response = self.client.post(
            "/encoding/schmidt",
            data=json.dumps({"vector": [3.14, 0, 2.25, 1, 4, 0.5, 2, 2]}),
            content_type="application/json",
        )
        self.assertEqual(3, response.get_json().get("n_qubits"))
        self.assertEqual(3, response.get_json().get("depth"))
        self.assertTrue(
            "gate multiplex1_reverse_dg q0 { ry(0.56396258) q0;"
            in response.get_json().get("circuit")
        )
        self.assertEqual(response.status_code, 200)

        # Test request failure for len(vector) != 2^n
        response = self.client.post(
            "/encoding/schmidt",
            data=json.dumps({"vector": [3.14, 0, 2.25, 1, 4, 0.5, 2, 2, 0]}),
            content_type="application/json",
        )
        self.assertTrue(
            "Invalid vector input! Vector must be of length 2^n"
            in response.get_json().get("message")
        )

    def test_hhl_algorithm(self):
        # Test errors
        response = self.client.post(
            "/algorithms/hhl",
            data=json.dumps(
                {"matrix": [[1.5, 0.5, 1], [0.5, 1.5, 1]], "vector": [0, 1]}
            ),
            content_type="application/json",
        )
        self.assertTrue(
            "Invalid matrix input! Matrix must be square."
            in response.get_json().get("message")
        )
        response = self.client.post(
            "/algorithms/hhl",
            data=json.dumps({"matrix": [[1.5, 0.8], [0.5, 1.5]], "vector": [0, 1]}),
            content_type="application/json",
        )
        self.assertTrue(
            "Invalid matrix input! Matrix must be hermitian."
            in response.get_json().get("message")
        )
        response = self.client.post(
            "/algorithms/hhl",
            data=json.dumps({"matrix": [[1.5, 0.5], [0.5, 1.5]], "vector": [0, 1, 2]}),
            content_type="application/json",
        )
        self.assertTrue(
            "Invalid matrix, vector input! Matrix and vector must be of the same dimension."
            in response.get_json().get("message")
        )
        response = self.client.post(
            "/algorithms/hhl",
            data=json.dumps(
                {
                    "matrix": [[1.5, 0.5, 1.0], [0.5, 1.5, 1.0], [1.0, 1.0, 0.5]],
                    "vector": [0, 1, 2],
                }
            ),
            content_type="application/json",
        )
        self.assertTrue(
            "Invalid matrix input! Input matrix dimension must be 2^n."
            in response.get_json().get("message")
        )

        # Test different matrix sizes
        response = self.client.post(
            "/algorithms/hhl",
            data=json.dumps({"matrix": [[1.5, 0.5], [0.5, 1.5]], "vector": [0, 1]}),
            content_type="application/json",
        )
        self.assertEqual(4, response.get_json().get("n_qubits"))
        self.assertEqual(4, response.get_json().get("depth"))
        match = re.search(
            "amplitude-enc q.*;\nQPE q.*,q.*,q.*;\n1/x q.*,q.*,q.*;\nQPE_dg q.*,q.*,q.*;\n",
            response.get_json().get("circuit"),
        )
        self.assertTrue(match is not None)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/algorithms/hhl",
            data=json.dumps(
                {
                    "matrix": [
                        [1.0, 0.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0, 0.0],
                        [0.0, 0.0, 0.0, 1.0],
                    ],
                    "vector": [0, 1, 0, 0],
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(6, response.get_json().get("n_qubits"))
        self.assertEqual(4, response.get_json().get("depth"))
        match = re.search(
            "amplitude-enc q.*,q.*;\nQPE q.*,q.*,q.*,q.*,q.*;\n1/x q.*,q.*,q.*,q.*;\nQPE_dg q.*,q.*,q.*,q.*,q.*;\n",
            response.get_json().get("circuit"),
        )
        self.assertTrue(match is not None)
        self.assertEqual(response.status_code, 200)
