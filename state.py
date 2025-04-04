# /state.py
from datetime import datetime, timedelta
from config import COOLDOWN_PERIOD_HOURS, logger

class TradeState:
    """
    Manages the in-memory state of the trading system.
    """
    
    def __init__(self):
        # The time of the last successful trade
        self.last_successful_trade_time = None
    
    def is_in_cooldown(self):
        """
        Check if we're within the cooldown period after a successful trade.
        
        Returns:
            bool: True if in cooldown period, False otherwise
        """
        if self.last_successful_trade_time is None:
            return False
            
        cooldown_end_time = self.last_successful_trade_time + timedelta(hours=COOLDOWN_PERIOD_HOURS)
        now = datetime.now()
        
        in_cooldown = now < cooldown_end_time
        
        if in_cooldown:
            remaining = (cooldown_end_time - now).total_seconds() / 3600  # hours
            logger.info(f"In cooldown period. {remaining:.2f} hours remaining.")
        
        return in_cooldown
    
    def set_successful_trade(self):
        """
        Mark that a successful trade has occurred, starting the cooldown period.
        """
        self.last_successful_trade_time = datetime.now()
        cooldown_end = self.last_successful_trade_time + timedelta(hours=COOLDOWN_PERIOD_HOURS)
        logger.info(f"Cooldown period started. Will last until {cooldown_end}")
