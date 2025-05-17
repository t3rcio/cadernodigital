import os
from datetime import datetime
from decouple import config

FORMAT_DATE = '%Y-%m-%d'
FORMAT_DATE_TIME = '%Y-%m-%d_%H:%M:%S'
LOG_PATH = os.path.join('./', '.logs')
LOG_FILE = '{}.log'.format(datetime.now().strftime(FORMAT_DATE_TIME))
LOG_FILENAME = os.path.join(LOG_PATH, LOG_FILE)
GOOGLE_API_KEY = config('GOOGLE_API_KEY')

