from anylog_api_py.anylog_connector import AnyLogConnector
from anylog_api_py.generic_post_cmd import declare_configs
from anylog_api_py.generic_get_cmd import get_dictionary
from utils_file_io import read_config_file


def __format_configs(anylog_confgis:dict)->dict:
    """
    convert anylog dict values into int if valid
    :args:
        anylog_configs:dict - variable dictionary with AnyLog
    :return:
        updated anylog_configs
    """
    for key in anylog_confgis:
        try:
            anylog_confgis[key] = int(anylog_confgis[key])
        except:
            pass
    return anylog_confgis


def set_params(anylog_connector:AnyLogConnector, config_file:str, exception:bool=False)->dict:
    """
    Given a configuration file,  store its content into the AnyLog dictionary and return complete dictionary
    :args:
        anylog_connector:AnyLogConnector - connection to AnyLog node
        config_file:str - configuration file with env variables to be set
        exception:bool - whether to print exceptions or not
    :params:
        status:bool
        file_configs:dict - configuration from file
        anylog_configs:dict - variable dictionary within AnyLog
    :return:
        anylog_configs
    """
    file_configs = read_config_file(config_file=config_file, exception=exception)

    # declare params in dictionary
    for key in file_configs:
        if file_configs[key] != "":
            status = declare_configs(anylog_conn=anylog_connector, key=key.lower(), value=file_configs[key], exception=exception)
        if status is False:
            print(f"Failed to set `{key}` to `{file_configs[key]}`")

    anylog_configs = get_dictionary(anylog_conn=anylog_connector, is_json=True, exception=exception)

    return __format_configs(anylog_configs)


