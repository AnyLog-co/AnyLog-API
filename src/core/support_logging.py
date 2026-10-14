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
        level:LevelMode|str - debug, info, warning, error (default), critical
        exception_type - exception class to raise (e.g. ValueError); RuntimeError if not given
        raise_exception:bool - whether to raise; None -> use FORCE_EXCEPTION. CRITICAL always raises
        cause - original exception, if re-raising from an except block
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


def update_service_name(service_name=SERVICE_NAME):
    global logger, SERVICE_NAME

    if service_name != SERVICE_NAME:
        SERVICE_NAME = service_name
        logger = logging.getLogger(service_name)

def update_force_exception(force_exception:bool=FORCE_EXCEPTION):
    global FORCE_EXCEPTION
    FORCE_EXCEPTION = force_exception

def update_minimal_level_mode(level_mode=DEFAULT_LevelMode):
    global MINIMAL_LevelMode
    if isinstance(level_mode, str):
        level_mode = LevelMode.__members__.get(level_mode.upper(), LevelMode.ERROR)
    MINIMAL_LevelMode = level_mode
