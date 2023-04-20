import anylog_connector
from generic_get import get_cmd
from generic_post import post_cmd


def check_connections(anylog_conn:anylog_connector, destination:str=None, execute_cmd:bool=True, view_help:bool=False):
    """
    Get connection information
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/anylog%20commands.md#get-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector
        execute_cmd:bool - execute a given command, if False, then return command
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - whether to print help information
    :params:
        headers:dict - REST header information
    :return:
        output from GET request, None if view help
    """
    command = "get connections"
    return get_cmd(anylog_conn=anylog_conn, cmd=command, destination=destination, execute_cmd=execute_cmd,
                   view_help=view_help)


def configure_connection(anylog_conn:anylog_connector.AnyLogConnector, protocol:str, external_ip:str, local_ip:str,
                         port:int, external_port:int=None, bind:bool=False, threads:int=3, timeout:int=30,
                         destination:str=None, execute_cmd:bool=True, view_help:str=True, exception:bool=False):
    """
    Configure connectivity to tcp, rest or broker on an AnyLog Node
    :url:
        TCP: https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#the-tcp-server-process
        REST: https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#rest-requests
        Broker: https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#message-broker
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog node
        protocol:str - connection type
            tcp
            rest
            (message) broker
        external_ip:str - external IP address
        local_ip:str - local or internal IP address (could be used as overlay IP)
        port:int - default port to connect to the node
        external_port:int - port to be used when accessing from the outside
        bind:bool - whether to bind the connection
        threads:int - number of thread on the given process
        timeout:int - default REST timeout (in seconds)
        execute_cmd:bool - execute a given command, if False, then return command
        destination:str - destination to send request against (ie `run client`)
        execute_cmd:bool - execute a given command, if False, then return command
        view_help:bool - whether to print help information
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
    :return:
        None - print information about command
        if execute_cmd is False, then return command
        False - fails, either due to invalid protocol or command simply failed
        True - success
    """
    if protocol == "tcp":
        command = "run tcp server where "
    elif protocol == "rest":
        command = "run rest server where "
    elif protocol == "broker" or protocol == "message broker":
        command = "run message broker where "
    else:
        if exception is True:
            print(f"Invalid protocol {protocol}, instead use: tcp, rest or (message) broker")
        return False

    command += (f"external_ip={external_ip} and external_ip={external_port} and "
               +f"internal_ip={local_ip} and internal_ip={port} "
               +f"and bind=false and threads={threads}")
    if external_port is None:
        command.replace(external_port, port)
    if bind is True:
        command.replace("bind=false", "bind=true")
    if protocol == "rest":
        command += f" and timeout={timeout}"

    return post_cmd(anylog_conn=anylog_conn, command=command, payload=None, destination=destination,
                    execute_cmd=execute_cmd, view_help=view_help)

