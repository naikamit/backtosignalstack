# /trader.py
import time
from signalstack import SignalStackClient
from state import TradeState
from config import MAX_SHARES, PAUSE_SECONDS, logger

class BinarySearchTrader:
    """
    Implements a trading strategy using binary search to find the maximum 
    number of shares that can be bought.
    """
    
    def __init__(self, client=None, max_shares=None, pause_seconds=None):
        """
        Initialize the trader.
        
        Args:
            client (SignalStackClient, optional): The API client to use
            max_shares (int, optional): The maximum number of shares to start with
            pause_seconds (int, optional): Seconds to pause between API calls
        """
        self.client = client or SignalStackClient()
        self.max_shares = max_shares or MAX_SHARES
        self.pause_seconds = pause_seconds or PAUSE_SECONDS
        self.state = TradeState()
        logger.info(f"Initialized BinarySearchTrader with max_shares: {self.max_shares}")
    
    def is_in_cooldown(self):
        """
        Check if we're in the cooldown period.
        
        Returns:
            bool: True if in cooldown, False otherwise
        """
        return self.state.is_in_cooldown()
    
    def execute_long_signal(self):
        """
        Execute the trading strategy for a long signal.
        Buy MSTU and close MSTZ positions.
        
        Returns:
            bool: True if the strategy was executed successfully
        """
        logger.info("Executing long signal strategy")
        
        # If in cooldown period, close both positions
        if self.state.is_in_cooldown():
            logger.info("In cooldown period - closing both MSTU and MSTZ positions")
            self.client.close_positions("MSTU")
            self.client.close_positions("MSTZ")
            return True
        
        # Try to buy MSTU using binary search
        success = self.binary_search_buy("MSTU")
        
        # If buy was successful, pause and close MSTZ positions
        if success:
            self._pause()
            logger.info("Closing MSTZ positions after successful MSTU buy")
            self.client.close_positions("MSTZ")
            self.state.set_successful_trade()
            return True
        
        logger.warning("Long signal strategy failed - could not buy any MSTU shares")
        return False
    
    def execute_short_signal(self):
        """
        Execute the trading strategy for a short signal.
        Buy MSTZ and close MSTU positions.
        
        Returns:
            bool: True if the strategy was executed successfully
        """
        logger.info("Executing short signal strategy")
        
        # If in cooldown period, close both positions
        if self.state.is_in_cooldown():
            logger.info("In cooldown period - closing both MSTU and MSTZ positions")
            self.client.close_positions("MSTU")
            self.client.close_positions("MSTZ")
            return True
        
        # Try to buy MSTZ using binary search
        success = self.binary_search_buy("MSTZ")
        
        # If buy was successful, pause and close MSTU positions
        if success:
            self._pause()
            logger.info("Closing MSTU positions after successful MSTZ buy")
            self.client.close_positions("MSTU")
            self.state.set_successful_trade()
            return True
        
        logger.warning("Short signal strategy failed - could not buy any MSTZ shares")
        return False
    
    def binary_search_buy(self, symbol):
        """
        Use binary search to find and buy the maximum number of shares possible.
        
        Args:
            symbol (str): The stock symbol to buy
            
        Returns:
            bool: Whether any shares were successfully bought
        """
        logger.info(f"Starting binary search to buy maximum shares of {symbol}")
        
        low = 1
        high = self.max_shares
        max_successful_quantity = 0
        
        while low <= high:
            mid = (low + high) // 2
            logger.info(f"Trying to buy {mid} shares of {symbol}")
            
            _, success = self.client.buy(symbol, mid)
            
            if success:
                logger.info(f"Successfully bought {mid} shares of {symbol}")
                max_successful_quantity = mid
                low = mid + 1  # Try a larger quantity
            else:
                logger.info(f"Failed to buy {mid} shares of {symbol}")
                high = mid - 1  # Try a smaller quantity
            
            # Pause before next attempt
            self._pause()
        
        if max_successful_quantity > 0:
            logger.info(f"Binary search complete. Maximum shares bought: {max_successful_quantity}")
            return True
        else:
            logger.warning(f"Binary search complete. Could not buy any shares of {symbol}")
            return False
    
    def _pause(self, seconds=None):
        """
        Pause execution for the specified number of seconds.
        
        Args:
            seconds (int, optional): Number of seconds to pause
        """
        pause_time = seconds if seconds is not None else self.pause_seconds
        logger.debug(f"Pausing for {pause_time} seconds")
        time.sleep(pause_time)
