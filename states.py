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

from FeatureCloud.app.engine.app import AppState, app_state, Role


def create_client(target_app_instance, general_app_instance, centralized=False):
    if centralized:
        return generate_centralized_states(general_app_instance, target_app_instance)
    return generate_federated_states(target_app_instance, general_app_instance)


def generate_federated_states(target_app_instance, general_app_instance=None):
    @app_state(name='initial', role=Role.BOTH, app_instance=general_app_instance)
    class InitialState(AppState):
        def register(self):
            self.register_transition('Local_Training')

        def run(self):
            data_to_broadcast = target_app_instance.load_data()
            if self.is_coordinator:
                self.broadcast_data(data_to_broadcast)

            return 'Local_Training'

    @app_state('Local_Training', app_instance=general_app_instance)
    class LocalTraining(AppState):

        def register(self):
            self.register_transition('Global_Aggregation', role=Role.COORDINATOR)
            self.register_transition('Local_Training', role=Role.PARTICIPANT)
            self.register_transition('Write_Results', role=Role.BOTH)

        def run(self):
            received_data = self.await_data()
            received_data = received_data if received_data else None
            data_to_send = target_app_instance.local_training(global_parameters=received_data)
            if data_to_send:
                self.send_data_to_coordinator(data_to_send,
                                              use_smpc=target_app_instance.config["use_smpc"])
            if target_app_instance.last_round:
                return "Write_Results"
            if self.is_coordinator:
                return "Global_Aggregation"
            return "Local_Training"

    @app_state('Global_Aggregation', app_instance=general_app_instance)
    class GlobalAggregation(AppState):

        def register(self):
            self.register_transition('Local_Training', role=Role.COORDINATOR)

        def run(self):
            if target_app_instance.config['use_smpc']:
                local_data = self.aggregate_data()
            else:
                local_data = self.gather_data()
            data_to_broadcast = target_app_instance.global_aggregation(local_parameters=local_data)
            self.broadcast_data(data_to_broadcast)
            return 'Local_Training'

    @app_state('Write_Results', app_instance=general_app_instance)
    class WriteResults(AppState):

        def register(self):
            self.register_transition('terminal')

        def run(self):
            target_app_instance.write_results()
            return 'terminal'

    return general_app_instance


def generate_centralized_states(general_app_instance, target_app_instance):
    @app_state(name='initial', role=Role.BOTH, app_instance=general_app_instance)
    class InitialState(AppState):

        def register(self):
            self.register_transition('Centralized')

        def run(self):
            return 'Centralized'

    @app_state('Centralized', app_instance=general_app_instance)
    class Centralized(AppState):

        def register(self):
            self.register_transition('terminal')

        def run(self):
            target_app_instance.centralized()
            return 'terminal'

    return general_app_instance
