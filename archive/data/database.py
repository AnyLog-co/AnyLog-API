import anylog_api.anylog_connector as anylog_connector
from anylog_api.__support__ import add_conditions
from anylog_api.anylog_connector_support import execute_publish_cmd
from anylog_api.anylog_connector_support import extract_get_results
from anylog_api.generic.get import get_help


def connect_dbms(conn:anylog_connector.AnyLogConnector, db_name:str, db_type:str='sqlite', host:str=None, port:int=None,
                 user:str=None, password:str=None, memory:bool=False, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
    """
    Connect to logical database
    :args:
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database name
        db_type:str - physical database type
        host:str - database IP
        port:str - database Port
        user:str - user associated with database
        password:str - password associated with database
        memory:bool - run in memory
        destination:str - execute command remotely
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    """
    status = None
    headers = {
        "command": f"connect dbms {db_name}",
        "User-Agent": "AnyLog/1.23"
    }
    add_conditions(headers, type=db_type, ip=host, port=port, user=user, password=password)
    if memory is True and db_name == 'sqlite':
        add_conditions(headers, type=db_type, ip=host, port=port, user=user, password=password, memory='true')

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def disconnect_dbms(conn:anylog_connector.AnyLogConnector, db_name:str, destination:str=None, view_help:bool=False,
                    return_cmd:bool=False, exception:bool=False):
    """
    Disconnect to logical database
    :args:
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database name
        destination:str - execute command remotely
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    :params:
        status:bool
        headers:dict - REST headers
    :return;
        status
    """
    headers = {
        "command": f"disconnect dbms {db_name}",
        "User-Agent": "AnyLog/1.23"
    }

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        return headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def drop_dbms(conn:anylog_connector.AnyLogConnector, db_name:str, db_type:str='sqlite', host:str=None, port:int=None,
                 user:str=None, password:str=None, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
    """
    Disconnect logical database
    :args:
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database name
        db_type:str - physical database type
        host:str - database IP
        port:str - database Port
        user:str - user associated with database
        password:str - password associated with database
        memory:bool - run in memory
        destination:str - execute command remotely
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    """
    status = None
    headers = {
        "command": f"drop dbms {db_name} from {db_type}",
        "User-Agent": "AnyLog/1.23"
    }
    add_conditions(headers, ip=host, port=port, user=user, password=password)

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        status = headers['command']
    elif view_help is False:
        status = execute_publish_cmd(conn=conn, cmd='post', headers=headers, payload=None, exception=exception)

    return status


def get_databases(conn:anylog_connector.AnyLogConnector, json_format:bool=False, destination:str=None,
                  view_help:bool=False, return_cmd:bool=False, exception:bool=False):
    """
    Get list of databases
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/sql%20setup.md#the-get-databases-command
    :args:
        conn:AnyLogConnector - connection to AnyLog
        json_format:bool - whether to get results in JSON dictionary
        destination:str - execute command remotely
        view_help:bool - whether to view help for command
        exception:bool - whether to print error messages
    :params:
        output - results from REST request
        headers:dict - REST header requests
        r:request.get, error:str - REST request results
    :return:
        if success returns content (output), else None
    """
    output = None
    headers = {
        'command': 'get databases',
        'User-Agent': 'AnyLog/1.23'
    }

    if json_format is True:
        add_conditions(headers, format="json")

    if destination is not None:
        headers['destination'] = destination

    if view_help is True:
        get_help(conn=conn, cmd=headers['command'], exception=exception)
    if return_cmd is True:
        output = headers['command']
    elif view_help is False:
        output = extract_get_results(conn=conn, headers=headers, exception=exception)

    return output


def check_db_exists(conn:anylog_connector.AnyLogConnector, db_name:str, destination:str=None, view_help:bool=False,
                    exception:bool=False):
    """
    check if database exists
    :args:
        conn:AnyLogConnector - connection to AnyLog
        db_name:str - logical database to view
        view_help:bool - whether to print help info for AnyLog command
        destination;bool - execute command remotely
        exception:bool - whether to print error messages
    :params:
        status:bool
        output:str - content from `get databases` request
    :return:
        exists True
        else False
    """
    status = False

    output = get_databases(conn=conn, json_format=True, view_help=view_help, destination=destination, exception=exception)
    if 'No DBMS connections found' not in output and output is not None:
        if db_name in list(output.keys()):
            status = True

    return status




