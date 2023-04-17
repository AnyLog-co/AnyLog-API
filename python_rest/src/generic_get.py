import anylog_connector


def get_status(anylog_conn:anylog_connector.AnyLogConnector, json_format:bool=True, view_help:bool=False):
    """
    Check whether node is running or not
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog node
        json_format:bool - get result in JSON format
        view_help:bool - execute `help` against `get status`
    :params:
        status:bool
        headers:dict - REST header information
        output - REST result
    :return:
        None - help
        False - failed
        True - success
    """
    status = False
    headers = {
        "command": "get status",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(headers)
        return None

    if json_format is True:
        headers["command"] += " where format=json"

    output = anylog_conn.get(headers=headers)
    if output is not None and 'Status' in output and "running" in  output["Status"] and "not" not in output["Status"]:
        status = True

    return status


def check_license(anylog_conn:anylog_connector.AnyLogConnector, view_help:bool=False):
    """
    Check whether license key is active or not
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog node
        view_help:bool - execute `help` against `get status`
    :params:
        status:bool
        headers:dict - REST header information
        output - REST result
    :return:
        None - help
        False - failed
        True - success
    """
    status = True
    headers = {
        "command": "get license",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(headers)
        return None

    output = anylog_conn.get(headers=headers)

    if "Missing Valid AnyLog License Key" in output:
        status = False

    return status


def get_dictionary(anylog_conn:anylog_connector.AnyLogConnector, json_format:bool=True, view_help:bool=False):
    """
    Extract dictionary from AnyLog
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - Connection to AnyLog node
        json_format:bool - get result in JSON format
        view_help:bool - execute `help` against `get dictionary`
    :params:
        status:bool
        headers:dict - REST header information
    :return:
        AnyLog dictionary
    """
    status = False
    headers = {
        "command": "get dictionary",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(headers)
        return None

    if json_format is True:
        headers["command"] += " where format=json"

    return anylog_conn.get(headers=headers)


