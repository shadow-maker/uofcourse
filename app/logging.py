from app.constants import LOG_FORMAT, LOG_DATE_FORMAT, LOG_DIR
from app.localdt import utc

import logging
import os

#
# Config
#

LOG_LEVEL = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

logFormatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
logging.Formatter.converter = utc.converter()

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)

logger.addHandler(consoleHandler)

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

def setLogFileHandler(logger: logging.Logger, fname: str, dirname=LOG_DIR, formatter=logFormatter):
	logger.addHandler(getLogFileHandler(fname, dirname, formatter))
