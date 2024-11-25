import anylog_api.anylog_connector as anylog_connector
import anylog_api.data.database as database_cmds


def connect_dbms(conn:anylog_connector.AnyLogConnector, params:dict, destination:str=None, view_help:bool=False,
                 return_cmd:bool=False, exception:bool=False):
    # required params
    node_type = params['node_type']
    db_type = params['db_type']
    db_user = None
    db_passwd = None
    db_ip = None
    db_port = None
    memory = False

    if params['db_type'] != 'sqlite':
        db_user = params['db_user']
        db_passwd = params['db_passwd']
        db_ip = params['db_ip']
        db_port = params['db_port']
    elif 'memory' in params:
        memory = params['memory']

    if node_type == 'master':
        database_cmds.connect_dbms(conn=conn, db_name='blockchain', db_type=db_type, db_user=db_user,
                                   db_password=db_passwd, db_ip=db_ip, db_port=db_port, return_cmd=return_cmd,
                                   destination=destination, view_help=view_help, exception=exception)
        database_cmds.create_table(conn=conn, db_name='blockchain', table_name='ledger', return_cmd=return_cmd,
                                   destination=destination, view_help=view_help, exception=exception)
    if node_type == 'operator':
        if 'default_dbms' not in params:
            print(f'Missing logical database name, cannot create operator node.')
            exit(1)
        database_cmds.connect_dbms(conn=conn, db_name=params['default_dbms'], db_type=db_type, db_user=db_user,
                                   db_password=db_passwd, db_ip=db_ip, db_port=db_port, return_cmd=return_cmd,
                                   destination=destination, view_help=view_help, exception=exception)

    if node_type in ['operator', 'publisher']:
        database_cmds.connect_dbms(conn=conn, db_name='almgm', db_type=db_type, db_user=db_user,
                                   db_password=db_passwd, db_ip=db_ip, db_port=db_port, return_cmd=return_cmd,
                                   destination=destination, view_help=view_help, exception=exception)
        database_cmds.create_table(conn=conn, db_name='almgm', table_name='tsd_info', return_cmd=return_cmd,
                                   destination=destination, view_help=view_help, exception=exception)
    if node_type == 'query' or ('system_query' in  params and params['system_query'] in [True, 'true', 'True'] ):
        database_cmds.connect_dbms(conn=conn, db_name='system_query', db_type=db_type, memory=memory,
                                   db_user=db_user, db_password=db_passwd, db_ip=db_ip, db_port=db_port,
                                   return_cmd=return_cmd, destination=destination, view_help=view_help,
                                   exception=exception)

def nosql_database(conn:anylog_connector.AnyLogConnector, db_name:str, params:dict, destination:str=None, view_help:bool=False,
                   return_cmd:bool=False, exception:bool=False):
    db_type = params['db_type']
    db_user = None
    db_passwd = None
    db_ip = '127.0.0.1'
    db_port = 27017
    if 'nosql_type' in params:
        db_type = params['nosql_type']
    if 'nosql_user' in params:
        db_user = params['nosql_user']
    if 'nosql_passwd' in params:
        db_passwd = params['nosql_passwd']
    if 'nosql_ip' in params:
        db_ip = params['nosql_ip']
    if 'nosql_port' in params:
        db_port = params['nosql_port']

    database_cmds.connect_dbms(conn=conn, db_name=params['default_dbms'], db_type=db_type, db_user=db_user,
                               db_password=db_passwd, db_ip=db_ip, db_port=db_port, return_cmd=return_cmd,
                               destination=destination, view_help=view_help, exception=exception)
