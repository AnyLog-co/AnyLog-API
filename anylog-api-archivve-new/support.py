import json
import os
from http import HTTPStatus
from typing import Dict
import httpx

ROOT_PATH = os.path.dirname(__file__)




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
