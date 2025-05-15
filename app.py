from WasteDetection.logger import logging
from WasteDetection.exception import AppException

# logging.info("*** Starting Custom Logs ***")

try:
    x = 5/0
    print(x)
except Exception as e:
    raise AppException(e)