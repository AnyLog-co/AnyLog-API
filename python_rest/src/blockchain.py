import anylog_connector
import generic_get


def check_synchronizer(anylog_conn:anylog_connector.AnyLogConnector):
    """
    Check whether blockchain synchronizer is active
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog via REST
    :params:
        status:bool
    :return:
        True if blockchain sync is active
        False if not
    """
    status = False
    active_processes = generic_get.get_processes(anylog_conn=anylog_conn, json_format=False, view_help=False)
    if "Blockchain Sync" in active_processes and "Status" in active_processes["Blockchain Sync"]:
        if active_processes["Blockchain Sync"]["Status"] != "Not declared":
            status = True

    return status

def run_synchronizer(anylog_conn:anylog_connector.AnyLogConnector, source:str, time:str, dest:str, connection:str,
                     view_help:bool=False):
    """
    Initiate the blockchain sync process
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/background%20processes.md#blockchain-synchronizer
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog via REST
        source:str - the source of the metadata (blockchain or a Master Node)
        dest:str - The destination of the blockchain data such as a file (a local file) or a DBMS (a local DBMS).
        The connection information that is needed to retrieve the data. For a Master, the IP and Port of the master/ledger node
        time:str - the frequency of updates.
        view_help:bool - view help regarding command
    :params
        status:bool
        headers:dict - REST header information
        r:requests.model.Response - response from REST request
    :return:
        status
    """
    status = False
    headers = {
        "command": f"run blockchain sync where source={source} and time={time} and dest={dest} and connection={connection}",
        "User-Agent": "AnyLog/1.23"
    }

    if view_help is True:
        anylog_connector.view_help(headers["command"])
        return None

    r = anylog_conn.post(headers=headers)
    if r is None or int(r.status_code) != 200:
        status = False

    return status