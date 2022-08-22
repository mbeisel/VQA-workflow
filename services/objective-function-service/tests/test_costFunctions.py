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
            "/objective/tsp",
            data=json.dumps({"adj_matrix":    [[ 0, 15, 16,  7],
                                               [ 8,  0,  5,  1],
                                               [10,  6,  0,  3],
                                               [12,  3,  1,  0]],
                             "counts": {'0001010000101000': 3,
                                     '0010010010000001': 11,
                                     '0001100001000010': 1,
                                     '0001100000100100': 43,
                                     '0001001010000100': 41,
                                     '1000000100100100': 6,
                                     '0100001010000001': 41,
                                     '0100100000100001': 12,
                                     '0010010000011000': 58,
                                     '0001001001001000': 493,
                                     '1000010000010010': 20,
                                     '0001010010000010': 7,
                                     '0010000110000100': 76,
                                     '0010100000010100': 2,
                                     '0010000101001000': 3,
                                     '0100000100101000': 5,
                                     '1000001001000001': 1,
                                     '0100001000011000': 4,
                                     '0100100000010010': 41,
                                     '0010100001000001': 17,
                                     '1000010000100001': 74,
                                     '1000001000010100': 6,
                                     '1000000101000010': 59},
                             "objFun": "Expectation",
                             "visualization": "false"}),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print(response.get_json())
        # self.assertEqual(7, response.get_json().get("n_qubits"))
        # self.assertTrue(
        #     'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[7];\nx q[2];\nx q[3];\nx q[6];\n'
        #     in response.get_json().values()
        # )
        #
        # # Test for list of numbers
        # response = self.client.post(
        #     "/encoding/basis",
        #     data=json.dumps(
        #         {"vector": [3.14, 2.25], "integral_bits": 3, "fractional_bits": 3}
        #     ),
        #     content_type="application/json",
        # )
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(14, response.get_json().get("n_qubits"))
        # self.assertTrue(
        #     'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[14];\nx q[2];\nx q[3];\nx q[6];\nx q[9];\nx q[12];\n'
        #     in response.get_json().values()
