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
import logging
import time
from multiprocessing import Process
from flask import jsonify
from qiskit.algorithms.optimizers import SPSA
import scipy.optimize as optimize
from app import app
import requests
import threading
from urllib.request import urlopen
from qiskit import *
import os

class Optimizer (Process):
    def __init__(self, topic, optimizer, parameters):
        super().__init__()
        self.topic = topic
        self.optimizer = optimizer
        self.parameters = parameters
        self.return_address = None

        self.camundaEndpoint = os.environ['CAMUNDA_ENDPOINT']
        print('endpoint', self.camundaEndpoint)
        #self.camundaEndpoint = "http://localhost:8080/engine-rest"  # os.environ['CAMUNDA_ENDPOINT']

        self.pollingEndpoint = self.camundaEndpoint + '/external-task'


    def run(self):
        print("Starting optimization")
        print(self.parameters)

        def decoyfunction(opt_parameters, *args):
            app.logger.info(opt_parameters[0])
            app.logger.info('publish' + str(opt_parameters))

            opt_parameters_array =[]
            for parameter in opt_parameters:
                opt_parameters_array.append(parameter)

            opt_parameters = opt_parameters_array


            # send response
            body = {
                "workerId": "optimization-service",
                "variables":
                    {"initialParameters": {"value": str(opt_parameters), "type": "String"}}
            }
            if self.return_address:
                app.logger.info(self.pollingEndpoint + '/' + self.return_address + '/complete' + ' body: ' +  str(body))
                response = requests.post(self.pollingEndpoint + '/' + self.return_address + '/complete',
                                     json=body)
                app.logger.info(response)

            # camunda_callback = requests.post(self.return_address,
            #                                  json={"corr_id": self.corr_id, "variables": {
            #                                          "parameters": str(opt_parameters)}})
            # app.logger.info("Callback returned status code: " + str(camunda_callback.status_code))
            return self.poll()


        if self.optimizer.lower() == 'spsa':
            spsa = SPSA(maxiter=200)
            res = spsa.optimize(len(self.parameters), decoyfunction, initial_point=self.parameters)
        else:
            res = optimize.minimize(decoyfunction, self.parameters, method=self.optimizer)
        print(res)

    def send_error(self,errorCode, externalTaskId):
        body = {
            "workerId": "KMeansInitializerService",
            "errorCode": errorCode
        }
        response = requests.post(self.pollingEndpoint + '/' + externalTaskId + '/bpmnError', json=body)
        print(response.status_code)

    def poll(self):
        while(True):
            app.logger.info('Polling for new external tasks at the Camunda engine with URL: {}'.format(self.pollingEndpoint))
            print('Polling for new external tasks at the Camunda engine with URL: ', self.pollingEndpoint)

            body = {
                "workerId": "optimization-service",
                "maxTasks": 1,
                "topics":
                    [{"topicName": self.topic,
                      "lockDuration": 100000000,
                      "variables": ["objValue"]
                      }]
            }

            try:
                response = requests.post(self.pollingEndpoint + '/fetchAndLock', json=body)
                if response.status_code == 200:
                    app.logger.info('in 200')
                    app.logger.info(response.json())
                    for externalTask in response.json():
                        app.logger.info('External task with ID for topic ' + str(externalTask.get('topicName')) + ': ' + str(
                            externalTask.get('activityId')))
                        self.return_address = externalTask.get('id')
                        variables = externalTask.get('variables')
                        if externalTask.get('topicName') == self.topic:
                            if ('objValue' in variables):
                               app.logger.info(variables)
                               return float(variables.get("objValue").get("value"))
            except Exception as e:
                print('Exception during polling!')
                print(e)
            time.sleep(5)

        # threading.Timer(3, self.poll).start()

    def download_data(self,url):
        response = urlopen(url)
        data = response.read().decode('utf-8')
        return str(data)



















