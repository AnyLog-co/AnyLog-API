import json
import random
import requests
from paho.mqtt import client as mqtt_client

MQTT_CLIENT_ID = 'python-mqtt-%s' % random.randint(random.choice(range(0, 500)), random.choice(range(501, 1000)))


def __convert_data(data:dict)->str:
    """
    If data is of type dict convert to JSON
    :args:
        data:dict - data to convert
    :params:
        json_data:str - data as a JSON
    :return:
        json_data
    """
    json_data = data
    if isinstance(data, dict):
        try:
            json_data = json.dumps(data)
        except Exception as e:
            print('Failed to convert data into JSON (Error: %s)' % e)
    return json_data


def put_data(conn:str, dbms:str, table:str, data:dict, mode:str='streaming') -> bool:
    """
    Send data via REST using PUT command
    :args:
        conn:str - REST IP & port
        dbms:str - logical database name
        table:str - table name to store data in
        data:dict - data to post into AnyLog
        mode:str - whether to PUT data continuously (streaming) or one at a time (file)
    :params:
        status:bool -
        headers:dict - REST header
    :return:
        False if fails, else True
    """
    status = True
    headers = {
        'type': 'json',
        'dbms': dbms,
        'table': table,
        'mode': 'streaming',
        'Content-Type': 'text/plain'
    }

    try:
        r = requests.put(url='http://%s' % conn, headers=headers, data=__convert_data(data))
    except Exception as e:
        print('Failed to PUT data into %s (Error: %s)' % (conn, e))
        status = False
    else:
        if int(r.status_code) != 200:
            print('Failed to PUT data into %s (Network Error: %s)' % (conn, r.status_code))
            status = False
    return status


def post_data(conn:str, rest_topic:str, data:dict) -> bool:
    """
    Send data via REST using POST command
    :requirement:
        an MQTT client that uses a REST connection as a broker
    :args:
        conn:str - REST IP & port
        rest_topic:str - topic correlated to the MQTT client using a REST
        data:dict - data to post into AnyLog - should contain logical database name and table
    :params:
        status:bool -
        headers:dict - REST header
    :return:
        False if fails, else True
    :sample-mqtt-client-call:
        run mqtt client where broker = rest and port=2049 and user-agent = anylog and topic = (name=yudash-rest and dbms = "bring [dbms]" and table = "bring [table]" and column.timestamp.timestamp = "bring [timestamp]" and column.value.float = "bring [value]")
    :sample-data:
        {
            'dbms': 'new_dbms',
            'table': 'new_table',
            'timestamp': '2021-10-20 15:35:49.32145',
            'value': 3.1459
        }
    """
    status = True
    headers = {
        'command': 'data',
        'topic': rest_topic,
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }

    try:
        r = requests.post(url='http://%s' % conn, headers=headers, data=__convert_data(data))
    except Exception as e:
        print('Failed to POST data into %s (Error: %s)' % (conn, e))
        status = False
    else:
        if int(r.status_code) != 200:
            print('Failed to POST data into %s (Network Error: %s)' % (conn, r.status_code))
            status = False
    return status


def mqtt_post_data(conn:str, mqtt_conn:str, mqtt_port:str, mqtt_topic:str, data:dict) -> bool:
    """
    Send data into the MQTT broker using AnyLog's MQTT publisher tool -
    :requirement:
        an MQTT client that with broker set to local if deploying AnyLog as a broker (run message broker ${IP} ${BROKER_PORT)
        an MQTT client that with broker set to URL if deploying any other MQTT broker
    :args:
        conn:str - REST IP & Port
        mqtt_conn:str - MQTT connection info ( [usr]@[ip]:[passwrd] ), if using AnyLogg brokerr only IP is required
        mqtt_port:str - MQTT port
        mqtt_topic:str - Topic correlated to the MQTT client
        data:dict - data to post into AnyLog - should contain logical database name and table
    :params:
        status:bool 
        headers:dict - REST header
        command:str - MQTT publish command
    :return:
        False if fails, else True
    :sample-mqtt-client-call:
        run mqtt client where broker=local and port=2050 and topic = (name=yudash-broker and dbms = "bring [dbms]" and table = "bring [table]" and column.timestamp.timestamp = "bring [timestamp]" and column.value.float = "bring [value]")
    :sample-data:
        {
            'dbms': 'new_dbms',
            'table': 'new_table',
            'timestamp': '2021-10-20 15:35:49.32145',
            'value': 3.1459
        }
    """
    status = True

    command = 'mqtt publish where broker=%s and port=%s' % (mqtt_conn.split('@')[-1].split(':')[0], mqtt_port)

    if '@' in mqtt_conn:
        command += ' and user=%s' % mqtt_conn.split('@')[0]
    if ':' in mqtt_conn:
        command += ' and password=%s' % mqtt_conn.split(':')[-1]

    command += " and topic=%s and message=%s" % (mqtt_topic, __convert_data(data))

    headers = {
        'command': command,
        'User-Agent': 'AnyLog/1.23'
    }

    try:
        r = requests.post('http://%s' % conn, headers=headers)
    except Exception as e:
        print('Failed to POST data into %s (Error: %s)' % (conn, e))
        status = False
    else:
        if int(r.status_code) != 200:
            print('Failed to POST data into %s (Network Error: %s)' % (conn, r.status_code))
            status = False
    return status


def mqtt_data(mqtt_conn:str, mqtt_port:str, mqtt_topic:str, data:dict)->bool:
    """
    Send data directly using MQTT

    :args:
        mqtt_conn:str - MQTT connection info ( [usr]@[ip]:[passwrd] ), if using AnyLogg brokerr only IP is required
        mqtt_port:str - MQTT port
        mqtt_topic:str - Topic correlated to the MQTT client
        data:dict - data to send into AnyLog
    :params:
        status:bool
        cur - connection to MQTT client
    :return:
       False if fails, else  True
    :mqtt-call:
    run mqtt client where broker=local and port=2050 and topic = (name=yudash-broker and dbms = "bring [dbms]" and table = "bring [table]" and column.timestamp.timestamp = "bring [timestamp]" and column.value.float = "bring [value]")
    :sample-data:
        {
            'dbms': 'new_dbms',
            'table': 'new_table',
            'timestamp': '2021-10-20 15:35:49.32145',
            'value': 3.1459
        }
    """
    status = True

    try:
        cur = mqtt_client.Client(client_id=MQTT_CLIENT_ID)
    except Exception as e:
        status = False
        print('Failed to declare client connection (Error: %s)' % e)
    else:
        broker = mqtt_conn.split('@')[-1].split(':')[0]
        try:
            cur.connect(host=broker, port=mqtt_port)
        except Exception as e:
            status = False
            print('Failed to connect client to MQTT broker %s:%s (Error: %s)' % (broker, mqtt_port, e))

    if status is not False:
        if '@' in mqtt_conn and ':' in mqtt_conn:
            try:
                cur.username_pw_set(username=mqtt_conn.split('@')[0], password=mqtt_conn.split(':')[-1])
            except Exception as e:
                status = False
                print('Faileld to set username [%s] and password [%s] for connection (Error: %s)' % (
                    mqtt_conn.split('@')[0], mqtt_conn.split(':')[-1], e))

    if status is not False:
        try:
            cur.publish(topic=mqtt_topic, payload=__convert_data(data), qos=1, retain=False)
        except Exception as e:
            status = False
            print('Failed to publish data against MQTT connection %s and portt %s (Error: %s)' % (
                mqtt_conn, mqtt_port, e))
    return status
