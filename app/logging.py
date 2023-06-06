from app import app
from app.constants import LOG_FORMAT, LOG_DATE_FORMAT, LOG_DIR
from app.localdt import utc

import logging
import os

#
# Config
#

try:
	LOG_LEVEL = logging._nameToLevel[app.config["LOG_LEVEL"].upper()]
except KeyError:
	LOG_LEVEL = logging.INFO

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

logFormatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
logging.Formatter.converter = utc.converter()

if not os.path.exists(LOG_DIR):
	os.makedirs(LOG_DIR)

#
# Util funcs
#

def getLogFileHandler(fname: str, dirname=LOG_DIR, formatter=logFormatter):
	if not os.path.exists(LOG_DIR):
		os.makedirs(LOG_DIR)

	path = os.path.join(dirname, fname)
	handler = logging.FileHandler(path)
	handler.setFormatter(formatter)

	return handler

def createLogger(name: str, fname: str, dirname=LOG_DIR, formatter=logFormatter):
	_logger = logging.getLogger(name)

	_logger.addHandler(getLogFileHandler(fname, dirname, formatter))

	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(logFormatter)
	_logger.addHandler(consoleHandler)

	return _logger
