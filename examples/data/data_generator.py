import datetime
import random


def data_generator(db_name:str, table_name:str)->dict:
    """
    Generate data
    :args:
        db_name:str - logical database name
        table_name:str - table to store data in
    :return:
        dict object to store in AnyLog
    """
    return {
        'dbms': db_name,
        'table': table_name,
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        'value': random.random() * 100
    }


def put_data_generator()->dict:
    """
    Generate data for REST PUT processes
    :return:
        dict object to store in AnyLog
    """
    return {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        'value': random.random() * 100
    }
