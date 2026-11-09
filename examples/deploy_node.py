import argparse
import asyncio
import os.path
import dotenv


from src.core.anylog_rest_api import AnyLogRest
from src.generic.status import get_status
from src.generic.config import get_dictionary
from src.data_management.dbms import connect_dbms, create_table
from src.metadata.blockchain import connect_blockchain, create_table_ledger, blockchain_sync_master, publish_policy, blockchain_get
from src.generic.status import ExecMode
from src.metadata.policy_definition import cluster_policy, node_policy
from src.core.support_logging import LevelMode, async_exec_logging
from src.generic.enable_services import enable_operator


def _check_file(env_file):
    env_file = os.path.expanduser(os.path.expandvars(env_file))
    if not os.path.isfile(env_file):
        raise argparse.ArgumentTypeError(f"Failed to locate file: {env_file}")
    return env_file


def _extract_info(conn:str):
    auth = None
    if '@' in conn:
        auth, conn = conn.split('@')
        auth = tuple(auth.split(':'))

    return conn, auth


def _read_file(env_file:str):
    if os.path.isfile(env_file):
        try:
            return dict(dotenv.dotenv_values(dotenv_path=env_file))
        except Exception as error:
            raise Exception(f"Failed to load content from dotenv file - {env_file} (Error: {error})")
    raise FileNotFoundError(f"Failed to locate {env_file}")

EXEC_MODE = ExecMode.EXECUTE

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("conn", type=str, help="REST connection to node (format: user:password@ip:port)")
    parser.add_argument("--env", required=True, type=_check_file, help="Env file to deploy node")
    parser.add_argument("--connection-timeout", required=False, type=float, default=30, help="seconds to wait for the TCP connection to establish")
    parser.add_argument("--read-timeout",       required=False, type=float, default=30, help="seconds to wait for response data once connected")
    parser.add_argument("--write-timeout",      required=False, type=float, default=30, help="seconds to wait while sending request data")
    parser.add_argument("--pool",               required=False, type=float, default=5,  help="seconds to wait for a free connection slot in httpx's connection pool")
    args = parser.parse_args()

    # connect to AnyLog agent
    conn, auth = _extract_info(conn=args.conn)
    anylog_conn = AnyLogRest(conn=conn, auth=auth, connection_timeout=args.connection_timeout,
                             read_timeout=args.read_timeout, write_timeout=args.write_timeout, pool=args.pool)

    # validate connection to node
    node_status = get_status(anylog_conn=anylog_conn, json_format=True, remote_destination=None)
    print(node_status)
    if not node_status or not node_status.get("status") or node_status.get("status").lower() != "running":
        raise ConnectionError(f"Failed to connect to AnyLog instance against {conn}")

    # extract AnyLog's dict and dotenv file variables
    dict_configs = get_dictionary(anylog_conn=anylog_conn, json_format=True, remote_destination=None)
    env_configs = _read_file(env_file=args.env)
    node_type = env_configs.get("NODE_TYPE", None)
    if not node_type:
        raise ValueError(f"Failed to define node type to configure AnyLog agent")

    # configure logical databases
    db_type     = env_configs.get("DB_TYPE", dict_configs.get("db_type"))
    default_db  = env_configs.get("DEFAULT_DBMS", dict_configs.get("db_type", "mydb"))
    in_memory   = env_configs.get("MEMORY", False)
    db_user     = env_configs.get("DB_USER", None)
    db_passwd   = env_configs.get("DB_PASSWD", None)
    db_ip       = env_configs.get("DB_IP", None)
    db_port     = env_configs.get("DB_PORT", None)
    autcommit   = env_configs.get("AUTOCOMMIT", True)

    if not db_type:
        raise ValueError(f"Failed to define physical database type")

    if node_type in ["master", "master-operator", "standalone", "standalone-operator", "master-publisher", "standalone-publisher"]:
        connect_blockchain(anylog_conn=anylog_conn, db_type=db_type, db_user=db_user, db_password=db_passwd,
                           db_ip=db_ip, db_port=db_port, exec_mode=EXEC_MODE)

        create_table_ledger(anylog_conn=anylog_conn, exec_mode=EXEC_MODE)

    # define connection to ledger (`run ledger`)
    blockchain_sync_master(anylog_conn=anylog_conn, sync_time=env_configs.get("BLOCKCHAIN_SYNC", "30 seconds"),
                           source=env_configs.get("BLOCKCHAIN_SOURCE", "master"),
                           dest=env_configs.get("BLOCKCHAIN_DESTINATION", "file"),
                           ledger_conn=env_configs.get("LEDGER_CONN", f"{dict_configs.get('ip')}:{dict_configs.get('anylog_server_port')}"),
                           exec_mode=EXEC_MODE)


    is_operator = True if node_type in ["master-operator", "standalone", "standalone-operator", "operator"] else False
    is_publisher = True if node_type in ["master-publisher", "standalone-publisher", "publisher"] else False

    if is_operator or is_publisher:
        connect_dbms(anylog_conn=anylog_conn, db_name="almgm", db_type=db_type, db_user=db_user, db_password=db_passwd,
                     db_ip=db_ip, db_port=db_port, exec_mode=EXEC_MODE)
        create_table(anylog_conn=anylog_conn, db_name="almgm", table_name="tsd_info", exec_mode=EXEC_MODE)

    cluster_id = None
    query_count = 0
    cluster_where_condition = [
        f'name={env_configs.get("CLUSTER_NAME", "My Cluster") if env_configs.get("CLUSTER_NAME", "My Cluster") != '' else "My Cluster"}',
        f'company={env_configs.get("COMPANY_NAME", "My Company")}'
    ]

    if is_operator:
        connect_dbms(anylog_conn=anylog_conn, db_name=default_db, db_type=db_type, db_user=db_user, db_password=db_passwd,
                     db_ip=db_ip, db_port=db_port, exec_mode=EXEC_MODE)

        # cluster policy
        while not cluster_id:
            cluster_id = blockchain_get(anylog_conn=anylog_conn, policy_type="cluster", where=cluster_where_condition,
                                        bring="id", bring_mode="first", exec_mode=EXEC_MODE)
            if not cluster_id and query_count == 0:
                _cluster_policy = cluster_policy(anylog_conn=anylog_conn,
                                                 name=env_configs.get("CLUSTER_NAME", "My Cluster") if env_configs.get(
                                                     "CLUSTER_NAME", "My Cluster") != '' else "My Cluster",
                                                 company=env_configs.get("COMPANY_NAME", "My Company"),
                                                 exec_mode=EXEC_MODE)

                publish_policy(anylog_conn=anylog_conn, policy=_cluster_policy, exec_mode=EXEC_MODE)
                query_count += 1
            elif not cluster_id:
                asyncio.run(async_exec_logging(
                    message=f"Failed to declare and/or locate cluster policy ({', '.join(cluster_where_condition)}) "
                            f"in blockchain",
                    level=LevelMode.ERROR, raise_exception=False))
                return None

    policy_id = None
    _node_policy = None
    query_count = 0
    node_name = env_configs.get("NODE_NAME") or dict_configs.get("node_name") or f"My {node_type}"
    where_conditions = [
        f'name={node_name}',
        f'company={env_configs.get("COMPANY_NAME", "My Company")}',
        f'ip={dict_configs.get("external_ip") if not dict_configs.get("tcp_bind") else dict_configs.get("ip")}',
        f'port={dict_configs.get("anylog_server_port")}',
    ]
    if node_type == 'operator' and cluster_id:
        where_conditions.append(f"cluster_id={cluster_id}")


    while not policy_id:

        policy_id = blockchain_get(anylog_conn=anylog_conn, policy_type=node_type.split('-')[-1],
                                   where=where_conditions, bring="id", bring_mode="first", exec_mode=EXEC_MODE)

        if not policy_id and query_count == 0:
            _node_policy = node_policy(anylog_conn=anylog_conn,node_type=node_type, name=node_name,
                                       company=env_configs.get("COMPANY_NAME", "My Company"), cluster=cluster_id,
                                       port=dict_configs.get("anylog_server_port"),
                                       rest_port=dict_configs.get("anylog_rest_port"),
                                       tcp_bind=dict_configs.get("tcp_bind", False),
                                       broker_port=dict_configs.get("anylog_broker_port", None),
                                       loc=dict_configs.get("loc"), country=dict_configs.get("country"),
                                       state=dict_configs.get("state"), city=dict_configs.get("city"),
                                       exec_mode=EXEC_MODE)

            publish_policy(anylog_conn=anylog_conn, policy=_node_policy, exec_mode=EXEC_MODE)
            query_count += 1
        elif not policy_id:
            asyncio.run(async_exec_logging(
                message=f"Failed to declare and/or locate {node_type} node policy (name={node_name}, "
                        f"company={env_configs.get("COMPANY_NAME", "My Company")}) in blockchain",
                level=LevelMode.ERROR, raise_exception=False))
            return None

    if is_operator:
        enable_operator(anylog_conn=anylog_conn, operator_id=policy_id,
                        master_node=env_configs.get("LEDGER_CONN", f"{dict_configs.get('ip')}:{dict_configs.get('anylog_server_port')}"),
                        exec_mode=EXEC_MODE)

    return None

if __name__ == "__main__":
    main()
