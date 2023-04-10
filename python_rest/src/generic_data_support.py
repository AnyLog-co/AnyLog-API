def generate_run_mqtt_client(broker:str, port:int, username:str=None, password:str=None, topic:str='*',
                             db_name:str=None, table_name:str=None, timestamp:str='timestamp', values:dict={},
                             logs:bool=False, user_agent:bool=False):
    """
    Generate `run mqtt client` command
    :args:
        broker:str - broker connection information
        port:int port associated with broker
        username:str - username credentials for broker
        password:str - password for username
        topic:str - specific topic to work against (if '*' then assumes all topic names)
        db_nmae:str - logical database name
        table_name:str - table name
        timestamp:str - timestamp column
        value:dict - dict of key/value pairs (ex. {'value': 'value'} || {'value': {'type': 'int', 'value': 'value'}}
                     if no type is set, uses string (str)
        logs:bool - whether to print MQTT logs
        user_agent:bool - whether to use user-agent in `run mqtt`. if `broker` == rest sets to True by default
    :params:
        command:str - generated command
    :return:
        command
    """
    command = f'run mqtt client where broker={broker} and port={port}'
    if broker == 'rest':
        user_agent = True
    if user_agent is True:
        command += f' and user-agent=true'

    if username is not None:
        command += f' and user={username}'
    if password is not None:
        command += f' and password={password}'

    command += f' and log=false'
    if logs is True:
        command += command.replace('log=false', 'log=true')

    command += f' and topic=(name={topic}'
    if db_name is not None:
        command += f' and dbms={db_name}'
    if table_name is not None:
        command += f' and table={table_name}'
    if timestamp is not None:
        command += f' and column.timestamp.timestamp={timestamp}'

    if values != {} and values is not None and isinstance(values, dict):
        for column_name in values:
            column_type = 'str'
            value = None
            if isinstance(values[column_name], dict):
                if 'type' in values[column_name]:
                    column_type = values[column_name]['type']
                    if column_type not in ['int', 'float', 'bool', 'str']:
                        column_type = 'str'
                if 'value' in values[column_name]:
                    value = values[column_name]['value']
            else:
                value = values[column_name]
            if value is not None:
                command += f' and column.{column_name}=(type={column_type} and value={value})'

    command += ')'

    return command


def generate_query(db_name:str, query:str, format:str='json', stat:bool=True,
                   include:str=None, extend:str=None, timezone:str='local'):
    """
    Generate SQL request
    :args:
        db_name:str - logical database to query against
        query:str - query to execute (ex. select count(*) from rand_datq where timestamp >= NOW() - 1 day)
        destination:str - whether to run query against the entire network or specific node(s). If set to None, then
                          run without `destination`
        format:str - result fromat (json || table)
        stat:bool - whether to print statistics at the end of the query
                    to return results in true JSON format - stat should be set to False
        include:str  - comma separated "list" of tables to include in query
        extend:str -   comma separated "list" of information to include in the results
        timezone:str - results timezone (https://github.com/AnyLog-co/documentation/blob/master/queries.md#timezones)
    :params:
        command:str - generated SQL REST request
    :return:
        command
    """
    # build query
    if format.split(':')[0].lower() not in ['json', 'table']:
        format='json'
    command = f'sql dbms={db_name} where format={format.lower()}'
    if stat is True:
        command += f' and stat=True'
    else:
        command += f' and stat=False'
    if include is not None:
        command += f' and include=({include})'
    if extend is not None:
        command += f' and extend={extend}'
    if timezone is not None:
        command += f' and timezone={timezone.lower()}'

    command += f' {query}'

    return command

