"""
SQL queries against AnyLog - build the `sql` command from python values and run it
"""
import asyncio
import re

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, build_headers, exec_info
from src.core.support_logging import LevelMode, async_exec_logging

RESPONSE_FORMATS = {"table", "json", "json:list"}
WHERE_OPERATORS = {"=", "!=", "<>", ">", ">=", "<", "<=", "like", "not like", "in", "not in"}

# Every spelling a user is likely to type, mapped to the unit AnyLog expects.
# "m" is intentionally missing - it's ambiguous between minute and month.
UNIT_ALIASES = {
    "second": {"s", "sec", "secs", "second", "seconds"},
    "minute": {"min", "mins", "minute", "minutes"},
    "hour":   {"h", "hr", "hrs", "hour", "hours"},
    "day":    {"d", "day", "days"},
    "week":   {"w", "wk", "wks", "week", "weeks"},
    "month":  {"mo", "mon", "month", "months"},
    "year":   {"y", "yr", "yrs", "year", "years"},
}
ALIAS_TO_UNIT = {alias: unit for unit, aliases in UNIT_ALIASES.items() for alias in aliases}
TIME_WINDOW_PATTERN = re.compile(r"(\d+)?\s*([a-z]+)", re.IGNORECASE)   # "1 hour", "15min", "hours"
AGGREGATE_PATTERN = re.compile(r"\b(min|max|avg|sum|count)\s*\(", re.IGNORECASE)
SQL_FUNCTION_PATTERN = re.compile(r"^[a-z_]+\(.*\)$", re.IGNORECASE)   # now(), date('now','-1 day'), ...


# ---------------------------------------------------------------------------------------------------------------------
# Support
# ---------------------------------------------------------------------------------------------------------------------
def _parse_time_window(value) -> tuple[str, int] | None:
    """
    Turn a human-friendly time window into (unit, count) for AnyLog
    :args:
        value - "1 hour", "15 min", "hours" (count defaults to 1), or a tuple like (15, "minutes")
    :return:
        ("hour", 1), ("minute", 15), ... or None if the value can't be understood
    """
    if isinstance(value, (tuple, list)) and len(value) == 2:
        value = f"{value[0]} {value[1]}"
    match = TIME_WINDOW_PATTERN.fullmatch(str(value).strip())
    if not match:
        return None
    count = int(match.group(1) or 1)
    unit = ALIAS_TO_UNIT.get(match.group(2).lower())
    if unit is None or count <= 0:
        return None
    return unit, count


def _join(value, separator: str = ", ") -> str | None:
    """Accept a string or a list of strings; return a single comma-separated string"""
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    joined = separator.join(str(item).strip() for item in value if str(item).strip())
    return joined or None


def _sql_literal(value) -> str:
    """
    Render a Python value as a SQL literal.
    SQL functions such as now() are passed through unquoted (same rule the remote-gui uses).
    """
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).strip()
    if SQL_FUNCTION_PATTERN.match(text):
        return text
    return "'" + text.replace("'", "''") + "'"


def _select_clause(select) -> str:
    """
    :args:
        select -
            "*" / "device, value"                     -> as-is
            ["device", "max(value)"]                  -> device, max(value)
            {"value": ["min", "max"], "*": "count"}   -> min(value) as min_value, max(value) as max_value,
                                                         count(*) as count_all
    """
    if isinstance(select, dict):
        parts = []
        for column, functions in select.items():
            if functions is None:              # {"device": None} -> plain column
                parts.append(column)
                continue
            for func in [functions] if isinstance(functions, str) else functions:
                func = func.strip().lower()
                alias = f"{func}_all" if column == "*" else f"{func}_{column}"
                parts.append(f"{func}({column}) as {alias}")
        return ", ".join(parts) or "*"
    return _join(select) or "*"


def _where_clause(where) -> str | None:
    """
    :args:
        where -
            raw SQL string                         -> as-is
            dict:
                {"device": "pump-1"}               -> device = 'pump-1'
                {"status": ["ok", "warn"]}         -> status IN ('ok', 'warn')
                {"error": None}                    -> error IS NULL
            list of (column, operator, value) tuples, joined with AND; put "or" between two tuples to OR them:
                [("value", ">=", 10), ("value", "<", 50)]
                [("device", "=", "pump-1"), "or", ("device", "=", "pump-2")]
    :raise:
        ValueError - unsupported operator or malformed condition
    """
    if where is None:
        return None
    if isinstance(where, str):
        return where.strip() or None

    if isinstance(where, dict):
        conditions = []
        for column, value in where.items():
            if value is None:
                conditions.append(f"{column} IS NULL")
            elif isinstance(value, (list, tuple, set)):
                conditions.append(f"{column} IN ({', '.join(_sql_literal(v) for v in value)})")
            else:
                conditions.append(f"{column} = {_sql_literal(value)}")
        return " AND ".join(conditions) or None

    sql, joiner = [], "AND"
    for item in where:
        if isinstance(item, str) and item.strip().lower() in ("and", "or"):
            joiner = item.strip().upper()
            continue
        if not isinstance(item, (list, tuple)) or len(item) != 3:
            raise ValueError(f"WHERE condition {item!r} must be (column, operator, value)")
        column, operator, value = item
        operator = str(operator).strip().lower()
        if operator not in WHERE_OPERATORS:
            raise ValueError(f"Unsupported WHERE operator {operator!r} - supported: {sorted(WHERE_OPERATORS)}")
        if operator in ("in", "not in"):
            rendered = f"({', '.join(_sql_literal(v) for v in value)})"
        else:
            rendered = _sql_literal(value)
        condition = f"{column} {operator.upper()} {rendered}"
        sql.append(f"{joiner} {condition}" if sql else condition)
        joiner = "AND"
    return " ".join(sql) or None


def _period_start(value: str) -> str:
    """now() stays unquoted; a timestamp string gets quoted - matches remote-gui"""
    return _sql_literal(value or "now()")


def build_query(db_name: str, table_name: str, select="*", where=None, group_by=None, order_by=None, limit: int = 0,
                increments=None, period=None, period_start: str = "now()", date_column: str = "insert_timestamp",
                response_format: str | None = "table", timezone: str | None = "utc",
                include_tables=None, extend_params=None) -> str:
    """
    Build the AnyLog `sql` command string without sending it (see `async_query` for the arguments)
    :return:
        AnyLog `sql` command
    :raise:
        ValueError - invalid input (async_query catches this and routes it through logging)
    """
    if increments and period:
        raise ValueError("AnyLog doesn't support a query with both increments and period")

    window_input = increments or period
    window = _parse_time_window(window_input) if window_input else None
    if window_input and window is None:
        raise ValueError(f"Invalid time window {window_input!r} - expected something like '1 hour', '15 min', '7 days'")

    select_sql = _select_clause(select)
    where_sql = _where_clause(where)
    date_column = date_column.strip()

    if increments:
        if not AGGREGATE_PATTERN.search(select_sql):
            raise ValueError("increments requires at least one aggregation in select, e.g. {'value': ['min', 'max']}")
        unit, count = window
        # same as remote-gui: bucket + the bucket's time range, then the user's columns
        select_sql = (f"increments({unit}, {count}, {date_column}), "
                      f"min({date_column}) as min_ts, max({date_column}) as max_ts, {select_sql}")
    elif period:
        unit, count = window
        period_sql = f"period({unit}, {count}, {_period_start(period_start)}, {date_column})"
        where_sql = f"{period_sql} AND ({where_sql})" if where_sql else period_sql

    sql = f"SELECT {select_sql} FROM {table_name.strip()}"
    if where_sql:
        sql += f" WHERE {where_sql}"
    if group_by_sql := _join(group_by):
        sql += f" GROUP BY {group_by_sql}"
    if order_by_sql := _join(order_by):
        sql += f" ORDER BY {order_by_sql}"
    if limit and int(limit) > 0:
        sql += f" LIMIT {int(limit)}"

    options = []
    if response_format:
        options.append(f"format={response_format}")
    if timezone:
        options.append(f"timezone={timezone}")
    if include_sql := _join(include_tables):
        options.append(f"include=({include_sql})")
    if extend_sql := _join(extend_params):
        options.append(f"extend=({extend_sql})")

    return f"sql {db_name.strip()}{' ' + ' and '.join(options) if options else ''} \"{sql}\""


async def async_query(anylog_conn: AnyLogRest, db_name: str, table_name: str,
                      select: str | list | dict = "*",
                      where: str | dict | list | None = None,
                      group_by: str | list | None = None, order_by: str | list | None = None, limit: int = 0,
                      increments: str | tuple | None = None, period: str | tuple | None = None,
                      period_start: str = "now()", date_column: str = "insert_timestamp",
                      response_format: str | None = "table", timezone: str | None = "utc",
                      include_tables: str | list | None = None, extend_params: str | list | None = None,
                      remote_destination: str | None = "network", exec_mode: ExecMode = ExecMode.EXECUTE):
    """
    Run a SQL query against AnyLog
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        db_name:str - logical database name
        table_name:str - table to query
        select - "*", "a, b", ["a", "max(b)"], or {"b": ["min", "max"], "*": "count"} (see `_select_clause`)
        where - raw SQL string, dict, or list of (column, operator, value) tuples (see `_where_clause`)
        group_by, order_by - string or list of columns ("value DESC" works in order_by)
        limit:int - max rows (0 = no limit)
        increments - time buckets, e.g. "1 hour", "15 min", (5, "minutes"); needs an aggregation in select
        period - window around `period_start`, e.g. "7 days", "1 hour"
        period_start:str - reference point for period: now() (default) or a timestamp string
        date_column:str - timestamp column used by increments / period
        response_format:str - table, json, json:list, or None for the node's default
        timezone:str - utc, local, pt, mt, ct, et, ...
        include_tables, extend_params - string or list (e.g. extend_params=["+ip", "+hostname", "@table_name"])
        remote_destination:str - "network" (default) queries all operators; "ip:port" (comma-separated for
            several) targets specific nodes; "local" / None runs only on the connected node
        exec_mode:ExecMode - Execution mode
    :cmd:
        sql {db_name} [format=... and timezone=... and include=(...) and extend=(...)] "SELECT ... FROM {table_name} ..."
    :return:
        query result, or None if the input was invalid
    :raise:
        ValueError - invalid query input (when FORCE_EXCEPTION is on)
    :sample-call:
        # hourly min/max/avg of value for one device, across the network
        await async_query(anylog_conn, "mydb", "readings", select={"value": ["min", "max", "avg"]},
                          increments="1 hour", where={"device": "pump-1"})
        # raw rows from the last 15 minutes where value >= 10
        await async_query(anylog_conn, "mydb", "readings", period="15 min", where=[("value", ">=", 10)])
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_query)

    if response_format is not None:
        response_format = str(response_format).strip().lower()
        if response_format not in RESPONSE_FORMATS:
            await async_exec_logging(message=f"Invalid response format {response_format!r} - supported: "
                                             f"{sorted(RESPONSE_FORMATS)}; using the node's default",
                                     level=LevelMode.WARNING, raise_exception=False)
            response_format = None

    try:
        command = build_query(db_name=db_name, table_name=table_name, select=select, where=where, group_by=group_by,
                              order_by=order_by, limit=limit, increments=increments, period=period,
                              period_start=period_start, date_column=date_column,
                              response_format=response_format, timezone=timezone,
                              include_tables=include_tables, extend_params=extend_params)
    except ValueError as error:
        return await async_exec_logging(message=f"Query not sent: {error}", level=LevelMode.ERROR,
                                        exception_type=ValueError, cause=error)

    headers = build_headers(command=command, remote_destination=remote_destination)
    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)


def query(anylog_conn: AnyLogRest, db_name: str, table_name: str, select: str | list | dict = "*",
          where: str | dict | list | None = None, group_by: str | list | None = None,
          order_by: str | list | None = None, limit: int = 0, increments: str | tuple | None = None,
          period: str | tuple | None = None, period_start: str = "now()", date_column: str = "insert_timestamp",
          response_format: str | None = "table", timezone: str | None = "utc",
          include_tables: str | list | None = None, extend_params: str | list | None = None,
          remote_destination: str | None = "network", exec_mode: ExecMode = ExecMode.EXECUTE):
    """Sync wrapper around `async_query` - see that function for details"""
    return asyncio.run(async_query(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name, select=select, where=where,
                                   group_by=group_by, order_by=order_by, limit=limit, increments=increments,
                                   period=period, period_start=period_start, date_column=date_column,
                                   response_format=response_format, timezone=timezone,
                                   include_tables=include_tables, extend_params=extend_params,
                                   remote_destination=remote_destination, exec_mode=exec_mode))