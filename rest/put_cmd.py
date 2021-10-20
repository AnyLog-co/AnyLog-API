import json

import import_packages
import_packages.import_dirs()

import anylog_api
import other_cmd


def put_data(conn:anylog_api.AnyLogConnect, dbms:str, table:str, payloads:list, mode:str='streaming', exception:bool=False)->bool:
    """
    Execute PUT data against against AnyLog
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        dbms:str - database name
        table:str - table name
        payloads:str - payloads to send data to AnyLog
        mode:str - mode by which to send data [streaming or file]
        exception:bool - whether to print exception or not
    :params:
        status:bool
        header:dict - header to add
        json_payload:json format of payload
        r:requests.response - response from requests
        error:str - error message
    :return:
        status
    """
    status = True
    header = {
        'type': 'json',
        'dbms': dbms,
        'table': table,
        'mode': 'streaming',
        'Content-Type': 'text/plain'
    }

    if mode in ['streaming', 'file']:
        header['mode'] = mode

    if isinstance(payloads, dict):
        json_payload = json.dumps(payloads)
        r, error = conn.put(headers=header, payload=json_payload)
        if other_cmd.print_error(conn=conn.conn, request_type='PUT', command='PUT data', r=r, error=error, exception=exception):
            status = False
    elif isinstance(payloads, list):
        for payload in payloads:
            json_payload = json.dumps(payload)
            r, error = conn.put(headers=header, payload=json_payload)
            if other_cmd.print_error(conn=conn.conn, request_type='PUT', command='PUT data', r=r, error=error, exception=exception):
                status = False
    elif isinstance(payloads, str):
        r, error = conn.put(headers=header, payload=payloads)
        if other_cmd.print_error(conn=conn.conn, request_type='PUT', command='PUT data', r=r, error=error, exception=exception):
            status = False
    else:
        status = False
        if exception is True:
            print('Invalid type %s for payloads' % type(payloads))

    return staus



