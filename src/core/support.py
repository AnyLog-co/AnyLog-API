from enum import Enum
import inspect

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
    INFO = None
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