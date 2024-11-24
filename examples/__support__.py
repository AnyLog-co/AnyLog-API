import argparse
import datetime
import time
import random
import re

from anylog_api.__support__ import check_conn_info

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
    conns = conn.split(',')
    rest_conns = {}
    for conn in conns:
        if check_conn_info(conn=conn) is True:
            rest_conns[conn] = None

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