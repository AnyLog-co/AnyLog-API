import json
import os

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

