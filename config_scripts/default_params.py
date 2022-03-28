import argparse
import os
import sys


ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('config_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'REST')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import configs_support
import generic_get_calls
import database_calls


def main():
    """
    The following stores the default dictionary params into configs.
    Note - for db_type of type SQLite there's no need to specify (other) database params
    :positional arguments:
        conn                        REST IP/Port connection to work against
        db_type     {psql,sqlite}   database type
    :optional arguments:
        -h, --help                      show this help message and exit
        --db-ip         DB_IP           database IP
        --db-port       DB_PORT         database port
        --db-user       DB_USER         database user
        --db-passwd     DB_PASSWD       password correlated to database user
        --auth          AUTH            Authentication (user, passwd) for node
        --timeout       TIMEOUT         REST timeout
        --exception     [EXCEPTION]     whether to print exception
    :params:
        global DEFAULT_PARAMS:list - list of key params that the default should be saved
        db_name:str - logical database name
        table_name:str - database table to store data into
        anylog_conn:anylog_conn:anylog_connection.AnyLogConnection - Connection to AnyLog via REST
        dictionary_values:dict - AnyLog's dictionary values
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('conn',         type=str,   default='127.0.0.1:2049', help='REST IP/Port connection to work against')
    parser.add_argument('db_type',      type=str,   default='sqlite',         choices=['psql', 'sqlite'], help='database type')
    parser.add_argument('--db-ip',      type=str,   default='127.0.0.1',      help='database IP')
    parser.add_argument('--db-port',    type=int,   default=5432,             help='database port')
    parser.add_argument('--db-user',    type=str,   default='admin',          help='database user')
    parser.add_argument('--db-passwd',  type=str,   default='passwd',         help='password correlated to database user')
    parser.add_argument('--auth',       type=tuple, default=(), help='Authentication (user, passwd) for node')
    parser.add_argument('--timeout',    type=int,   default=30, help='REST timeout')
    parser.add_argument('--exception',  type=bool,  nargs='?',  const=True, default=False, help='whether to print exception')
    args = parser.parse_args()

    db_name = 'configs'
    table_name = 'default_params'

    anylog_conn = AnyLogConnection(conn=args.conn, auth=args.auth, timeout=args.timeout)
    if not generic_get_calls.validate_status(anylog_conn=anylog_conn, exception=args.exception):
        print(f'Failed to validate connection to AnyLog on {anylog_conn.conn}')
        exit(1)

    dictionary_values = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=args.exception)
    database_calls.connect_dbms(anylog_conn=anylog_conn, db_name=db_name, db_type=args.db_type, db_ip=args.db_ip,
                                db_port=args.db_port, db_user=args.db_user, db_passwd=args.db_passwd,
                                exception=args.exception)

    configs_support.create_table(anylog_conn=anylog_conn, db_type=args.db_type, table_name=table_name,
                                 db_name=db_name, exception=args.exception)

    for value in dictionary_values:
        configs_support.insert_data(anylog_conn=anylog_conn, table_name=table_name, variable_type="variable",
                                    insert_data={value: dictionary_values[value]}, db_name=db_name,
                                    exception=args.exception)


if __name__ == '__main__':
    main()
