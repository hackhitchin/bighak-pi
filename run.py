import logging
import logging.handlers

from bighak.bighak import Dashboard

LOG_FILENAME = 'bighak.log'

# Set up a specific logger with our desired output level
my_logger = logging.getLogger('bighak')
my_logger.setLevel(logging.DEBUG)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                               maxBytes=5242880,
                                               backupCount=5,
                                               )
my_logger.addHandler(handler)

dashboard = Dashboard()

try:
    dashboard.start()
except:
    dashboard.shut_down()
