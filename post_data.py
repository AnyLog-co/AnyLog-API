"""
Sample JSON: {"dbms": "anylog", "table": "test", "timestamp": "2021-01-01 00:00:00", "value": 0} 

Required MQTT call: run mqtt client where broker=rest and user-agent = anylog and topic=(name=anylog and dbms="bring [dbms]" and table="bring [table]" and column.timestamp.timestamp="bring [timestamp]" and column.value.float="bring [value]") 
""" 
import json 
import requests 

def post_data(conn:str, data:dict):
    """
    Send data to AnyLog 
    :args: 
        conn:str - AnyLog REST IP & Port 
        data:list - list to send into AnyLog
    :params: 
        headers:dict - AnyLog headers 
        jdata:str - JSON conversion of 
    :return: 
        nothing is returned. however if something fails message is printed
    """
    headers = {
        'command': 'data',
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }    
    jdata = json.dumps(data) 
    try: 
        r = requests.post('http://%s' % conn, headers=headers, data=jdata)
    except Exception as e: 
        print('Failed to POST data to %s (Error: %s)' % (conn, e))
    else: 
        if r.status_code != 200: 
           print('Failed to POST data to %s due to network error: %s' % (conn, r.status_code))


