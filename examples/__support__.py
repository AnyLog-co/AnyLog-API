import argparse
import datetime
import time
import random
import re

from anylog_api.__support__ import check_conn_info

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