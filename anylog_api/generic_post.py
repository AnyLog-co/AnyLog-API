from anylog_api.anylog_connector import AnyLogConnector
import anylog_api.anylog_connector_support as anylog_connector_support


def __generic_execute(anylog_conn:AnyLogConnector, headers:dict, view_help:bool=False, exception:bool=False):
    """
    Process POST command via REST
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        headers:dict - REST information
        view_help:bool - whether to execute HELP against command (prints to screen)
        print_output:bool - whether to print results from executed command
        exception:bool - whether to print exceptions
    :params:
        status:bool
    :return:
        status
    """
    status = False
    if view_help is True:
        anylog_connector_support.rest_help(anylog_conn=anylog_conn, command=headers['command'], exception=exception)
        status = True
    else:
        r, error = anylog_conn.get(headers=headers)
        if r is False and exception is True:
            anylog_connector_support.print_rest_error(call_type='GET', cmd=headers['command'], error=error)
        else:
            status = True

    return status


def reset_event_log(anylog_conn:AnyLogConnector, view_help:bool=False, destination:str=None, exception:bool=False):
    """
    Reset event log
    :command:
        reset event log
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        view_help:bool - whether to execute HELP against command (prints to screen)
        destination:str - remote machine IP and Port
        exception:bool - whether to print exceptions
    :params:
        status:bool - output from POST request
        headers:dict - REST informationheaders:dict - REST information
    :return:
        status
    """
    headers = {
        "command": "reset error log",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    status = __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, exception=exception)

    return status

def reset_error_log(anylog_conn:AnyLogConnector, view_help:bool=False, destination:str=None, exception:bool=False):
    """
    Reset error log
    :command:
        reset error log
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        view_help:bool - whether to execute HELP against command (prints to screen)
        destination:str - remote machine IP and Port
        exception:bool - whether to print exceptions
    :params:
        status:bool - output from POST request
        headers:dict - REST information
    :return:
        status
    """
    headers = {
        "command": "reset error log",
        "User-Agent": "AnyLog/1.23"
    }
    if destination is not None:
        headers['destination'] = destination

    status = __generic_execute(anylog_conn=anylog_conn, headers=headers, view_help=view_help, exception=exception)

    return status


def reset_query_status(anylog_conn:AnyLogConnector, view_help:bool=False, destination:str=None, exception:bool=False):
    """
    Reset query status
    :command:

    """