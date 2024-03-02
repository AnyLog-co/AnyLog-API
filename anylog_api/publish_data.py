# URL:
from anylog_api.anylog_connector import AnyLogConnector
import anylog_api.anylog_connector_support as anylog_connector_support


def send_data_via_put(anylog_conn:AnyLogConnector, payload:str, db_name:str, table_name:str, exception:bool=False):
    """
    Send data into AnyLog via PUT
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#using-a-put-command
    :sample data:
    {
        "timestamp": "2023-01-04T10:15:32.245185Z",
        "value": "31.415923458"
    }
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        payload:str - JSON serialized content to store into AnyLog
        db_name:str - database to store data into
        table_name:str - table to store data into
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:str - REST header information
        r - results from POST command
        error:str - error (code) if POST fails
    :return:
        status
    """
    headers = {
        'type': 'json',
        'dbms': db_name,
        'table': table_name,
        'mode': 'streaming',
        'Content-Type': 'text/plain'
    }

    r, error = anylog_conn.put(headers=headers, payload=payload)

    status = r
    if r is False and exception is True:
        anylog_connector_support.print_rest_error(call_type='PUT', cmd='data', error=error)

    return status

def send_data_via_post(anylog_conn:AnyLogConnector, payload:str, topic:str, exception:bool=False):
    """
    Send data into AnyLog via POST - make sure there's a running message client to receive content coming via POST
    :URL:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#using-a-post-command
    :sample data:
    {
        "db_name": "test",
        "table": "sample_data"
        "timestamp": "2023-01-04T10:15:32.245185Z",
        "value": "31.415923458"
    }
    :args:
        anylog_connector:AnylogConnector - connection to AnyLog node
        payload:str - JSON serialized content to store into AnyLog
        topic:str - messagge client topic to accept data against 
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:str - REST header information
        r - results from POST command
        error:str - error (code) if POST fails
    :return:
        status
    """
    headers = {
        'command': 'data',
        'topic': topic,
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }

    r, error = anylog_conn.post(headers=headers, payload=payload)

    status = r
    if r is False and exception is True:
        anylog_connector_support.print_rest_error(call_type='POST', cmd='data', error=error)

    return status


