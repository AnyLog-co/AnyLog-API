import argparse
import os.path
import dotenv


from src.core.anylog_rest_api import AnyLogRest
from src.generic.status import get_status
from src.generic.config import get_dictionary
from src.data_management.dbms import connect_dbms, create_table
from src.metadata.blockchain import connect_blockchain, create_table_ledger
from src.generic.status import ExecMode

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

    if "operator" in node_type or "publisher" in node_type or "standalone" in node_type:
        connect_dbms(anylog_conn=anylog_conn, db_name="almgm", db_type=db_type, db_user=db_user, db_password=db_passwd,
                     db_ip=db_ip, db_port=db_port, exec_mode=EXEC_MODE)
        create_table(anylog_conn=anylog_conn, db_name="almgm", table_name="tsd_info", exec_mode=EXEC_MODE)

    if "operator" in node_type:
        connect_dbms(anylog_conn=anylog_conn, db_name=default_db, db_type=db_type, db_user=db_user, db_password=db_passwd,
                     db_ip=db_ip, db_port=db_port, exec_mode=EXEC_MODE)

if __name__ == "__main__":
    main()
