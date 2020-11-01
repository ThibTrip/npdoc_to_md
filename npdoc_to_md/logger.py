# +
import logging
import os

loggers = {}

def log(text, name='npdoc_to_md', msg_level='info', level=logging.INFO):
    """
    Logs given text to stderr (default of the logging library).

    Parameters
    ----------
    text : str
        Text to log
    name : str, default "npdoc_to_md"
        Name of the logger
    msg_level : str, default "info"
        Level for the given text (we will use logger.info or logger.warning etc
        depending on this argument)
    level : int, default logging.INFO

    Notes
    -----
    This is heavily inspired from:
    https://github.com/SergeyPirogov/webdriver_manager/blob/master/webdriver_manager/logger.py
    Examples
    --------
    >>> log('info')
    >>> import logging
    >>> log('warning!', level=logging.WARNING)
    """
    assert msg_level in ('debug', 'info', 'warning', 'error', 'exception', 'critical')
    # environment variable so user can customize the logging level of npdoc_to_md
    log_level = os.getenv('NPDOC_TO_MD_LOG_LEVEL')
    if log_level:
        level = int(log_level)
    # only add a handler if we do not have one (otherwise we'd have duplicated logs)
    if loggers.get(name):
        getattr(loggers.get(name), msg_level)(text)
    else:
        _logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s | %(levelname)s     '
                                      '| %(name)s    | %(module)s:%(funcName)s:%(lineno)s '
                                      '- %(message)s')
        handler.setFormatter(formatter)
        _logger.addHandler(handler)
        _logger.setLevel(level)
        loggers[name] = _logger
        getattr(_logger, msg_level)(text)
