"""
Custom logger for the library

Module heavily inspired from:
https://github.com/SergeyPirogov/webdriver_manager/blob/master/webdriver_manager/logger.py

Also thanks to this post for coloring the logs:
https://stackoverflow.com/a/56944256/10551772
"""
import logging
import os
from dataclasses import dataclass


# # Helpers

# +
@dataclass(frozen=True)
class LoggingLevel:
    method_name:str
    color:str


# string for resetting color that we will need to use for every log line
# (in the formatting as we do not want to change the message)
reset_color = "\x1b[0m"


# mapping/switch {level:LoggingLevel}
loggers = {}
log_method_switch = {logging.CRITICAL:LoggingLevel(method_name='critical', color="\x1b[31;1m"),  # bold red
                     logging.ERROR:LoggingLevel(method_name='error', color="\x1b[31;20m"),  # red
                     logging.WARNING:LoggingLevel(method_name='warning', color="\x1b[33;20m"),  # yellow
                     logging.INFO:LoggingLevel(method_name='info', color="\x1b[38;20m"),  # grey
                     logging.DEBUG:LoggingLevel(method_name='debug', color="\x1b[1;34m")}  # blue


# -

# # Main function

def log(text:str, name:str='npdoc_to_md', level:int=logging.INFO, exc_info:bool=False) -> None:
    """
    Logs given text to stderr (default of the logging library).

    Parameters
    ----------
    text
        Text to log
    name
        Name of the logger
    level
        See logging levels
        https://docs.python.org/3/library/logging.html#logging-levels
    exc_info
        Whether to include exceptions info

    Notes
    -----
    This is heavily inspired from:
    https://github.com/SergeyPirogov/webdriver_manager/blob/master/webdriver_manager/logger.py

    Examples
    --------
    * setting the log level of the library via an environment variable
    >>> import os, logging
    >>> from npdoc_to_md.logger import log
    >>> os.environ['NPDOC_TO_MD_LOG_LEVEL'] = str(logging.WARNING) # doctest: +SKIP
    >>>
    >>> # this won't log anything (INFO level < WARNING level)
    >>> log('info', level=logging.INFO) # doctest: +SKIP
    >>>
    >>> # this will log something
    >>> log('warn', level=logging.WARNING) # doctest: +SKIP
    """
    # get the appropriate log method (info, warning etc.)
    try:
        log_level:LoggingLevel = log_method_switch[level]
    except KeyError:  # pragma: no cover
        raise ValueError(f'{level} is not a valid log level. See https://docs.python.org/3/library/logging.html')

    # environment variable so user can customize the logging level of the library
    logger_level = os.getenv('NPDOC_TO_MD_LOG_LEVEL', logging.INFO)
    logger_level = int(logger_level) if isinstance(logger_level, str) else logger_level

    # init logger
    if name not in loggers:
        _logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(color)s%(asctime)s | %(levelname)s     '
                                      '| %(name)s    | %(module)s:%(funcName)s:%(lineno)s '
                                      f'- %(message)s{reset_color}')
        handler.setFormatter(formatter)
        _logger.addHandler(handler)
        _logger.setLevel(logger_level)
        loggers[name] = _logger

    # log
    getattr(loggers[name], log_level.method_name)(msg=text, exc_info=exc_info, extra={'color': log_level.color})
