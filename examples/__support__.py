import argparse
import datetime
import dotenv
import os
import random
import time




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
        raise argparse.ArgumentTypeError(FileNotFoundError(error_msg))

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


def data_generator(db_name:str=None, table:str=None, total_rows:int=10, wait_time:int=0.5)->list:
    """
    Generate data to be inserted
    :args:
        db_name:str - logical database name
        table:str - physical table name
        total_rows:int - number of rows to insert
        wait_time:float - wait time between each row
    :params:
        rows:list - of rows to insert
        row:dict - generated row to insert
    :return:
        rows
    """
    rows = []

    for i in range(total_rows):
        row = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "value": round(random.random() * 100, 2)
        }
        if db_name:
            row['dbms'] = db_name
        if table:
            row['table'] = table
        rows.append(row)
        if i < total_rows - 1:
            time.sleep(wait_time)

    return rows