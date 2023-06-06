from app.localdt import utc
from app.logging import LOG_DIR, createLogger

import os

logPreFname = os.path.join(os.getcwd(), LOG_DIR, "update-" + utc.now().strftime("%Y-%m-%d"))
logFname = logPreFname + ".log"
count = 1
while os.path.exists(logFname):
	count += 1
	logFname = f"{logPreFname}({count}).log"

logger = createLogger(__name__, logFname)
