# ******************************************************************************
#  Copyright (c) 2020 University of Stuttgart
#
#  See the NOTICE file(s) distributed with this work for additional
#  information regarding copyright ownership.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ******************************************************************************
import threading

from app import app, circuit_executor
from flask import jsonify, abort, request


@app.route('/execution-service', methods=['POST'])
def execute_circuit():
    """Execute a given quantum circuit on a specified quantum computer."""

    app.logger.info('Received Post request to execute circuit...')
    if not request.json:
        app.logger.error("Service currently only supports JSON")
        abort(400, "Only Json supported")

    if 'ProgrammingLanguage' not in request.json:
        app.logger.error("ProgrammingLanguage not defined in request")
        abort(400, "ProgrammingLanguage not defined in request")
    programming_language = str(request.json['ProgrammingLanguage'])
    app.logger.info('ProgrammingLanguage: ' + programming_language)
    if not programming_language.lower() in ['qiskit', 'openqasm']:
        app.logger.error("ProgrammingLanguage is not supported. Currently only Qiskit can be used")
        abort(400, "ProgrammingLanguage is not supported. Currently only Qiskit can be used")

    # if 'Provider' not in request.json:
    #     app.logger.error("Provider not defined in request")
    #     abort(400, "Provider not defined in request")
    # provider = request.json['Provider']
    # app.logger.info('Provider: ' + provider)
    # if not provider.lower() == 'ibm':
    #     app.logger.error("Provider is not supported. Currently only IBM can be used")
    #     abort(400, "Provider is not supported. Currently only IBM can be used")

    if 'QPU' not in request.json:
        app.logger.error("QPU not defined in request")
        abort(400, "QPU not defined in request")
    qpu = request.json['QPU']
    app.logger.info('QPU: ' + qpu)

    if 'Credentials' not in request.json:
        app.logger.error("AccessToken not defined in request")
        abort(400, "AccessToken not defined in request")
    credentials = request.json['Credentials']

    if 'QuantumCircuit' not in request.json:
        app.logger.error("QuantumCircuit not defined in request")
        abort(400, "QuantumCircuit not defined in request")
    quantum_circuit = request.json['QuantumCircuit']

    shots = request.json['Shots']
    if 'Shots' not in request.json:
        app.logger.info("Using default number of shots (1024)")
        shots = 1024

    app.logger.info("Passed input is valid")


    # Threaded longrunning task version
    # t = threading.Thread(target=circuit_executor.execute_circuit, args=(quantum_circuit, qpu, credentials, shots))
    # t.daemon = True
    # t.start()
    # return jsonify({'Status': "Circuit execution process initiated"}), 200
    return circuit_executor.execute_circuit(quantum_circuit, qpu, credentials, shots)
