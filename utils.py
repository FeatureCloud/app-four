import os
import bios
import ast
import abc

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


def get_root_dir(input_dir=True):
    if input_dir:
        if is_native():
            return ""
        return "/mnt/input"
    if is_native():
        return "results"
    return "/mnt/output"

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
    @abc.abstractmethod
    def load_data(self, config):
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
    def centralized(self, config):
        pass
