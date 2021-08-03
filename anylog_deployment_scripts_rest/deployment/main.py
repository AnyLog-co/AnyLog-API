import argparse
import time 

import config
import rest
import scheduler 

from master import init as master 
from operators import init as operator
from generic_node import init as generic_node

def __check_status(conn:str, timeout:float=10, auth:tuple=None, exception:bool=True)->bool: 
    """
    Check status @ startup until node is up or up to 5 minutes
    :args:
        conn:str - REST connection info
        timeout:float - timeout 
        auth:tuple - REST authentication
        exception:bool - wehther to print exception
    :param: 
        status:bool 
        mx_time:bool - whether failed due to timeout error (max 5 minutes) 
        max_time:float - max amount of attempts (time base)
    :return:
       status 
    """
    status = False 
    mx_time = False 
    max_time = time.time() + 60
    while status == False and mx_time == False:
        status = rest.get(conn=conn, cmd="get status", timeout=timeout, auth=auth, exception=exception)
        if status == None:
            status = False 
        else: 
            status = True 

        if time.time() > max_time: 
            mx_time = True 
        if status == False:
            time.sleep(5)
       
    return status 

def main(): 
    """
    Deployment code for master via REST
    :positional arguments:
        conn    REST connection info
        config  INI config file (full path)
    :optional arguments:
        -h, --help                      show this help message and exit
        -t, --timeout       TIMEOUT     REST timeout                                                            (default: 10)
        -e, --exception     EXCEPTION   If set to True prints error messages during exceptions                  (default: False)  
        -b, --blockchain    BLOCKCHAIN  IF set to True adds policy to blockchain (needed for first time only)   (default: False) 
    :param: 
        auth:tuple - authentication information 
        config_params:dcit - Parameter based on config file   
        anylog_params:dct - AnyLog dictonary parameters
    :note:
    Node should only contain (in docker ports should be exposed)  
        --> set authentciation off 
        --> TCP port 
        --> REST port 
    :sample docker: 
        docker run --network host --name ${NODE_NAME} -e NODE_TYPE=rest -e ANYLOG_TCP_PORT=${TCP_PORT} -e ANYLOG_REST_PORT=${REST_PORT} [-e ANYLOG_BROKER_PORT=${BROKER_PORT}] -v ${NODE_NAME}-anylog:/app/AnyLog-Network/anylog:rw \  -v ${NODE_NAME}-blockchain:/app/AnyLog-Network/blockchain:rw -v ${NODE_NAME}-data:/app/AnyLog-Network/data:rw -d anylogco/anylog:${BUILD_TYPE}  
    """
    auth = None 
    config_params = {} 
    anylog_params = {} 
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('conn',                  type=str,   default='127.0.0.1:2049', help='REST connection info')
    parser.add_argument('config',                type=str,   default=None,             help='INI config file (full path)') 
    parser.add_argument('-t', '--timeout',       type=float, default=10,               help='REST timeout') 
    parser.add_argument('-e', '--exception',     type=bool,  nargs='?',                const=True, default=False, help='If set to True, prints error messages during exceptions') 
    parser.add_argument('-b', '--blockchain',    type=bool,  nargs='?',                const=True, default=False, help='If set to True adds policy to blockchain (needed for first run only)')
    parser.add_argument('-x', '--remove-buffer', type=bool,  nargs='?',                const=True, default=False, help='Remove buffering for (operator and publisher nodes only)') 
    args = parser.parse_args()
    
    # Validate connecton
    status = __check_status(conn=args.conn, timeout=args.timeout, auth=auth, exception=args.exception) # wait till node is running 
    if status == False: 
        print('Failed to connect to AnyLog node. Cannot continue') 
        exit(1) 
    elif status == True: 
        print('Connected to AnyLog Node: %s' % args.conn)

    # get configs
    anylog_params = config.config_import(config_file=args.config, conn=args.conn, timeout=args.timeout, auth=auth, exception=args.exception) # import into AnyLog dictionary
    anylog_params = config.config_export(conn=args.conn, timeout=args.timeout, auth=auth, exception=args.exception, data=anylog_params) # export for AnyLog dictionary 

    # Set authentication 
    if 'set_authentication' in config_params and 'authentication_user_info' in config_params and bool(config_params['set_authentication']) == True: 
        auth = tuple(config_params['authentication_user_info'].split(':')) 
        status = [] 
        for cmd in ["set local password=%s" % auth[1], 'set authentication on', 'id add user where name=%s and password=%s and type=admin' % (auth[0], auth[1])]:
            status = rest.post(conn=args.conn, cmd=cmd, timeout=args.timeout, auth=None, exception=args.exception)
        if False in status: 
            if args.exception == True: 
                print('Failed to set authentication information') 
            config_params['set_authentication'] = False 

    if 'master_node' not in anylog_params: 
        print('Missing master node from config file. Cannot continue') 
        exit(1) 
    """
    status = scheduler.schedule_one(conn=args.conn, timeout=args.timeout, auth=auth, exception=args.exception)
    if status == False and args.exception == True: 
        print('Failed to scheduler 1 process process') 
    """
    if 'node_type' in anylog_params and anylog_params['node_type'] == 'master': 
        status = master(conn=args.conn, anylog_params=anylog_params, timeout=args.timeout, auth=auth, exception=args.exception, init_blockchain=args.blockchain)
        if status == False: 
            print('Issue during configuration of %s node on %s' % (anylog_params['node_type'], args.conn))
        else: 
            print('Configured %s node on %s' % (anylog_params['node_type'], args.conn)) 
            status = rest.post(conn=args.conn, cmd="reset error log", timeout=args.timeout, auth=None, exception=args.exception)
    elif 'node_type' in anylog_params and anylog_params['node_type'] == 'operator': 
        status = operator(conn=args.conn, anylog_params=anylog_params, timeout=args.timeout, auth=auth, exception=args.exception, init_blockchain=args.blockchain, remove_buffer=args.remove_buffer)
    elif 'node_type' in anylog_params and anylog_params['node_type'] in ['query', 'publisher']: 
        status = generic_node(conn=args.conn, anylog_params=anylog_params, timeout=args.timeout, auth=auth, exception=args.exception, remove_buffer=args.remove_buffer)
        if status == False: 
            print('Issue during configuration of %s node on %s' % (anylog_params['node_type'], args.conn))
        else: 
            print('Configured %s node on %s' % (anylog_params['node_type'], args.conn)) 
            status = rest.post(conn=args.conn, cmd="reset error log", timeout=args.timeout, auth=None, exception=args.exception)
    elif 'node_type' in anylog_params: 
        print('Node of type %s not currently supported' % anylog_params['node_type']) 
    else: 
        print('Unknown node_type. Cannot configure node') 
    
if __name__ == '__main__': 
    main()
