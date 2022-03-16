import os
import sys
ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).split('configs')[0]
REST_PATH = os.path.join(ROOT_PATH, 'REST')
sys.path.insert(0, REST_PATH)

from anylog_connection import AnyLogConnection
import database_calls


def create_table(anylog_conn:AnyLogConnection, db_type:str, table_name:str, db_name:str='configs',
                 exception:bool=False):
    """
    Create configuration table
    :args:
        anylog_conn:anylog_connection.AnyLogConnection - Connection to AnyLog via REST
        db_type:str - database type
        table_name:str - table name
        db_name:str - database name
        exception:bool - whether or not to print exceptions
    :params:
        create_table:str - create table statement
    :sample table:
        CREATE TABLE IF NOT EXISTS default_params(
            command_id SERIAL PRIMARY KEY,
            al_value VARCHAR NOT NULL,
            al_command VARCHAR NOT NULL
        );
    """
    create_table = (f"CREATE TABLE IF NOT EXISTS {table_name}("
                    +"command_id SERIAL PRIMARY KEY, "
                    +"al_value VARCHAR NOT NULL, "
                    +"al_command VARCHAR NOT NULL,"
                    +"UNIQUE (al_value)"
                    +");")
    if db_type == 'sqlite':
        create_table = create_table.replace(" SERIAL PRIMARY KEY,", " INTEGER PRIMARY KEY AUTOINCREMENT,", 1)
        create_table = create_table.replace("UNIQUE (al_value)", "CONSTRAINT al_value_constraint UNIQUE (al_value)")

    database_calls.execute_post_command(anylog_conn=anylog_conn, db_name=db_name, command=create_table,
                                        exception=exception)



def insert_data(anylog_conn:AnyLogConnection, table_name:str, insert_data:dict, db_name:str='configs',
                exception:bool=False):
    """
    Insert data into configuration data
    :args:
        anylog_conn:anylog_connection.AnyLogConnection - Connection to AnyLog via REST
        table_name:str - table name
        insert_data:dict - data to be inserted
        db_name:str - database name
        exception:bool - whether or not to print exceptions
    """
    # stmt = f"INSERT INTO {table_name}(al_value, alv_command) VALUES (%s, %s);"
    select_stmt = f"SELECT COUNT(*) FROM {table_name} WHERE al_value='%s=<>'"
    insert_stmt = f"INSERT INTO {table_name} (al_value, al_command) VALUES ('%s=<>', '%s');"
    update_stmt = f"UPDATE {table_name} SET al_command='%s' WHERE al_value='%s=<>'"
    
    for param in insert_data:
        row_count = database_calls.execute_get_command(anylog_conn=anylog_conn, db_name=db_name,
                                                       command=select_stmt % param.rstrip().lstrip(),
                                                       format='json', stat=False, destination=None, exception=exception)
        if row_count['Query'][0]['COUNT(*)'] == 0:
            database_calls.execute_post_command(anylog_conn=anylog_conn, db_name=db_name,
                                                command=insert_stmt % (param.rstrip().lstrip(), insert_data[param]),
                                                exception=exception)
        else:
            database_calls.execute_post_command(anylog_conn=anylog_conn, db_name=db_name,
                                                command=update_stmt % (insert_data[param], param.rstrip().lstrip()),
                                                exception=exception)

