"""统一日志工具（替换原 fortune_service.py 的 print 式日志）。"""
import logging
import sys

logger = logging.getLogger('fortune')
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter(
        '[%(levelname)s] %(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


def log_info(msg):
    logger.info(msg)


def log_error(msg):
    logger.error(msg)


def log_debug(msg):
    logger.debug(msg)


def log_warning(msg):
    logger.warning(msg)
