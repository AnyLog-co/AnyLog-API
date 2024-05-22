import argparse
import dotenv
import os.path
import re


def check_conn(conn:str)->dict:
    """
    Check whether configurations are declared properly
    :args:
        conn:str - user input for connection information
    :params:
        rest_conn:dict - REST connection
        error_msg:str - error message (used for raise)
        auth:tuple - authentication informataion
        pattern:re.compile - compile to chck IP:PORT
    :raise:
        if err_msg != ""
    :return:
        rest_conns
    """
    rest_conns = {}
    error_msg = ""
    auth = None
    pattern = re.compile(
        r'^'  # Start of string
        r'((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'  # Match the first three octets
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'  # Match the fourth octet
        r':'  # Match the colon
        r'([0-9]{1,5})'  # Match the port number (1 to 5 digits)
        r'$'  # End of string
    )

    if '@' in conn:
        auth, conn = conn.split('@')
    if not pattern.fullmatch(conn):
        error_msg += f"\n\tInvalid connection IP:PORT value {conn}. Expected part: 127.0.0.1:32048"
    else:
        rest_conns[conn] = auth
    if auth is not None and ":" not in auth:
        error_msg += f"\n\tInvalid authentication information value {auth}. Expected part: user:password"
    elif auth is not None:
        rest_conns[conn] = tuple(auth.split(":"))
    if error_msg:
        raise argparse.ArgumentTypeError(f"Invalid Connection format. Expected format: user:password@IP:PORT {error_msg}")

    return rest_conns

def check_configs(config_files:str):
    """
    Check configuration file(s)
    :args:
        config_files:str - user input configs
    :params:
        configs:list - config_files as a list
        error_msg:str - error message (used for raise)
        :raise:
        if err_msg != ""
    :return:
        config_files
    """
    configs = []
    error_msg = ""
    for config in config_files.split(","):
        full_path = os.path.expanduser(os.path.expandvars(config))
        if not os.path.isfile(full_path):
            error_msg += f"Missing config file {full_path}\n"
        else:
            configs.append(full_path)
    if error_msg != "":
        raise argparse.ArgumentTypeError(error_msg)

    return configs


def read_configs(config_file:str, exception:bool=False)->dict:
    """
    Read configuration files
    :args:
        config_file:str - configuration file to read
        exception: whether to print exceptions
    :params:
        configs:dict - output from file
    :return:
        configs
    """
    configs = {}
    if isinstance(config_file, list):
        for config in config_file:
            output =   read_configs(config_file=config, exception=exception)
            configs = {**configs, **output}
    else:
        try:
           configs = dotenv.dotenv_values(config_file)
        except Exception as error:
            if exception is True:
                print(f"Failed to read config file {config_file} (Error: {error})")
    if len(configs) > 0: # convert to lower case keys
        return {key.lower(): value for key, value in configs.items()}
    return configs
