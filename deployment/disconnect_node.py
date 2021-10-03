import __init__
import anylog_api
import dbms_cmd
import get_cmd
import post_cmd
import policy_cmd
import other_cmd


def disconnect_node(conn:anylog_api.AnyLogConnect, config:dict, node_types:list=None,
                    clean_node:bool=False, exception:bool=False):
    """
    Disconnect node from network:
        1. disconnect from processes lin process list
        2. disconnect from databases
    If clean_node:
        1. drop connected databases
        2. drop correlated policy based on the shared configs
    :note:
        code only removes policies of type: master, operator, publisher and query
    :args:
        conn:anylog_api.AnyLogConnect - connect to AnyLog
        config:dict - config from file
        node_type:list - node type
        clean_node:bool - to remove everything (but files) from node
        exception:bool - whether to print exceptions
    :params:
        master_node:str - corresponding master node
        process_list:str - AnyLog process list
        params:dict - blockchain to config matching for query params
        query_params:dict - parameters used to query the database
    """
    if config['node_type'] == 'master' or config['node_type'] == 'single_node':
        master_node = 'local'
    else:
        master_node = config['master_node']

    # disconnect processes
    process_list = get_cmd.get_processes(conn=conn, exception=exception)
    if process_list is not None:
        for process in process_list.split('\n'):
            process_status = True
            if 'running' in process.lower():
                if process.split('|')[0].lstrip().rstrip() == 'Operator':
                    process_status = post_cmd.stop_process(conn=conn, process_name='operator', exception=exception)
                elif process.split('|')[0].lstrip().rstrip() == 'Publisher':
                    process_status = post_cmd.stop_process(conn=conn, process_name='publisher', exception=exception)
                elif process.split('|')[0].lstrip().rstrip() == 'Blockchain Sync':
                    process_status = post_cmd.stop_process(conn=conn, process_name='synchronizer', exception=exception)
                elif process.split('|')[0].lstrip().rstrip() == 'MQTT':
                    process_status = post_cmd.stop_process(conn=conn, process_name='mqtt', exception=exception)
                elif process.split('|')[0].lstrip().rstrip() == 'Scheduler':
                    process_status = post_cmd.stop_process(conn=conn, process_name='scheduler', exception=exception)

                if process_status is False:
                    print('Failed to stop %s' % process.split('|')[0].lstrip().rstrip())
                else:
                    print('Stopped: %s' % process.split('|')[0].lstrip().rstrip())

    # disconnect database(s)
    dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
    for dbms in dbms_list:
        if not dbms_cmd.disconnect_dbms(conn=conn, db_name=dbms, exception=exception):
            print('Failed to disconnect database: %s' % dbms)
        else:
            print("Disconnected from: %s" % dbms)

    if clean_node is True:
        # clean database(s)
        if config['db_type'] == 'psql':
            if not dbms_cmd.connect_dbms(conn=conn, config=config, db_name='postgres', exception=exception):
                print("Failed to connect to 'Postgres' database, as such cannot drop correlated logical databases")
                status = False
        if config['node_type'] != 'query':
            if not dbms_cmd.drop_dbms(conn=conn, db_name='system_query', db_type='sqlite', exception=exception):
                print("Failed to drop '%s' logical database " % 'system_query')
            else:
                print("Disconnected from: %s" % dbms)

        updated_dbms_list = dbms_cmd.get_dbms(conn=conn, exception=exception)
        for db_name in dbms_list:
            if db_name not in updated_dbms_list: # validate the database being dropped is disconnected
                if not dbms_cmd.drop_dbms(conn=conn, db_name=db_name, db_type=config['db_type'], exception=exception):
                    print("Failed to drop '%s' logical database " % db_name)
            elif db_name != 'postgres':
                print("'%s' logical database was not disconnected, thus unable to be dropped" % db_name)
        if config['db_type'] == 'psql':
            if not dbms_cmd.disconnect_dbms(conn=conn, db_name='postgres', exception=exception):
                print("Failed to disconnect from 'Postgres' database")
        

        params = {
            'name': 'node_name',
            'company': 'company_name',
            'ip': 'external_ip',
            'local_ip': 'ip',
            'port': 'anylog_server_port',
            'rest_port': 'anylog_rest_port'
        }

        query_params = {}
        for query in params:
            if params[query] in config:
                query_params[query] = config[params[query]]

        if node_types is not None:
            for node in node_types:
                """
                The reason the code skips node of type query is because when deploying "single_node" there's no need
                to specify a query node on the database as all nodes can query (all) data 
                """
                if not policy_cmd.drop_policy(conn=conn, master_node=master_node, policy_type=node,
                                              query_params=query_params, exception=exception) and node != 'query':
                    print('Failed to drop policy of type %s' % node)
                else:
                    print('Policy of type %s was dropped' % node)
        elif not policy_cmd.drop_policy(conn=conn, master_node=master_node, policy_type=config['node_type'],
                                        query_params=query_params, exception=exception):
            print('Failed to drop policy of type %s' % config['node_type'])
        else:
            print('Policy of type %s was dropped' % config['node_type'])










