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

from app import app, optimizer
from flask import jsonify, abort, request
from .optimizer import Optimizer


@app.route('/optimization-service', methods=['POST'])
def execute_circuit():
    """Execute a given quantum circuit on a specified quantum computer."""

    app.logger.info('Received Post request to execute circuit...')
    if not request.json:
        app.logger.error("Service currently only supports JSON")
        abort(400, "Only Json supported")

    if 'corr_id' not in request.json:
        app.logger.error("corr_id not defined in request")
        abort(400, "corr_id not defined in request")
    corr_id = request.json['corr_id']
    app.logger.info('corr_id: ' + corr_id)

    if 'optimizer' not in request.json:
        app.logger.error("optimizer not defined in request")
        abort(400, "optimizer not defined in request")
    optimizer = request.json['optimizer']
    app.logger.info('optimizer: ' + optimizer)
    if not optimizer.lower() in ['cobyla', 'spsa', 'nelder-mead']:
        app.logger.error("optimizer is not supported.")
        abort(400, "optimizer is not supported.")

    if 'initialParameters' not in request.json:
        app.logger.error("initialParameters not defined in request")
        abort(400, "initialParameters not defined in request")
    initialParameters = request.json['initialParameters']
    app.logger.info('initialParameters: ' + initialParameters)

    if 'returnAddress' not in request.json:
        app.logger.error("returnAddress not defined in request")
        abort(400, "returnAddress not defined in request")
    returnAddress = request.json['returnAddress']
    app.logger.info('returnAddress: ' + returnAddress)


    # Threaded longrunning task version
    # t = threading.Thread(target=circuit_executor.execute_circuit, args=(quantum_circuit, qpu, credentials, shots))
    # t.daemon = True
    # t.start()
    # return jsonify({'Status': "Circuit execution process initiated"}), 200
    process = Optimizer(corr_id, optimizer, initialParameters, returnAddress)
    process.start()
    return jsonify('Optimization process for id {} started'.format(corr_id))
