import ast
from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.generic_get_calls import get_dictionary
from anylog_api_py.generic_post_calls import add_dict_params
from file_io import read_configs


def setup_configurations(anylog_conn:AnyLogConnector, config_file:str, exception:bool=False)->dict:
    """
    Setup configuration for AnyLog node
    :args:
        anylog_conn:AnyLogConnector - connection to AnyLog
        config_file:str - configuration file
        exception:bool - whether to print exceptions
    :params
        node_configs:dict - AnyLog node configurations
        file_configs:dict - configurations from file
    :return:
        node_configs
    """
    node_configs = {}
    # read configuration file
    file_configs = read_configs(config_file=config_file, exception=exception)

    # add configurations to AnyLog dictionary
    if file_configs != {}:
        add_dict_params(anylog_conn=anylog_conn, configs=file_configs, exception=exception)

    # read all configurations in AnyLog dictionary
    node_configs = get_dictionary(anylog_conn=anylog_conn, json_format=True, remote_destination=None, view_help=False,
                                  exception=exception)

    # update merge missing configs (if any) with nodes
    for config in file_configs:
        if config.lower() not in node_configs:
            if not isinstance(file_configs[config], str ):
                node_configs[config.lower()] = file_configs[config]
            elif len(file_configs[config].strip()) > 0:
                node_configs[config.lower()] = file_configs[config].strip()

    # convert to proper value (ex. '3' to 3)
    for config in node_configs:
        try:
            node_configs[config] = ast.literal_eval(node_configs[config])
        except SyntaxError:
            pass

    return node_configs