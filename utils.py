"""
    FeatureCloud Four States App  Template
    Copyright 2023 Mohammad Bakhtiari. All Rights Reserved.
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import os
import shutil
import bios
import ast
import abc
from time import sleep
from FeatureCloud.app.engine.app import App, app
import states
from bottle import Bottle
from FeatureCloud.app.api.http_ctrl import api_server
from FeatureCloud.app.api.http_web import web_server
import yaml


def print_configurations(data):
    print("\t\t\tConfigurations...")
    print("\n****************************************\n")
    formatted_yaml = yaml.dump(data, indent=2)
    print(formatted_yaml)
    print("\n****************************************\n")


def is_native():
    path_prefix = os.getenv("PATH_PREFIX")
    if path_prefix:
        return False
    return True


CONFIG_FILE = "config.yml"


def read_config():
    file_path = CONFIG_FILE
    if not is_native():
        file_path = f"/mnt/input/{CONFIG_FILE}"
    return bios.read(file_path)


def is_simulation(app_name):
    config = read_config()[app_name]
    return config.get('simulation', None) is not None


def get_root_dir(input_dir=True, simulation_dir=None):
    simulation_dir = "/" + simulation_dir if simulation_dir else ''

    if input_dir:
        if is_native():
            return f".{simulation_dir}"
        return f"/mnt/input{simulation_dir}"
    if is_native():
        return f"./results{simulation_dir}"
    return f"/mnt/output{simulation_dir}"


def is_centralized(app_name):
    config = read_config()[app_name]
    return config.get('centralized', False)


def file_has_class(file_path, class_name):
    with open(file_path, 'r') as file:
        source_code = file.read()

    try:
        parsed = ast.parse(source_code)
    except SyntaxError:
        return False

    for node in ast.walk(parsed):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return True

    return False


class FeatureCLoudApp(abc.ABC):
    def __init__(self, config, simulation_dir=None):
        self.config = config
        self.input_root_dir = get_root_dir(simulation_dir=simulation_dir)
        self.output_root_dir = get_root_dir(input_dir=False, simulation_dir=simulation_dir)
        if os.path.exists(self.output_root_dir):
            shutil.rmtree(self.output_root_dir)
        os.makedirs(self.output_root_dir)

        self.last_round = False

    @abc.abstractmethod
    def load_data(self):
        """

        Returns
        -------
        data_to_broadcast: list
#             Values or messages from coordinator to all client
        """

    @abc.abstractmethod
    def local_training(self, global_parameters):
        """

        Parameters
        ----------
        global_parameters

        Returns
        -------

        """

    @abc.abstractmethod
    def global_aggregation(self, local_parameters):
        """

        Parameters
        ----------
        local_parameters

        Returns
        -------

        """

    @abc.abstractmethod
    def write_results(self):
        """

        Returns
        -------

        """

    @abc.abstractmethod
    def centralized(self):
        pass


def run_client(app, client_id, clients_ids, coordinator_role, shared_memory):
    app.register()
    app.handle_setup(client_id=client_id,
                     coordinator=coordinator_role,
                     clients=clients_ids)
    app.shared_memory = shared_memory


class Controller:
    def __init__(self, clients_id):
        self.clients = {id.strip(): [] for id in clients_id}

    def register(self, client, app, coordinator):
        app.register()
        app.handle_setup(client_id=client,
                         coordinator=coordinator,
                         clients=list(self.clients.keys()))
        self.clients[client] = app

    def run(self):
        while True:
            for client in self.clients:
                if self.data_available(client):
                    data, dest_client = self.check_outbound(client)
                    if dest_client:
                        print("send_to_participant")
                        self.set_inbound(data, source_client=client, dest_client=dest_client)
                    else:
                        if self.clients[client].coordinator:
                            # broadcast
                            print("broadcast", list(self.clients.keys())[1:])
                            for dest_client in list(self.clients.keys())[1:]:
                                self.set_inbound(data, source_client=client, dest_client=dest_client)
                        else:
                            print("send_to_coordinator")
                            self.set_inbound(data, source_client=client, dest_client=list(self.clients.keys())[0])

            sleep(1)
            if self.finished():
                break

    def check_outbound(self, client):
        dest = self.status(client)['destination']

        data = self.clients[client].handle_outgoing()
        return data, dest

    def set_inbound(self, data, source_client, dest_client):
        self.clients[dest_client].handle_incoming(data, source_client)

    def finished(self):
        finished = [self.status(app)['finished'] for app in self.clients]
        return all(finished)

    def status(self, client):
        app = self.clients[client]
        client_status = {
            'available': app.status_available,
            'finished': app.status_finished,
            'message': app.status_message if app.status_message else (
                app.current_state.name if app.current_state else None),
            'progress': app.status_progress,
            'state': app.status_state,
            'destination': app.status_destination,
            'smpc': app.status_smpc,
        }
        return client_status

    def data_available(self, client):
        return self.status(client)['available']


def simulate(config, app_name, MyApp):
    print(f"Simulated: {config['simulation']}")
    clients_ids = [id.strip() for id in config['simulation']['clients'].split(',')]
    clients_dirs = config['simulation']['clients_dir'].split(',')
    simulation_dir = config['simulation'].get('dir', None)
    if simulation_dir:
        clients_dirs = [f"{simulation_dir}/{d}" for d in clients_dirs]
    controller = Controller(clients_ids)
    for i, (client_id, client_dir) in enumerate(zip(clients_ids, clients_dirs)):
        app = App()
        states.create_client(
            MyApp(config=read_config()[app_name],
                  simulation_dir=client_dir)
            , app
        )
        controller.register(client_id, app, coordinator=i == 0)
    controller.run()


def centralized(app_class, app_name):
    config = read_config()[app_name]
    print(f"centralized: {config['centralized']}")
    general_app_instance = App()
    states.create_client(
        app_class(
            config=config,
            simulation_dir=config['centralized'].get('data_dir', None)
        ), general_app_instance, centralized=True
    )
    general_app_instance.register()
    general_app_instance.handle_setup(client_id='1', coordinator=True, clients=['1'])


def federated(app_class, app_name):
    my_app = app_class(read_config()[app_name])
    states.generate_federated_states(target_app_instance=my_app)
    app.register()
    server = Bottle()
    server.mount('/api', api_server)
    server.mount('/web', web_server)
    server.run(host='localhost', port=5000)
