"""
Tips:
1. Do not rename the MyApp class and its five methods!
2. Return values of load_data, local_training, and global_aggregation methods will be communicated!
3. Return values of write_results will be discarded!
4. App supports five scenarios:
    * Native:
        - Centralized
        - Simulation of federated: No SMPC support
    * Containerized:
        - Centralized
        - Simulation of federated: No SMPC support
        - Federated
5. Containerized federated settings will be used in workflows for real world- collaboration
6. APP_NAME is case-sensitive and should contain the name of the app as a string and match the name of the config file
7. The config file should always named as `config.yml`
8. file structure:
    * Native
        - Centralized:
            data_dir to a directory containing all files for centralized training
        - Simulation:

"""

import utils

APP_NAME = "fc_example_config"


class MyApp(utils.FeatureCLoudApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load_data(self, config):
        pass

    def local_training(self, global_parameters):
        pass

    def global_aggregation(self, local_parameters):
        pass

    def write_results(self):
        pass

    def centralized(self, config):
        pass

