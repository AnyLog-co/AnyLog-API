"""
Logging for AnyLog-API - every module logs (and optionally raises) through `async_exec_logging`

Environment:
    SERVICE_NAME - logger name (default: anylog-api)
    FORCE_EXCEPTION - "true" (default) raises after logging, "false" only logs
"""
from enum import Enum
import logging
import os


SERVICE_NAME = os.getenv("SERVICE_NAME", "anylog-api")
FORCE_EXCEPTION = True if os.getenv("FORCE_EXCEPTION", "true").lower().strip() == "true" else False

logger = logging.getLogger(SERVICE_NAME)

class LevelMode(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

MINIMAL_LevelMode = LevelMode.WARNING


async def async_exec_logging(message: str, level:LevelMode|str|None=MINIMAL_LevelMode,
                             exception_type: type[Exception] | None = None,
                             raise_exception: bool | None = None, cause: BaseException | None = None):
    """
    Log a message and optionally raise it as an exception
    :args:
        message:str - message to log
        level:LevelMode|str - debug, info, warning (default), error, critical; raised to MINIMAL_LevelMode if lower
        exception_type:type[Exception] - exception class to raise (ex. ValueError); RuntimeError if not given
        raise_exception:bool - whether to raise; None -> use FORCE_EXCEPTION. CRITICAL always raises
        cause:BaseException - original exception, if re-raising from an except block
    :return:
        None - when not raising
    :raise:
        exception_type (or RuntimeError) - see raise_exception
    """
    if raise_exception is None:
        raise_exception = FORCE_EXCEPTION
    if not level and MINIMAL_LevelMode:
        level = MINIMAL_LevelMode
    elif level and isinstance(level, str):
        level = LevelMode.__members__.get(level.upper(), LevelMode.ERROR)

    if level.value < MINIMAL_LevelMode.value:
       level = MINIMAL_LevelMode

    logger.log(level.value, message, exc_info=cause, stacklevel=2)

    if True in [raise_exception, FORCE_EXCEPTION]  or level == LevelMode.CRITICAL:
        raise (exception_type or RuntimeError)(message) from cause


def update_service_name(service_name:str=SERVICE_NAME):
    """
    Change the logger name
    :args:
        service_name:str - new logger name
    """
    global logger, SERVICE_NAME

    if service_name != SERVICE_NAME:
        SERVICE_NAME = service_name
        logger = logging.getLogger(service_name)


def update_force_exception(force_exception:bool=FORCE_EXCEPTION):
    """
    Change whether logged errors are also raised
    :args:
        force_exception:bool - True raises after logging, False only logs
    """
    global FORCE_EXCEPTION
    FORCE_EXCEPTION = force_exception


def update_minimal_level_mode(level_mode:LevelMode|str=MINIMAL_LevelMode):
    """
    Change the lowest level a message is logged at (lower levels are raised to it)
    :args:
        level_mode:LevelMode|str - debug, info, warning, error, critical (unknown strings -> error)
    """
    global MINIMAL_LevelMode
    if isinstance(level_mode, str):
        level_mode = LevelMode.__members__.get(level_mode.upper(), LevelMode.ERROR)
    MINIMAL_LevelMode = level_mode
