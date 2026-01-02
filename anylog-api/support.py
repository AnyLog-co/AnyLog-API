import json
import os
from http import HTTPStatus
from typing import Dict
import httpx

ROOT_PATH = os.path.dirname(__file__)


def load_json(file_path: str) -> Dict:
    full_path = os.path.expandvars(os.path.expanduser(file_path))
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert keys to int if numeric
    return {int(k): v for k, v in data.items()}


def url_builder(conn: str, is_auth: bool = False) -> str:
    if conn.startswith("http"):
        return conn
    scheme = "https" if is_auth else "http"
    return f"{scheme}://{conn}"


class NetworkErrorResolver:
    def __init__(self, errors: Dict[int, str], generic: Dict[int, str]):
        self.errors = errors
        self.generic = generic

    def resolve(self, status_code: int) -> str:
        if status_code in self.errors:
            return self.errors[status_code]

        category = status_code // 100
        if category in self.generic:
            return self.generic[category]

        try:
            return HTTPStatus(status_code).phrase
        except ValueError:
            return "Unknown Network Error"


def extract_response_content(response: httpx.Response):
    try:
        return response.json()
    except ValueError:
        return response.text
