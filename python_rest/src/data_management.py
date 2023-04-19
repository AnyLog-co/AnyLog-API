import anylog_connector


def post_data(anylog_conn:anylog_connector.AnyLogConnector, topic:str, payload:str):
    """
    Publish data into AnyLog via POST command
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#using-a-post-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        topic:str - topic to publish data against
        payload:str - JSON string of data to publish
    :params:
        status:bool
        headers:dict - REST header information
        r:results.model.Response - request response
    :return:
        status
    """
    status = True
    headers = {
        'command': 'data',
        'topic': topic,
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }

    r = anylog_conn.post(headers=headers, payload=payload)
    if r is None or int(r.status_code) != 200:
        status = False

    return status


def put_data(anylog_conn:anylog_connector.AnyLogConnector, payload:str, db_name:str, table_name:str, mode:str="streaming",
             exception:bool=False):
    """
    Store data into AnyLog via PUT
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/adding%20data.md#using-a-put-command
    :args:
        anylog_conn:anylog_connector.AnyLogConnector - connection to AnyLog
        payload:str - JSON string of data to publish
        db_name:str - logical database to store data
        table_name:str - table to store data in
        mode:streaming - format to ingest data (default: streaming)
            file - The body of the message is JSON data. Database load (on an Operator Node) and data send
                   (on a Publisher Node) are with no wait. File mode is the default behaviour.
            streaming - The body of the message is JSON data that is buffered in the node. Database load
                        (on an Operator Node) and data send (on a Publisher Node) are based on time and volume
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST headers
    :return:
       status
    """
    status = True
    headers = {
        'type': 'json',
        'dbms': db_name,
        'table': table_name,
        'Content-Type': 'text/plain'
    }

    if mode in ["streaming", "file"]:
        headers["mode"] = mode
    else:
        status = False
        if exception is True:
            print(f"Invalid processing mode {mode}. Supported modes - streaming & file.")

    if status is True:
        r = anylog_conn.put(headers=headers, payload=payload)
        if r is None or int(r.status_code) != 200:
            status = False

    return status
