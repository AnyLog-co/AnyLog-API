class AnyLogError(Exception):
    """Base for all AnyLog-API errors."""

class AnyLogConnectionError(AnyLogError, ConnectionError):
    """Could not reach the node (DNS, refused connection, bad URL, ...)."""

class AnyLogTimeoutError(AnyLogError, TimeoutError):
    """Node did not respond within the configured timeout."""

class AnyLogHTTPError(AnyLogError):
    """Node responded with a non-2xx status."""
    def __init__(self, messag:str, status_code:int|None=None):
        super().__init__(message)
        self.status_code = status_code