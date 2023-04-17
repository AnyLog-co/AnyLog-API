import anylog_connector


def set_license_key(anylog_conn:anylog_connector.AnyLogConnector, license_key:str, view_help:bool=False):
    """
    Set license key
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        license_key:str - license key
        view_help:bool - execute `help` against `set license`
    :params:
        status:bool
        headers:dict - REST header information
        r:requests.model.Response - response from REST request
    :return:
        None - if help
        False - if fails
        True - if succeed
    """
    status = True
    headers = {
        "command": f"set license where activation_key = {license_key}",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(headers)
        return None

    r = anylog_conn.post(headers=headers)
    if r is None or int(r.status_code) != 200:
        status = False

    return status