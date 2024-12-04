import argparse

from anylog_api.anylog_api import AnyLogAPI
import anylog_api.__support__ as anylog_api_support
import deploy_node
import __support__ as support

def __validate_params(params:dict):
    node_type = params['node_type'] if 'node_type' in params else None
    if not node_type:
        raise ValueError('Missing node type, cannot continue with node deployment...')
    elif node_type not in ['master', 'operator', 'query']:
        raise ValueError(f'Invalid node type {node_type}, cannot continue...')
    node_name = params['node_name'] if 'node_name' in params else None
    if not node_name:
        raise ValueError('Missing node name, cannot continue with node deployment...')
    company_name = params['company_name'] if 'company_name' in params else None
    if not company_name:
        raise ValueError('Missing company name, cannot continue with node deployment...')


def main():
    """
    The following demonstrates deploying AnyLog / EdgeLake instance via REST.
    :positional arguments:
        conn                  REST connection information (Format:  {user}:{password}@{ip}{port})
    :optional arguments:
        -h, --help            show this help message and exit
        --configs       CONFIGS         comma seperated dotenv configuration file(s)
        --timeout       TIMEOUT         REST timeout
        --edgelake      [EDGELAKE]      Connect to EdgeLake instance
        --exception     [EXCEPTION]     Print exception
        --license-key   LICENSE_KEY     License key fo AnyLog if not part of configs
    :params:
        conn:str - connection information for node
        node_status:bool - node status (True / False)
        params:dict - dictionary with configuration file(s) information
        dictionary_params:dict - merged configurations for both AnyLog/EdgeLake and configuration file
        generic_policy:dict - generated node policy
        policy_id:str - policy ID
    """
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=anylog_api_support.validate_conn_info, default='127.0.0.1:32549', help='REST connection information (Format: {user}:{password}@{ip}{port})')
    parse.add_argument('--configs', type=support.check_configs, default=None, help='comma seperated dotenv configuration file(s)')
    parse.add_argument('--timeout', type=float, default=60, help='REST timeout')
    parse.add_argument('--edgelake',  type=bool, const=True, nargs='?', default=False, help='Connect to EdgeLake instance')
    parse.add_argument('--exception', type=bool, const=True, nargs='?', default=False, help='Print exception')
    parse.add_argument('--license-key', type=str, default=None, help='License key fo AnyLog if not part of configs')
    args = parse.parse_args()

    # can only use 1 connection at aa times
    conn = list(args.conn.keys())[0]
    if len(list(args.conn.keys())) != 1:
        for key in args.conn:
            if key != len(list(args.conn.keys())):
                del args.conn[key]

    # connect to AnyLog / EdgeLake
    args.conn[conn] = AnyLogAPI(conn=conn, timeout=args.timeout, exception=args.exception)

    # validate connection
    node_status = args.conn[conn].get_status(destination=None, view_help=False)
    if node_status is False:
        raise ConnectionError(f'Failed to connect to node against {conn}')

    # read configs file
    for config_file in args.configs:
        params = support.read_configs(config_file=config_file, exception=args.exception)

    # declare license key
    if args.edgelake is False and 'license_key' not in params and not args.license_key:
        raise ValueError("Missing license key, cannot continue...")
    elif args.edgelake is False and 'license_key' in params:
        args.conn[conn].execute_post(command=f'set license where activation_key={params["license_key"]}', payload=None,
                                     destination=None, view_help=False)
    elif args.edgelake is False and args.license_key:
        args.conn[conn].execute_post(command=f'set license where activation={args.license_key}', payload=None,
                                     destination=None, view_help=False)

    # update AnyLog dictionary with information from config file
    args.conn[conn].execute_post(command='params', payload=params, destination=None, view_help=False)
    dictionary_params = args.conn[conn].execute_get(command="get dictionary where format=json", destination=None,
                                                    view_help=False)
    dictionary_params = anylog_api_support.format_data(data=dictionary_params)

    # validate required params exist
    __validate_params(params=dictionary_params)

    deploy_node.deploy_node(anylog_conn=args.conn[conn], params=dictionary_params)

    node_type = dictionary_params['node_type']
    node_name = dictionary_params['node_name']
    company_name = dictionary_params['company_name']
    external_ip = dictionary_params['external_ip']
    local_ip = dictionary_params['ip']
    anylog_server_port = dictionary_params['anylog_server_port']
    anylog_rest_port = dictionary_params['anylog_rest_port']
    ledger_conn = dictionary_params['ledger_conn'] if 'ledger_conn' in dictionary_params else '127.0.0.1:32048'

    # call to declare node
    policy_id = None
    status = False
    if node_type in ['master', 'query']:
        new_policy = deploy_node.node_policy(node_type=node_type, node_name=node_name, company_name=company_name,
                                             external_ip=external_ip, local_ip=local_ip,
                                             anylog_server_port=anylog_server_port, anylog_rest_port=anylog_rest_port)
        while policy_id is None and status is False:
            policy_id = deploy_node.get_policy_id(conn=args.conn[conn], policy_type=node_type, policy_name=node_name,
                                                  company_name=company_name)
            if not policy_id and status is False:
                deploy_node.declare_policy(conn=args.conn[conn], policy=new_policy, ledger_conn=ledger_conn)
                status = True
            elif not policy_id and status is True:
                raise ConnectionError(f'Failed to publish policy against {conn}')
            else:
                deploy_node.declare_policy(conn=args.conn[conn], policy=new_policy)
    else:
        # declare cluster
        cluster_name = params['cluster_name'] if 'cluster_name' in params else params['node_name']
        new_policy = deploy_node.cluster_node(cluster_name=cluster_name, company_name=company_name)

        while policy_id is None and status is False:
            policy_id = deploy_node.get_policy_id(conn=args.conn[conn], policy_type='cluster', policy_name=node_name,
                                                  company_name=company_name)
            if not policy_id and status is False:
                deploy_node.declare_policy(conn=args.conn[conn], policy=new_policy, ledger_conn=ledger_conn)
                status = True
            elif not policy_id and status is True:
                raise ConnectionError(f'Failed to publish policy against {conn}')
            else:
                deploy_node.declare_policy(conn=args.conn[conn], policy=new_policy)

        # declare operator
        new_policy = deploy_node.node_policy(node_type=node_type, node_name=node_name, company_name=company_name,
                                             external_ip=external_ip, local_ip=local_ip,
                                             anylog_server_port=anylog_server_port, anylog_rest_port=anylog_rest_port,
                                             cluster_policy=policy_id)

        while policy_id is None and status is False:
            policy_id = deploy_node.get_policy_id(conn=args.conn[conn], policy_type='cluster', policy_name=node_name,
                                                  company_name=company_name)
            if not policy_id and status is False:
                deploy_node.declare_policy(conn=args.conn[conn], policy=new_policy, ledger_conn=ledger_conn)
                status = True
            elif not policy_id and status is True:
                raise ConnectionError(f'Failed to publish policy against {conn}')
            else:
                deploy_node.declare_policy(conn=args.conn[conn], policy=new_policy)


    if node_type == 'operator':
        create_table = str(dictionary_params['create_table']).lower() if 'create_table' in dictionary_params else "true"
        update_tsd_info = str(dictionary_params['update_tsd_info']).lower() if 'update_tsd_info' in dictionary_params else "true"
        compress_file = str(dictionary_params['compress_file']).lower() if 'compress_file' in dictionary_params else "true"
        compress_sql = str(dictionary_params['compress_sql']).str() if 'compress_sql' in dictionary_params else "true"
        archive = str(dictionary_params['archive']).str() if 'archive' in dictionary_params else "true"
        archive_sql = str(dictionary_params['archive_sql']).str() if 'archive_sql' in dictionary_params else "true"
        operator_threads = dictionary_params['operator_threads'] if 'operator_threads' in dictionary_params else 3

        cmd = (f"run operator where create_table= {create_table} and update_tsd_info= {update_tsd_info} and "
              +f"compress_json={compress_file} and compress_sql={compress_sql} and archive_json={archive} and "
              +f"archive_sql={archive_sql} and master_node={ledger_conn} and policy={policy_id} and "
              +f"threads={operator_threads}")

        args.conn[conn].execute_post(command=cmd, payload=None, destination=None, view_help=False)


if __name__ == '__main__':
    main()
