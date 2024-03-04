# URL: https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md
from anylog_api.anylog_connector import AnyLogConnector
import anylog_api.anylog_connector_support as anylog_connector_support

def __generic_execute(anylog_conn:AnyLogConnector, headers:dict, view_help:bool=False, print_output:bool=False, exception:bool=False):
    """
    Process GET command via REST
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        headers:dict - REST information
        view_help:bool - whether to execute HELP against command (prints to screen)
        print_output:bool - whether to print results from executed command
        exception:bool - whether to print exceptions
    :params:
        output - output from GET request
    :return:
        output
    """
    output = None

    if view_help is True:
        anylog_connector_support.rest_help(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            anylog_connector_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        elif not isinstance(r, bool):
            output = anylog_connector_support.extract_results(cmd=headers['command'], r=r, exception=exception)
        if print_output is True:
            print(output)
            output = None

    return output


def get_status(anylog_conn:AnyLogConnector, json_format:bool=False, view_help:bool=False, destination:str=None, print_output:bool=False, exception:bool=False):
    """
    Check status of node - Replies with the string 'running' if the node is active. Can be extended to include additional status information
    :command:
        get status
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        json_format:bool - return `get status` in JSON format
        view_help:bool - whether to execute HELP against command (prints to screen)
        print_output:bool - whether to print results from executed command
        destination:str - remote machine IP and Port
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        output from __generic_execute
    """
    headers = {
        "command": "get status",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers['destination'] = destination

    return __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)


def get_dictionary(anylog_conn:AnyLogConnector, json_format:bool=False, view_help:bool=False, destination:str=None, print_output:bool=False, exception:bool=False):
    """
    Get the declared variables with their assigned values.
    :command:
        get dictionary
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-dictionary-command
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        json_format:bool - return `get status` in JSON format
        view_help:bool - whether to execute HELP against command (prints to screen)
        destination:str - remote machine IP and Port
        print_output:bool - whether to print results from executed command
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        output from __generic_execute
    """
    headers = {
        "command": "get dictionary",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers['destination'] = destination

    return __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)


def get_hostname(anylog_conn:AnyLogConnector, view_help:bool=False, destination:str=None, print_output:bool=False, exception:bool=False):
    """
    Get name of host
    :command:
        get hostname
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        view_help:bool - whether to execute HELP against command (prints to screen)
        destination:str - remote machine IP and Port
        print_output:bool - whether to print results from executed command
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        output from __generic_execute
    """
    headers = {
        "command": "get hostname",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    return __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)


def get_processes(anylog_conn:AnyLogConnector, json_format:bool=False, view_help:bool=False, destination:str=None, print_output:bool=False, exception:bool=False):
    """
    check status of AnyLog services
    :command:
        get processes
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/monitoring%20nodes.md#the-get-processes-command
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        json_format:bool - return `get status` in JSON format
        view_help:bool - whether to execute HELP against command (prints to screen)
        print_output:bool - whether to print results from executed command
        destination:str - remote machine IP and Port
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        output from __generic_execute
    """
    headers = {
        "command": "get processes",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers['destination'] = destination

    return __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)


def get_connections(anylog_conn:AnyLogConnector, json_format:bool=False, view_help:bool=False, destination:str=None, print_output:bool=False, exception:bool=False):
    """
    check status of AnyLog services
    :command:
        Get the external connections to the node.
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        json_format:bool - return `get status` in JSON format
        view_help:bool - whether to execute HELP against command (prints to screen)
        print_output:bool - whether to print results from executed command
        destination:str - remote machine IP and Port
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        output from __generic_execute
    """
    headers = {
        "command": "get connections",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers['destination'] = destination

    return __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)


def get_scheduler(anylog_conn:AnyLogConnector, scheduler_id:int=None, view_help:bool=False, destination:str=None, print_output:bool=False, exception:bool=False):
    """
    Information on the scheduled tasks
    :command:
        get scheduler
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/alerts%20and%20monitoring.md#view-scheduled-commands
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        scheduler_id:int - optional ID for the scheduler
        view_help:bool - whether to execute HELP against command (prints to screen)
        print_output:bool - whether to print results from executed command
        destination:str - remote machine IP and Port
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        output from __generic_execute
    """
    headers = {
        "command": "get scheduler",
        "User-Agent": "AnyLog/1.23"
    }
    if scheduler_id is not None:
        headers['command'] += f" {scheduler_id}"
    if destination is not None:
        headers['destination'] = destination

    return __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)


def get_event_log(anylog_conn:AnyLogConnector, json_format:bool=False, view_help:bool=False, destination:str=None, print_output:bool=False, exception:bool=False):
    """
    Get log of events on the node
    :command:
        get event log
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/logging%20events.md#the-event-log
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        json_format:bool - return `get status` in JSON format
        view_help:bool - whether to execute HELP against command (prints to screen)
        print_output:bool - whether to print results from executed command
        destination:str - remote machine IP and Port
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        output from __generic_execute
    """
    headers = {
        "command": "get event log",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers['destination'] = destination

    return __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)


def get_error_log(anylog_conn:AnyLogConnector, json_format:bool=False, view_help:bool=False, destination:str=None, print_output:bool=False, exception:bool=False):
    """
    Get log of errors on the node
    :command:
        get error log
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/logging%20events.md#the-error-log
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        json_format:bool - return `get status` in JSON format
        view_help:bool - whether to execute HELP against command (prints to screen)
        print_output:bool - whether to print results from executed command
        destination:str - remote machine IP and Port
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        output from __generic_execute
    """
    headers = {
        "command": "get error log",
        "User-Agent": "AnyLog/1.23"
    }
    if json_format is True:
        headers['command'] += " where format=json"
    if destination is not None:
        headers['destination'] = destination

    return __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)


def get_echo_queue(anylog_conn:AnyLogConnector, view_help:bool=False, destination:str=None, print_output:bool=False, exception:bool=False):
    """
    Get log of errors on the node
    :command:
        get echo queue
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/logging%20events.md#the-error-log
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        json_format:bool - return `get status` in JSON format
        view_help:bool - whether to execute HELP against command (prints to screen)
        print_output:bool - whether to print results from executed command
        destination:str - remote machine IP and Port
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        output from __generic_execute
    """
    headers = {
        "command": "get echo queue",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    return __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)


def execute_test_network(anylog_conn:AnyLogConnector, view_help:bool=False, print_output:bool=False, exception:bool=False):
    """
    Send a command to a group of nodes in the network and organize the replies from all participating nodes.
    :command:
        test network
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/test%20commands.md#the-test-network-commands
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        json_format:bool - return `get status` in JSON format
        view_help:bool - whether to execute HELP against command (prints to screen)
        print_output:bool - whether to print results from executed command
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        output from __generic_execute
    """
    headers = {
        "command": "test network",
        "User-Agent": "AnyLog/1.23"
    }

    return __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)


def execute_test_node(anylog_conn:AnyLogConnector, view_help:bool=False, destination:str=None, print_output:bool=False, exception:bool=False):
    """
    Execute a test to validate the TCP connection, the REST connection and the local blockchain structure.
    :command:
        test node
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/test%20commands.md#test-node
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        json_format:bool - return `get status` in JSON format
        view_help:bool - whether to execute HELP against command (prints to screen)
        destination:str - remote machine IP and Port
        print_output:bool - whether to print results from executed command
        exception:bool - whether to print exceptions
    :params:
        headers:dict - REST information
    :return:
        output from __generic_execute
    """
    headers = {
        "command": "test node",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    return __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, print_output=print_output, exception=exception)