import rest 

def __build_topic(topic_name:str="#", topic_dbms:str=None, topic_table:str=None, column_timestamp:dict={'name': 'timestamp', 'type': 'timestamp', 'value': 'now'}, column_values:dict=[{}])->str: 
    """
    Given MQTT topic parameter(s), build an MQTT topic for client
    :args: 
        topic_name:str - topic to track via MQTT 
        topic_dbms:str - database to store data from MQTT into 
        topic_table:str - table to store data from MQTT into 
        column_timestamp:dict - timestamp information to extract from MQTT [example: {'name': 'timestamp', 'type': 'timestamp', 'vaule': 'now'}] 
        column_values:list - list of columns other than timestamp to add extract data from [example: {'name': 'value', 'type': 'int', 'vaule': 'bring [opcua1][value]'}]
    :params: 
        cmd:str - topic component of MQTT 
    :return: 
        cmd
    """
    if None in [topic_dbms, topic_table]: 
        return "'%s'" % topic_name
    cmd = "(name='%s' and dbms='%s' and table='%s'" % (topic_name, topic_dbms, topic_table)

    if isinstance(column_timestamp, dict) and column_timestamp != {} and column_timestamp != None: 
        try: 
            name = column_timestamp['name']
        except: 
            name = 'timestamp'
        try: 
            column_type = column_timestamp['type']
        else: 
            column_type='timestamp' 
        if column_type not in ['int', 'timestamp', 'bool', 'str']: 
            column_type = 'str' 
        try: 
            value = column_timestamp['value']
        except: 
            value = 'now' 
        cmd += " and column.%s=(value='%s' and type='%s')" % (name, value, column_type) 
    elif isinstance(column_timestamp, list) and column_timestamp != [] and column_timestamp != None: 
        for column in column_timestamp: 
            try: 
                name = column['name']
            except: 
                name = 'timestamp'
            try: 
                column_type = column['type']
            else: 
                column_type='timestamp' 
            if column_type not in ['int', 'timestamp', 'bool', 'str']: 
                column_type = 'str' 
            try: 
                value = column['value']
            except: 
                value = 'now' 
            cmd += " and column.%s=(value='%s' and type='%s')" % (name, value, column_type) 

    # Plesae note - the default config asks regarding only column. it is up to a user to manually set multiple columns 
    if isinstance(column_values, dict) and column_values != {} and column_values != None: 
        try: 
            name = column_values['name']
        except: 
            name = None
        try: 
            column_type = column_values['type']
        else: 
            column_type='str'
        if column_type not in ['int', 'timestamp', 'bool', 'str']: 
            column_type = 'str' 
        try: 
            value = column_values['value']
        except: 
            value = None
        if name != None and value != None: # add to command only if non of the params are empty
            cmd += " and column.%s=(value='%s' and type='%s')" % (name, value, column_type) 

    elif isinstance(column_values, list) and column_values != [] and column_values != None: 
        for column in column_values: 
            try: 
                name = column['name']
            except: 
                name = None
            try: 
                column_type = column['type']
            else: 
                column_type='str'  
            if column_type not in ['int', 'timestamp', 'bool', 'str']: 
                column_type = 'str' 
            try: 
                value = column['value']
            except: 
                value = None
            if name != None and value != None: # add to command only if non of the params are empty
                cmd += " and column.%s=(value='%s' and type='%s')" % (name, value, column_type) 

    return cmd + ")"

def mqtt(broker:str, conn:str, timeout:float=10, auth:tuple=None, exception::bool=True, user:str=None, passwd:str=None, port:int=None, log:bool=False, topic_name:str="#", 
        topic_dbms:str=None, topic_table:str=None, column_timestamp:dict={'name': 'timestamp', 'type': 'timestamp', 'value': 'now'}, column_values:dict=[{}])->bool: 
    """
    Declare MQTT client - based on the arguments given by the user one of the 3 types of MQTT processes will be deployed
    :mqtt types: 
        extract data from MQTT and format it to file/Operator: run mqtt client where broker [and user and password and port] and log and topic=(name and dbms and table and column.timestamp.timestmap and column.value=(value and type))
        extract data from specific topic, but keep raw: run mqtt client where broker [and user and password and port] and log and topic=name
        extract all data from a specific MQTT: run mqtt client where broker [and user and password and port] and log and topic="#"  
    :args: 
        conn:str - REST connection info
        timeout:float - REST timeout 
        auth:tuple - REST authentication
        exception:bool - Exception information
        # MQTT 
        broker:str - MQTT broker info
            -> IP - Remote broker 
            -> local - local broker 
            -> REST - utilize mqtt process as part of the rest
        user:str - MQTT user info 
        passwd:str - MQTT password for user 
        port:int  - MQTT port number 
        log:bool - whether to print output messages to screen (True) or not (False) 
        # MQTT Topic
        topic_name:str - topic to track via MQTT 
        topic_dbms:str - database to store data from MQTT into 
        topic_table:str - table to store data from MQTT into 
        column_timestamp:dict - timestamp information to extract from MQTT [example: {'name': 'timestamp', 'type': 'timestamp', 'vaule': 'now'}] 
        column_values:list - list of columns other than timestamp to add extract data from
    :params: 
        status:bool 
        cmd:str - command to execute
    """
    status = True

    cmd = "run mqtt client where broker=%s and log=%s" % (broker, log)
    if user != None: 
        cmd += " and user='%s'" % user
        if passwd != None: 
            cmd += " and password='%s'" % passwd
    if port != None: 
        cmd += " and port=%s" % port
    if topic_name != None: 
        cmd += " and topic=%s" % __build_topic(topic_name=topic_name, topic_dbms=topic_dbms, topic_table=topic_table, column_timestamp=topic_timestamp, column_values=column_values)
    else: 
        cmd += " and topic='#'" 

    status = rest.post(conn=conn, cmd=cmd, timeout=timeout, auth=auth, exception=exception)
    if status == False and exception == True: 
        print('Failed to start MQTT client for broker: %s' % broker) 

    return status 
