"""
Note: content in payloads will be converted to table columns
"""
import json 
import requests

def put_data(payloads:list, conn:str, dbms:str, table_name:str, mode:str)->bool:
    """
    Send payload to node via REST 
    :args: 
        payloads:dict - data to store in database 
        conn:str - connection string 
        dbms:str - logical database to store data in 
        table_name:str - logical table to store data in 
        mode:str - format by which to send data via REST 
    :param:
        header:dict - REST PUT header info        
    """
    header = { 
        'type': 'json', 
        'dbms': dbms, 
        'table': table_name,
        'mode': mode, 
        'Content-Type': 'text/plain'
    }
    status=True 
    for payload in payloads: 
        json_payload = json.dumps(payload) 
        try: 
            requests.put('http://%s' % conn, headers=header, data=json_payload)
        except Exception as e:
            print(e) 
            status=False  
    return status
