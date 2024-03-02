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

    return output