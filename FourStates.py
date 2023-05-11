from FeatureCloud.app.engine.app import AppState, app_state, Role
import states


@app_state(name='initial', role=Role.BOTH)
class InitialState(AppState, states.InitialState):

    def register(self):
        self.register_transition('Local_Training')

    def run(self):
        super(InitialState, self).run()
        data_to_broadcast = None if self.data_to_broadcast is None else self.data_to_broadcast
        self.broadcast_data(data_to_broadcast)
        return 'Local_Training'


@app_state('Local_Training')
class LocalTraining(AppState, states.LocalTraining):

    def register(self):
        self.register_transition('Global_Aggregation', role=Role.COORDINATOR)
        self.register_transition('Local_Training', role=Role.PARTICIPANT)
        self.register_transition('Write_Results', role=Role.BOTH)

    def run(self):
        self.received_data = self.await_data()
        super(LocalTraining, self).run()
        if self.data_to_send is None:
            raise NotImplementedError("Local_Training is expected to have some local parameters to share")
        self.send_data_to_coordinator(self.data_to_send, use_smpc=self.use_smpc)
        if self.last_round:
            return "Write_Results"
        if self.is_coordinator:
            return "Global_Aggregation"
        return "Local_Training"


@app_state('Global_Aggregation')
class GlobalAggregation(AppState, states.GlobalAggregation):

    def register(self):
        self.register_transition('Local_Training', role=Role.COORDINATOR)

    def run(self):
        if self.use_smpc:
            self.local_data = self.aggregate_data(use_smpc=True)
        else:
            self.local_data = self.gather_data()
        super(GlobalAggregation, self).run()
        if self.data_to_broadcast is None:
            raise NotImplementedError("Global_Aggregation is expected to have some local parameters to share")
        self.broadcast_data(self.data_to_broadcast)
        return 'Local_Training'


@app_state('Write_Results')
class WriteResults(AppState, states.WriteResults):

    def register(self):
        self.register_transition('terminal')

    def run(self):
        super(WriteResults, self).run()
        return 'terminal'
