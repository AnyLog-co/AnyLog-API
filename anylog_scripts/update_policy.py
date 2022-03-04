import argparse


def main():
    """
    The following provides an example for creating an AnyLog Network Management Policy (ANMP).
    An ANMP allows for modifying a policy without the need to recreate said policy.
    positional arguments:
        conn                  REST IP/Port connection to work against
    :optional arguments:
        -h, --help                              show this help message and exit
        --policy-type       POLICY_TYPE         blockchain type that needs to be updated    (ex. operator)
        --where-conditions  WHERE_CONDITIONS    condition to find relevent policy           (ex. name=!node_name and company=!company_name)
        --new-values        NEW_VALUES          comma separated list of values to update    (ex. ip=127.0.0.1,hostname=new-host)
        --auth              AUTH                Authentication (user, passwd) for node
        --timeout           TIMEOUT             REST timeout
        --exception         EXCEPTION           whether to print exception
    :params:
        anylog_conn:AnyLogConnection - connection to AnyLog via REST
        policy:dict - Policy to create a correlating ANMP
        policy_id:str - ID of policy
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('conn', type=str, default='127.0.0.1:2049', help='REST IP/Port connection to work against')
    parser.add_argument('--policy-type', type=str, default='operator', help='blockchain type that needs to be updated')
    parser.add_argument('--where-conditions', type=str, default='name=!node_name and company=!company_name', help='condition to find relevent policy')
    parser.add_argument('--new-values', type=str, default='ip=127.0.0.1,hostname=new-host', help='comma separated list of values to update')
    parser.add_argument('--auth', type=tuple, default=(), help='Authentication (user, passwd) for node')
    parser.add_argument('--timeout', type=int, default=30, help='REST timeout')
    parser.add_argument('--exception', type=bool, nargs='?', const=True, default=False, help='whether to print exception')
    args = parser.parse_args()

    anylog_conn = AnyLogConnection(conn=conn, auth=auth, timeout=timeout)
    # validate status
    print("Validate Connection")
    if not generic_get_calls.validate_status(anylog_conn=anylog_conn, exception=exception):
        print(f'Failed to validate connection to AnyLog on {anylog_conn.conn}')
        exit(1)

    policy = blockchain_calls.blockchain_get(anylog_conn=anylog_conn, policy_type=args.policy_type,
                                             where_condition=args.where_condition, exception=args.exception)
    policy_id = policy[args.policy_type]['id']

    new_values = {}
    for value in args.new_values.split(','):
        value = value.rstrip().lstrip().replace(" =", "=").replace("= ", "=")
        new_values[value.split("=")[0]] = value.split("=")[-1]

    policy_type = "anmp"
    policy_values = {policy_id: new_values}
    blockchain_calls.declare_policy(anylog_conn=anylog_conn, policy={policy_type: policy_values},
                                    master_node="!master_node", exception=False)


if __name__ == '__main__':
    main()

