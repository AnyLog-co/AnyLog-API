

def generate_query(db_name:str, query:str, format:str='json', stat:bool=True,
                   include:str=None, extend:str=None, timezone:str='local')->str:
    """
    Generate SQL request
    :args:
        db_name:str - logical database to query against
        query:str - query to execute (ex. select count(*) from rand_datq where timestamp >= NOW() - 1 day)
        destination:str - whether to run query against the entire network or specific node(s). If set to None, then
                          run without `destination`
        format:str - result fromat (json || table)
        stat:bool - whether to print statistics at the end of the query
                    to return results in true JSON format - stat should be set to False
        include:str  - comma separated "list" of tables to include in query
        extend:str -   comma separated "list" of information to include in the results
        timezone:str - results timezone (https://github.com/AnyLog-co/documentation/blob/master/queries.md#timezones)
    :params:
        command:str - generated SQL REST request
    :return:
        command
    """
    # build query
    if format.split(':')[0].lower() not in ['json', 'table']:
        format='json'
    command = f'sql dbms={db_name} where format={format.lower()}'
    if stat is True:
        command += f' and stat=True'
    else:
        command += f' and stat=False'
    if include is not None:
        command += f' and include=({include})'
    if extend is not None:
        command += f' and extend={extend}'
    if timezone is not None:
        command += f' and timezone={timezone.lower()}'

    command += f' {query}'

    return command

