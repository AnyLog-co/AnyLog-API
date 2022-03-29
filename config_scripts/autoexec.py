import os
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('anylog_scripts')[0]
REST_PATH = os.path.join(ROOT_PATH, 'anylog_pyrest')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import blockchain_calls
import database_calls
import deployment_calls
import generic_get_calls
import generic_post_calls
import support

def main(conn:str, autoexec_file:str='$HOME/AnyLog-API/anylog_scripts/autoexec.json', auth:tuple=(), timeout:int=30,
         exception:bool=False):
    """
    Sample code for deploying autoexec file into AnyLog via REST
    :args:
        conn:str - REST IP:PORT for communicating with AnyLog
        autoexec_file:str - local path for autoexec file
        auth:tuple - authentication information
        timeout:int - REST timeout (in seconds)
        exception:bool - whether to print exception

    """
    anylog_conn = AnyLogConnection(conn=conn, auth=auth, timeout=timeout)
    autoexec_file = os.path.expandvars(os.path.expanduser(autoexec_file))

    print("Validate File & Connection")
    if not os.path.isfile(autoexec_file):
        print(f'Failed to locate {autoexec_file}')

    if not generic_get_calls.validate_status(anylog_conn=anylog_conn, exception=exception):
        print(f'Failed to validate connection to AnyLog on {anylog_conn.conn}')
        exit(1)

    file_content = support.read_file(file_name=autoexec_file, exception=exception)

    generic_post_calls.set_script(anylog_conn=anylog_conn, script_path='autoexec.json',
                                  script_content=file_content, exception=exception)


    local_scripts = generic_get_calls.get_dictionary(anylog_conn=anylog_conn, exception=exception)['local_scripts']
    full_script_path = f"{local_scripts}/autoexec.json"
    if '\\' in local_scripts:
        full_script_path = f"{local_scripts}\\autoexec.json"

    generic_post_calls.process_script(anylog_conn=anylog_conn, script_path=full_script_path, exception=exception)


if __name__ == '__main__':
    main(conn='10.0.0.111:2149', autoexec_file='$HOME/AnyLog-API/anylog_scripts/autoexec.json', auth=(), timeout=30,
         exception=True)


