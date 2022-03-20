import argparse
import os
import sys
ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('config_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'REST')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import configs_support
import generic_get_calls
import generic_post_calls
import database_calls


""" 
a "command" is an AnyLog command to be executed and stored in variable 
a "variable" is a hardset value to be stored in a variable
"""
PARAMS = {
    "anylog_general": {
        "anylog_path": {
            "type": "variable",
            "value": None,
        },
        "hostname": {
            "type": "command",
            "value": "get hostname"
        },
        "company_name": {
            "type": "variable",
            "value": "Ai-Ops"
        },
        "node_name": {
            "type": "variable",
            "value": "al-aiops-node1"
        },
        "node_type": { # master, operator, publisher, query, standalone (master+operator), standalone-publisher (master+publisher)
            "type": "variable",
            "value": "standalone"
        },
        "location": { # location of the node
            "type": "variable",
            "value": generic_get_calls.get_location(exception=False)
        }
    },
    "anylog_network": {
        # A user should only change the external and (local) IPs if they don't want to use the defaults.
        "external_ip": {
            "type": "variable",
            "value": None
        },
        "ip": {
            "type": "variable",
            "value": None
        },
        "anylog_server_port": {
            "type": "variable",
            "value": 2148
        },
        "anylog_rest_port": {
            "type": "variable",
            "value": 2149
        }
    },
    "anylog_database": {
        "db_type": { # if db_type == sqlite then all other db params are not needed
            "type": "variable",
            "value": "psql"
        },
        "db_ip": {
            "type": "variable",
            "value": "127.0.0.1"
        },
        "db_port": {
            "type": "variable",
            "value": 5432
        },
        "db_user": {
            "type": "variable",
            "value": "aladmin"
        },
        "db_passwd": {
            "type": "variable",
            "value": "AnyLogTemp1!"
        }
    },
    "anylog_blockchain": {
        "master_node": {
            "type": "variable",
            "value": "10.1.2.10:2148"
        },
        "source": {
            "type": "variable",
            "value": "master"
        },
        "sync_time": {
            "type": "variable",
            "value": '"30 seconds"'
        },
        "dest": {
            "type": "variable",
            "value": "file"
        }
    },
    "anylog_operator": { # operator specific params
        "default_dbms": {
            "type": "variable",
            "value": "aiops"
        },
        "enable_partitions": {
            "type": "variable",
            "value": "true"
        },
        "cluster_name": {
            "type": "variable",
            "value": "aiops-cluster1"
        },
        "partition_table": {
            "type": "variable",
            "value": "*"
        },
        "partition_column": {
            "type": "variable",
            "value": "timestamp"
        },
        "partition_interval": {
            "type": "variable",
            "value": '"7 days"'
        },
        "partition_keep": { # keep about 3 months of data
            "type": "variable",
            "value": 12
        },
        "partition_sync": {
            "type": "variable",
            "value": '"1 day"'
        }
    },
    "anylog_mqtt": { # mqtt params, not needed if deployment of type not master or query
        "enable_mqtt": {
            "type": "variable",
            "value": True
        },
        "broker": {
            "type": "variable",
            "value": "rest"
        },
        "mqtt_port": {
            "type": "variable",
            "value": 2149
        },
        "mqtt_log": {
            "type": "variable",
            "value": False
        },
        "mqtt_topic_name": {
            "type": "variable",
            "value": "aiops"
        },
        "mqtt_topic_dbms": {  # alternatively you can set the default to be [anylog_operator][default_dbms]
            "type": "variable",
            "value": '"bring [dbms]"'
        },
        "mqtt_topic_table": {
            "type": "variable",
            "value": '"bring [table]"'
        },
        "mqtt_column_timestamp": {
            "type": "variable",
            "value": '"bring [ts]"'
        },
        "mqtt_column_value": {
            "type": "variable",
            "value": '"bring [value]"'
        },
        "mqtt_column_value_type": {
            "type": "variable",
            "value": "float"
        }
    },
    "anylog_deployment": { # deployment params, not needed if deployment of type not master or query
        # file name format: [db_name].[table_name].[autogenerated_file_id].json
        "dbms_name": {
            "type": "variable",
            "value": '"bring file_name[0]"'
        }, # alternatively you can set the default to be [anylog_operator][default_dbms]
        "table_name": {
            "type": "variable",
            "value": '"bring file_name[1]"'
        },
        "write_immediate": {
            "type": "variable",
            "value": True
        },

        # run operator Params (needed for node_type == operator)
        "create_table": {
            "type": "variable",
            "value": True
        },
        "update_tsd_info": {
            "type": "variable",
            "value": True
        },
        "archive": {
            "type": "variable",
            "value": True
        },
        "distributor": {
            "type": "variable",
            "value": True
        },

        # run publisher params (needed for node_type == publisher)
        "compress_json": {
            "type": "variable",
            "value": True
        },
        "move_json": {
            "type": "variable",
            "value": True
        },
    }
}


def main():
    """
    The following stores the configuration parameters into logical database tables and then converts then
    into the AnyLog dictionary.
    :note:
        for db_type of type SQLite there's no need to specify (other) database params
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

    anylog_conn = AnyLogConnection(conn=args.conn, auth=args.auth, timeout=args.timeout)
    if not generic_get_calls.validate_status(anylog_conn=anylog_conn, exception=args.exception):
        print(f'Failed to validate connection to AnyLog on {anylog_conn.conn}')
        exit(1)

    database_calls.connect_dbms(anylog_conn=anylog_conn, db_name=db_name, db_type=args.db_type, db_ip=args.db_ip,
                                db_port=args.db_port, db_user=args.db_user, db_passwd=args.db_passwd,
                                exception=args.exception)

    for table_name in list(PARAMS.keys()):
        configs_support.create_table(anylog_conn=anylog_conn, db_type=args.db_type, table_name=table_name,
                                     db_name=db_name, exception=args.exception)
        for param in PARAMS[table_name]:
            if PARAMS[table_name][param]['value'] not in [None, ""]: # assert value is not empty
                if isinstance(PARAMS[table_name][param]['value'], bool):
                    PARAMS[table_name][param]['value'] = str(PARAMS[table_name][param]['value']).lower()
                configs_support.insert_data(anylog_conn=anylog_conn, table_name=table_name,
                                            variable_type=PARAMS[table_name][param]['type'],
                                            insert_data={param: PARAMS[table_name][param]['value']}, db_name=db_name,
                                            exception=args.exception)
        generic_post_calls.convert_db_to_dict(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name,
                                              condition=None, exception=args.exception)


if __name__ == '__main__':
    main()
