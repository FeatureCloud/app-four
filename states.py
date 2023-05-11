"""
Tips:
1. Do not rename the states!
2. Return values of 'run' method will be discarded!
3. Do not define any arguments for run method!
4. Do not rename predefined attributes in classes
5. Do not use predefined attributes in classes for unrelated purposes
"""

INPUT_DIR = "/mnt/input"
OUTPUT_DIR = "/mnt/output"
CONFIG_FILE = "/mnt/input/config.yml"


class InitialState:
    """
    Attributes:
        data_to_broadcast: list
            Values or messages from coordinator to all client
    """

    def __init__(self):
        self.data_to_broadcast = None

    def run(self):
        pass


class LocalTraining:
    """
    Attributes:
        received_data: list
            Values or messages from coordinator to all client
        data_to_send: list
            Local parameters to share with the coordinator
        last_round: bool
            if True, the training loop is over, i.e., go to WriteResults!
        use_smpc: bool
            Use SMPC if True

    """

    def __init__(self):
        self.received_data = None
        self.data_to_send = None
        self.use_smpc = False
        self.last_round = None

    def run(self):
        pass


class GlobalAggregation:
    """
    Attributes:
        local_data: list
            received local parameters
        use_smpc: bool
            If True, local_data contains aggregated data from SMPC
            If False, local_data contains all clients' data
        data_to_broadcast: list
            Values or messages from coordinator to all client

    """

    def __init__(self):
        self.local_data = None
        self.use_smpc = False
        self.data_to_broadcast = None

    def run(self):
        pass


class WriteResults:
    """
    Attributes:

    """

    def __init__(self):
        pass

    def run(self):
        pass
