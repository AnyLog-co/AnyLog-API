from anylog_connector import AnyLogConnector
import database_deployment


def deploy_master(anylog_conn:AnyLogConnector, configuration:dict, exception:bool=False):
    database_deployment.declare_database(anylog_conn=anylog_conn, db_name='blockchain', anylog_configs=configuration, exception=exception)
    database_deployment.declare_table(anylog_conn=anylog_conn, db_name='blockchain', table_name='ledger', exception=exception)
    if 'system_query' in configuration and configuration['system_query'] is True:
        database_deployment.declare_database(anylog_conn=anylog_conn, db_name='system_query', anylog_configs=configuration, exception=exception)


