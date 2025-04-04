# /config.py
import os
import logging

# API configuration
SIGNAL_STACK_WEBHOOK_URL = os.environ.get('SIGNAL_STACK_WEBHOOK_URL', 'https://app.signalstack.com/hook/eL6vejLLAiy1cDd888gevK')

# Trading configuration
MAX_SHARES = int(os.environ.get('MAX_SHARES', '5000'))
COOLDOWN_PERIOD_HOURS = int(os.environ.get('COOLDOWN_PERIOD_HOURS', '12'))
PAUSE_SECONDS = int(os.environ.get('PAUSE_SECONDS', '1'))

# Logging configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOGGING_FORMAT
)

logger = logging.getLogger('webhook-service')
