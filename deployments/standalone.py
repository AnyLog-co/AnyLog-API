import argparse
import anylog_pyrest.blockchain_calls as blockchain_calls
import anylog_pyrest.database_calls as database_calls
import anylog_pyrest.generic_get_calls as generic_get_calls

def standalone():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rest_conn', type=str, default='127.0.0.1:2049', help='REST connection information')
    parser.add_argument('-e', '--exception', type=bool, nargs='?', const=True, default=False, help='Whether to print errors')
    args = parser.parse_args()

    if not generic_get_calls.validate_status(conn=args.rest_conn, exception=args.excption):
        print('Failed')
    print('Success')

