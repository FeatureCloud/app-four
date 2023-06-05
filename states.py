from FeatureCloud.app.engine.app import AppState, app_state, Role
import myapp
import utils


app_instance = myapp.MyApp()

if utils.is_centralized(myapp.APP_NAME):
    if utils.file_has_class('myapp.py', 'Centralized'):
        @app_state(name='initial', role=Role.BOTH)
        class InitialState(AppState):

            def register(self):
                self.register_transition('Centralized')

            def run(self):
                return 'Centralized'


        @app_state('Centralized')
        class Centralized(AppState):

            def register(self):
                self.register_transition('terminal')

            def run(self):
                app_instance.centralized()
                return 'terminal'
else:
    @app_state(name='initial', role=Role.BOTH)
    class InitialState(AppState):

        def register(self):
            self.register_transition('Local_Training')

        def run(self):
            data_to_broadcast = app_instance.load_data()
            self.broadcast_data(data_to_broadcast)
            return 'Local_Training'


    @app_state('Local_Training')
    class LocalTraining(AppState):

        def register(self):
            self.register_transition('Global_Aggregation', role=Role.COORDINATOR)
            self.register_transition('Local_Training', role=Role.PARTICIPANT)
            self.register_transition('Write_Results', role=Role.BOTH)

        def run(self):
            received_data = self.await_data()
            data_to_send = app_instance.local_training(global_parameters=received_data)
            # if self.data_to_send is None:
            #     raise NotImplementedError("Local_Training is expected to have some local parameters to share")
            self.send_data_to_coordinator(data_to_send, use_smpc=app_instance.config["use_smpc"])
            if self.last_round:
                return "Write_Results"
            if self.is_coordinator:
                return "Global_Aggregation"
            return "Local_Training"


    @app_state('Global_Aggregation')
    class GlobalAggregation(AppState):

        def register(self):
            self.register_transition('Local_Training', role=Role.COORDINATOR)

        def run(self):
            if self.use_smpc:
                local_data = self.aggregate_data(use_smpc=True)
            else:
                local_data = self.gather_data()
            data_to_broadcast = app_instance.global_aggregation(local_parameters=local_data)
            # if self.data_to_broadcast is None:
            #     raise NotImplementedError("Global_Aggregation is expected to have some local parameters to share")
            self.broadcast_data(data_to_broadcast)
            return 'Local_Training'


    @app_state('Write_Results')
    class WriteResults(AppState):

        def register(self):
            self.register_transition('terminal')

        def run(self):
            app_instance.write_results()
            return 'terminal'
