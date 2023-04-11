import dotenv
import os


def __create_file(file_path:str, exception:bool=False)->(str, bool):
    """
    create a new file if DNE
    :args:
        file_path:str - file path
        exception:bool - whether to print exceptions
    :params:
        status:bool
        full_path:str - full path of file_path
    :return:
        full_path, status
    """
    status = True
    full_path = os.path.expanduser(os.path.expandvars(file_path))
    if not os.path.isfile(full_path):
        try:
            open(full_path, 'w').close()
        except Exception as error:
            status = False
            if exception is True:
                print(f'Failed to create file {file_path} (Error: {error})')

    return full_path, status


def __read_dotenv(config_file: str, exception: bool = False) -> dict:
    """
    Read configs from .env file
    :args:
        config_file:str - .env file to read configs from
        exception:bool - whether to print exceptions
    :params:
        configs:dict - configs read from .env file
    :return:
        configs
    """
    configs = {}

    try:
        configs = dict(dotenv.dotenv_values(config_file))
    except Exception as error:
        if exception is True:
            print(f'Failed to read configs from {config_file} (Error: {error})')

    return configs


def __lower_case(configs:dict):
    """
    Convert configuration to lower case
    :args:
        configs:dict - configurations to convert to lower case
    :return:
       configs with lower case keys
    """
    return {key.lower(): value for key, value in configs.items()}


def generic_write(file_path:str, content:str, exception:bool=False)->bool:
    """
    Given a file path and content (string) write it to file
    :args:
        file_path:str - file to write into
        content:str - content to write
        exception:bool - whether to print exception
    :params:
        status:bool
    """
    file_path, status = __create_file(file_path=file_path, exception=exception)

    if status is True:
        try:
            with open(file_path, 'a') as f:
                try:
                    f.write(content)
                except Exception as error:
                    status = False
                    if exception is True:
                        print(f'Failed to write content in file {file_path} (Error: {error})')
        except Exception as error:
            status = False
            if exception is True:
                print(f'Failed to open file {file_path} to append content (Error: {error})')

    return status


def read_configs(config_file:str, exception:bool=False)->dict:
    """
    Given a configuration file, extract configurations
    :supports:
        - .env
        - .yml (to be developed)
    :args:
        config_file:str - YAML file
        exception:bool - whether to write exception
    :params:
        file_extension:str - file extension
        configs:dict - content in YAML file
    :return:
        configs
    """
    full_path = os.path.expanduser(os.path.expandvars(config_file))
    file_extension = config_file.rsplit('.', 1)[-1]
    configs = {}

    if os.path.isfile(full_path):
        if file_extension == 'env':
            configs = __read_dotenv(config_file=full_path, exception=exception)
        elif file_extension in ['.yml', '.yaml']:
            pass
        elif exception is True:
            print(f'Invalid extension type: {file_extension}')
    elif exception is True:
        print(f"Failed to locate configuration file: {config_file}")

    if configs != {}:
        configs = __lower_case(configs=configs)

    return configs
