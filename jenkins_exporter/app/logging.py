import logging
import os

DEBUG = int(os.environ.get("DEBUG", "0"))
logger = logging.getLogger("jenkins_exporter")
