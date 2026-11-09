import asyncio
import json
import inspect
import os
import re

from enum import Enum

from src.core.support_logging import LevelMode, async_exec_logging

class ListCommands:
    """
    help with function information
    """
    def list_commands(self):
        """
        provide docstring / help for functions
        """
        return {
            name: getattr(self, name).__doc__
            for name in dir(self)
            if not name.startswith("_") and callable(getattr(self, name))
        }

class ExecMode(Enum):
    EXECUTE = "execute" # execute command
    COMMAND = "command" # return
    HELP = "help" # print command help
    INFO = "info" # print python function name + description



def url_builder(conn:str, is_auth:bool=False)->str:
    if conn.startswith("http"):
        return conn
    scheme = "https" if is_auth else "http"
    return f"{scheme}://{conn}"

def load_json(file_path:str)->dict:
    full_path = os.path.expandvars(os.path.expanduser(file_path))
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert keys to int if numeric
    return {int(k): v for k, v in data.items()}


def exec_info(func):
    """
    If exec.info is enabled then provide python function information (as print)
    :args:
        func - function
    :print:
        method: get_status
        description: `get status` against AnyLog node
    """
    doc = inspect.getdoc(func) or ""
    summary = doc.splitlines()[0] if doc else ""  # just the first line of the docstring
    info = f"method: {func.__name__}\ndescription: {summary}"
    print(info)
    return None

def serialize_data(payload)->str|None:
    """
    Serialize payload to a JSON string for publishing
    :return:
        JSON string, or None if the payload can't be serialized (raises TypeError when FORCE_EXCEPTION is on)
    """
    if isinstance(payload, str):
        return payload
    try:
        return json.dumps(payload)
    except (TypeError, ValueError) as error:
        return asyncio.run(async_exec_logging(message=f"Failed to serialize content to be published (Error: {error})",
                                              level=LevelMode.ERROR, exception_type=TypeError, cause=error))


def format_value(value) -> str:
    """
    Format a value for an AnyLog where condition
        bool / 'true' / 'false' -> true / false
        int / float / numeric string -> as is
        string -> "quoted" (left alone if already quoted)
    """
    if isinstance(value, bool):          # check before int - bool is a subclass of int
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)

    value = str(value).strip()
    if value.lower() in ("true", "false"):
        return value.lower()
    if re.fullmatch(r"-?\d+(\.\d+)?", value):
        return value
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):  # already quoted
        return value
    return f"'{value}'" if '"' in value else f'"{value}"'


def format_conditions(conditions) -> list[str]:
    """
    ['name=My Cluster', 'status=active'] -> ['name="My Cluster"', 'status="active"']
    Also accepts a dict, or a stringified list (e.g. from a CLI / env var).
    """
    if isinstance(conditions, str):
        conditions = conditions.strip().strip('"')
        try:
            conditions = ast.literal_eval(conditions)
        except (ValueError, SyntaxError):
            conditions = [conditions]

    if isinstance(conditions, dict):
        return [f"{k}={format_value(v)}" for k, v in conditions.items()]

    formatted = []
    for cond in conditions:
        key, sep, val = str(cond).partition("=")   # split on first '=' only
        formatted.append(f"{key.strip()}={format_value(val)}" if sep else str(cond))
    return formatted