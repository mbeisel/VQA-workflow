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

import json
import time
from multiprocessing import Process
import pika
from flask import jsonify
from qiskit.algorithms.optimizers import SPSA
import scipy.optimize as optimize
from app import app
import requests

class Optimizer (Process):
    def __init__(self, corr_id, optimizer, parameters, return_address):
        super().__init__()
        self.corr_id = corr_id
        self.optimizer = optimizer
        self.parameters = parameters
        self.return_address = return_address


    def run(self):
        print("Starting optimization")

        def decoyfunction(opt_parameters, *args):
            print('publish' + str(opt_parameters))
            camunda_callback = requests.post(self.return_address,
                                             json={"corr_id": self.corr_id, "variables": {
                                                     "parameters": str(opt_parameters)}})
            app.logger.info("Callback returned status code: " + str(camunda_callback.status_code))
            # channel.basic_publish(exchange='',
            #                       routing_key=self.exec_queue_name,
            #                       body=json.dumps({'params':list(x)}))

            # TODO
            # pollQueue
            # return value

            # while True:
            #     time.sleep(1)
            #     try:
            #         #result = channel.queue_declare(queue=self.queueName, passive=True).method
            #         method_frame, header_frame, body = channel.basic_get(self.opt_queue_name)
            #         if method_frame:
            #             print(method_frame, header_frame, body)
            #             received_params = json.loads(body.decode("utf-8"))
            #             channel.basic_ack(method_frame.delivery_tag)
            #             return received_params['objectiveValue']
            #
            #     except Exception:
            #         print('No message returned')
            #     print("Thread" + self.opt_queue_name + "checking queue for " + self.opt_queue_name)

        #channel.basic_consume(queue='initOptimization', on_message_callback=optimizeCallback, auto_ack=True)
        if self.optimizer.lower() == 'spsa':
            spsa = SPSA(maxiter=200)
            res = spsa.optimize(len(self.parameters), decoyfunction, initial_point=self.parameters)
        else:
            res = optimize.minimize(decoyfunction, self.parameters, method=self.optimizer)
        print(res)
        print ("Exiting " + self.name)












import threading
from urllib.request import urlopen
import json
import numpy as np
import qiskit
from qiskit import *
from qiskit import transpile
import requests
import os


def send_error(errorCode, externalTaskId):
    body = {
        "workerId": "KMeansInitializerService",
        "errorCode": errorCode
    }
    response = requests.post(pollingEndpoint + '/' + externalTaskId + '/bpmnError', json=body)
    print(response.status_code)


def poll():
    print('Polling for new external tasks at the Camunda engine with URL: ', pollingEndpoint)

    body = {
        "workerId": "KMeansExecutorService",
        "maxTasks": 1,
        "topics":
            [{"topicName": topic,
              "lockDuration": 100000000
              }]
    }

    try:
        response = requests.post(pollingEndpoint + '/fetchAndLock', json=body)

        if response.status_code == 200:
            for externalTask in response.json():
                print('External task with ID for topic ' + str(externalTask.get('topicName')) + ': ' + str(
                    externalTask.get('id')))
                variables = externalTask.get('variables')
                if externalTask.get('topicName') == topic:
                    if ('circuits_string' in variables) & ('ibmq_token' in variables) & ('ibmq_backend' in variables):
                        if variables.get("circuits_string").get("type") == "String":
                            circuits_string = variables.get("circuits_string").get("value")
                        else:
                            circuits_string = download_data(camundaEndpoint + "/process-instance/" + externalTask.get("processInstanceId") + "/variables/circuits_string/data")
                        if variables.get("ibmq_token").get("type") == "String":
                            ibmq_token = variables.get("ibmq_token").get("value")
                        else:
                            ibmq_token = download_data(camundaEndpoint + "/process-instance/" + externalTask.get("processInstanceId") + "/variables/ibmq_token/data")
                        if variables.get("ibmq_backend").get("type") == "String":
                            ibmq_backend = variables.get("ibmq_backend").get("value")
                        else:
                            ibmq_backend = download_data(camundaEndpoint + "/process-instance/" + externalTask.get("processInstanceId") + "/variables/ibmq_backend/data")

                        cluster_mapping = execute(circuits_string, ibmq_token, ibmq_backend)

                        # send response
                        body = {
                            "workerId": "KMeansExecutorService",
                            "variables":
                                {"cluster_mapping": {"value": cluster_mapping, "type": "String"}}
                        }
                        response = requests.post(pollingEndpoint + '/' + externalTask.get('id') + '/complete',
                                                 json=body)
                        print('Status code of response message: ' + str(response.status_code))
                    else:
                        send_error("Executing K-Means failed", externalTask.get('id'))
    except Exception as e:
        print('Exception during polling!')
        print(e)

    threading.Timer(3, poll).start()


def download_data(url):
    response = urlopen(url)
    data = response.read().decode('utf-8')
    return str(data)


def create_backend(backend_name, token):
    backend_name = backend_name.lower()
    if 'aer' in backend_name:
        provider = 'aer'
        instance = backend_name[4:]
    elif 'ibmq' in backend_name:
        provider = 'ibmq'
        instance = backend_name
    else:
        raise Exception('Unknown backend name specified.')

    if 'ibmq' in provider:
        if token == '':
            raise Exception('A token is needed when using ibm backends.')
        else:
            if IBMQ.active_account():
                IBMQ.disable_account()
            return IBMQ.enable_account(token).get_backend(instance)

    elif 'aer' in provider:
        if 'qasm' in instance:
            return Aer.get_backend('qasm_simulator')
        elif 'vector' in instance:
            return Aer.get_backend('statevector_simulator')
        else:
            raise Exception('Backend provider '
                            + provider
                            + ' does not have an instance called '
                            + instance
                            + '.')
    else:
        raise Exception('Unknown backend provider.')



def execute(circuits_string, ibmq_token, ibmq_backend):
    print('Executing K-Means circuits...')

    # retrieve IBMQ backend object
    backend = create_backend(ibmq_backend, ibmq_token)

    # retrieve circuits from the string representation
    circuits_strings = circuits_string.split('##########')
    circuits = []
    for circuit_string in circuits_strings:
        circuits.append(QuantumCircuit.from_qasm_str(circuit_string))

    # execute the circuits and retrieve the cluster mappings
    print('Executing circuits: ', len(circuits))
    cluster_mapping = execute_negative_rotation_clustering(circuits, 2, backend, 8192)

    return str(json.dumps(cluster_mapping.tolist()))


camundaEndpoint = os.environ['CAMUNDA_ENDPOINT']
pollingEndpoint = camundaEndpoint + '/external-task'
topic = os.environ['CAMUNDA_TOPIC']
poll()
