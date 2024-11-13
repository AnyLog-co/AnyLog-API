import argparse
import datetime
import time
import random
import re


def check_conn(conn:str)->dict:
    """
    Check whether configurations are declared properly
    :args:
        conn:str - user input for connection information
    :params:
        rest_conn:dict - REST connection
        error_msg:str - error message (used for raise)
        auth:tuple - authentication informataion
        pattern:re.compile - compile to chck IP:PORT
    :raise:
        if err_msg != ""
    :return:
        rest_conns
    """
    rest_conns = {}
    error_msg = ""
    auth = None
    pattern = re.compile(
        r'^'  # Start of string
        r'((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'  # Match the first three octets
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'  # Match the fourth octet
        r':'  # Match the colon
        r'([0-9]{1,5})'  # Match the port number (1 to 5 digits)
        r'$'  # End of string
    )

    if '@' in conn:
        auth, conn = conn.split('@')
    if not pattern.fullmatch(conn):
        error_msg += f"\n\tInvalid connection IP:PORT value {conn}. Expected part: 127.0.0.1:32048"
    else:
        rest_conns[conn] = auth
    if auth is not None and ":" not in auth:
        error_msg += f"\n\tInvalid authentication information value {auth}. Expected part: user:password"
    elif auth is not None:
        rest_conns[conn] = tuple(auth.split(":"))
    if error_msg:
        raise argparse.ArgumentTypeError(f"Invalid Connection format. Expected format: user:password@IP:PORT {error_msg}")

    return rest_conns

def data_generator(db_name:str=None, table:str=None, total_rows:int=10, wait_time:int=0.5)->list:
    """
    Generate data to be inserted
    :args:
        db_name:str - logical database name
        table:str - physical table name
        total_rows:int - number of rows to insert
        wait_time:float - wait time between each row
    :params:
        rows:list - of rows to insert
        row:dict - generated row to insert
    :return:
        rows
    """
    rows = []

    for i in range(total_rows):
        row = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "value": round(random.random() * 100, 2)
        }
        if db_name:
            row['dbms'] = db_name
        if table:
            row['table'] = table
        rows.append(row)
        if i < total_rows - 1:
            time.sleep(wait_time)

    return rows