imort rest

def send_raw_data(conn:str, payloads:list=[], frmt:str='JSON')->bool: 
    """
    Send data to AnyLog with data containing dbms & table info
   :args: 
        conn:str - REST connection information
        payloads:list - list of data to send via REST
        frmt:str - format of data being sent (JSON or DICT)
   :param:
        status:bool 
        headers:dict - header to send data 
   :return: 
        status
   :sample_data:
    [
        {"dbms": "dmci", "table": "fic11", "value": 50, "ts": "2019-10-14T17:22:13.051101Z"},
        {"dbms": "dmci", "table": "fic16", "value": 501, "ts": "2019-10-14T17:22:13.050101Z"},
        {"dbms": "dmci", "table": "ai_mv", "value": 501, "ts": "2019-10-14T17:22:13.050101Z"} 
    ]
    """
    status = True
    headers = { 
        'command': 'data',
        'User-Agent': 'AnyLog/1.23', 
        'Content-Type': 'text/plain'
    }
    if frmt.upper() == "JSON": 
        try: 
            r = requests.post(conn=conn, headers=headers, data=payloads)
        except Exception as e: 
            print('Failed to send data to AnyLog (Error: %s)' % e)
            status = False
        else: 
            if r.status_code != 200:
                print('Failed to send data to AnyLog due to network error: %s' % r.status_code)
                status = False
    elif frmt.upper() == "DICT": 
        try: 
            r = requests.post(conn=conn, headers=headers, data=payloads)
        except Exception as e: 
            print('Failed to send data to AnyLog (Error: %s)' % e)
            status = False
        else: 
            if r.status_code != 200:
                print('Failed to send data to AnyLog due to network error: %s' % r.status_code)
                status = False

    return status 


def send_data(conn:str, dbname:str, table:str, payloads:list=[], frmt:str='JSON')->bool: 
    """
    Send data to AnyLog with database & table preset in headers 
   :args: 
        conn:str - REST connection information
        dbname:str - database name
        table: str - table name 
        payloads:list - list of data to send via REST
        frmt:str - format of data being sent (JSON or DICT)
   :param:
        status:bool 
        headers:dict - header to send data 
   :return: 
        status
   :sample_data:
    [
        {"value": 50, "ts": "2019-10-14T17:22:13.051101Z"},
        {"value": 501, "ts": "2019-10-14T17:22:13.050101Z"},
        {"value": 501, "ts": "2019-10-14T17:22:13.050101Z"} 
    ]
    """
    status = True
    headers = { 
        'command': 'data',
        'dbms': dbms, 
        'table': table_name,
        'User-Agent': 'AnyLog/1.23', 
        'Content-Type': 'text/plain'
    }
    if frmt.upper() == "JSON": 
        try: 
            r = requests.post(conn=conn, headers=headers, data=payloads)
        except Exception as e: 
            print('Failed to send data to AnyLog (Error: %s)' % e)
            status = False
        else: 
            if r.status_code != 200:
                print('Failed to send data to AnyLog due to network error: %s' % r.status_code)
                status = False
    elif frmt.upper() == "DICT": 
        try: 
            r = requests.post(conn=conn, headers=headers, data=payloads)
        except Exception as e: 
            print('Failed to send data to AnyLog (Error: %s)' % e)
            status = False
        else: 
            if r.status_code != 200:
                print('Failed to send data to AnyLog due to network error: %s' % r.status_code)
                status = False

    return status 
