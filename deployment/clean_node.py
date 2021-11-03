import import_packages
import_packages.import_dirs()
import anylog_api
import blockchain_cmd
import dbms_cmd
import get_cmd
import post_cmd
import policy_cmd


def disconnect_node(conn:anylog_api.AnyLogConnect, exception:bool=False)->bool:
    """
    Disconnect from network
        * stop blockchain sync
        * stop Publisher / Operator
        * stop MQTT
        * Scheduler 1
    :args:
        conn:anylog_api.AnyLogConnect - connection to AnyLog
        exception:bool - whether to print exception
    :params:
        statuses:list - list of status from each process
    :return:
        if all succeed return True, else return False
    """
    statuses = []
    process_list = get_cmd.get_processes(conn=conn, exception=exception)
    if process_list is not None:
        for line in process_list.split('\n'):
            if line.rstrip().lstrip().split(' ')[0] in ['Operator', 'Publisher', 'Consumer', 'MQTT'] and 'Running' in line:
                process = line.lstrip().rstrip().split(' ')[0].lower()
                status = post_cmd.stop_process(conn=conn, process_name=process, exception=exception)
                statuses.append(status)
            if 'Blockchain Sync' in line and 'Running' in line:
                status = post_cmd.stop_process(conn=conn, process_name='synchronizer', exception=exception)
                statuses.append(status)

    status = post_cmd.stop_process(conn=conn, process_name='scheduler 1', exception=exception)
    statuses.append(status)

    status = True
    if False in statuses:
        print('Failed to stop one or more processes')
        status = False

    return status


def disconnect_dbms(conn:anylog_api.AnyLogConnect, drop_data:bool=False, config_data:dict={},
                    exception:bool=False)->bool:
    """
    Disconnect (& drop) database
    :args:
        conn:anylog_api.AnyLogConnect - REST connection to AnyLog
        drop_data:bool - whether to drop database (False by default)
        config_data:dict - configuration information (required only if drop_data is True
        exception:bool - whether to print exceptions
    :params:
        statuses:list - list of status results
        psql_status:list - whether connected to PSQL - True unless fails to connect to PSQL
        database_list:dict - list of logical databases + database type
    :return:
        if all statuses are True return True, else Return False
    """
    if drop_data is True and config_data == {}:
        print('Unable to drop database(s) due to missing config_data dictionary')

    statuses = []
    psql_status = False
    database_list = dbms_cmd.get_dbms_type(conn=conn, exception=exception)
    if 'blockchain' in database_list:
        del database_list['blockchain']

    if 'psql' in list(database_list.values()) and drop_data is True and config_data != {}:
        psql_status = True
        if not dbms_cmd.connect_dbms(conn=conn, config=config_data, db_name='postgres', exception=exception):
            print("Failed to connect to Postgres Database, as such won't be able to drop databases using PSQL")
            psql_status = False

    for db_name in database_list:
        status = dbms_cmd.disconnect_dbms(conn=conn, db_name=db_name, exception=exception)
        if status is True and drop_data is True and config_data != {}:
            """
            Database won't be dropped under 1 of 2 conditions
                1. The database type is PostgresSQL & AnyLog fails to connect to postgres logical database
                2. The logical database is the blockchain
            """
            if (database_list[db_name] == 'psql' and psql_status is False) or db_name == 'blockchain':
                pass
            else:
                status = dbms_cmd.drop_dbms(conn=conn, db_name=db_name, db_type=database_list[db_name], exception=exception)
                statuses.append(status)
        else:
            statuses.append(status)

    if psql_status is True:
        dbms_cmd.disconnect_dbms(conn=conn, db_name='postgres', exception=exception)

    status = True
    if False in statuses:
        print('Failed to disconnect and/or drop one or more databases')
        status = False

    return status

def remove_policy(conn:anylog_api.AnyLogConnect, config_data:dict, node_types:list=[], exception:bool=False)->bool:
    """
    Remove policy from blockchain - does not remove cluster or table policies
    :args:
        conn:anylog_api.AnyLogConnect - REST connection into AnyLog
        config_data:dict - node configuration information
        node_types:list - for "single node deployment" the nodes correlated to the node
        exception:bool - whether to print exceptions
    :params:
    :return:
        if successfully drop policy return True, else return False - code doesn't validate policy was dropped
    """
    statuses = []
    where_conditions = {
        'name': config_data['node_name'],
        'company': config_data['company_name'],
        'ip': config_data['external_ip'],
        'local_ip': config_data['ip'],
        'port': int(config_data['anylog_tcp_port']),
        'rest_port': int(config_data['anylog_rest_port'])
    }

    if config_data['node_type'] == 'single_node':
        for node in node_types:
            if node != 'query': # query node isn't written to blockchain in sing_node config as all nodes can act as query node
                status = policy_cmd.drop_policy(conn=conn, master_node=config_data['master_node'], policy_type=node, query_params=where_conditions, exception=exception)
                statuses.append(status)
                if status is True:
                    blockchain_cmd.master_pull_json(conn=conn, master_node='local', master_file='!blockchain_file',
                                                    local_file='!blockchain_file', exception=exception)
        status = True
        if False in statuses:
            status = False
    else:
        status = policy_cmd.drop_policy(conn=conn, master_node=config_data['master_node'], policy_type=config_data['node_type'], query_params=where_conditions, exception=exception)

    if config_data['node_type'] == 'master' or 'master' in node_types and status is True:
        drop_db = None
        while drop_db not in ['yes', 'no']:
            if drop_db is None:
                drop_db = input('Would you like to drop the blockchain logical database [yes/no]? ')
            else:
                drop_db = input('Invalid Option: %s.  Would you like to drop the blockchain logical database [yes/no]? ' % drop_db)

        if drop_db == 'yes':
            if dbms_cmd.disconnect_dbms(conn=conn, db_name='blockchain', exception=exception):
                database_list = dbms_cmd.get_dbms_type(conn=conn, exception=exception)
                if 'psql' in list(database_list.values()) and dbms_cmd.connect_dbms(conn=conn, config=config_data, db_name='postgres', exception=exception):
                    status = dbms_cmd.drop_dbms(conn=conn, db_name='blockchain', db_type='psql', exception=exception)
                else:
                    status = dbms_cmd.drop_dbms(conn=conn, db_name='blockchain', db_type='sqlite', exception=exception)

    return status



















