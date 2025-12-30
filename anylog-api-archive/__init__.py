"""
AnyLog API package for REST and async-based communication.
"""

from .anylog_connector import AnyLogConnector
from .async_anylog_connector import AnyLogConnector as AsyncAnyLogConnector

__all__ = ["AnyLogConnector", "AsyncAnyLogConnector"]
