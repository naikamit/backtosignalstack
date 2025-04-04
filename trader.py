# /trader.py
import time
from signalstack import SignalStackClient
from state import TradeState
from config import MAX_SHARES, PAUSE_SECONDS, logger

class IterativeTrader:
    """
    Implements a trading strategy using an iterative approach to find the maximum 
    number of shares that can be bought.
    """
    
    def __init__(self, client=None, max_shares=None, pause_seconds=None):
        """
        Initialize the trader.
        
        Args:
            client (SignalStackClient, optional): The API client to use
            max_shares (int, optional): The initial number of shares to try
            pause_seconds (int, optional): Seconds to pause between API calls
        """
        self.client = client or SignalStackClient()
        self.max_shares = max_shares or MAX_SHARES
        self.pause_seconds = pause_seconds or PAUSE_SECONDS
        self.state = TradeState()
        logger.info(f"Initialized IterativeTrader with initial shares: {self.max_shares}")
    
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
        
        # Try to buy MSTU using iterative approach
        success = self.iterative_buy("MSTU")
        
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
        
        # Try to buy MSTZ using iterative approach
        success = self.iterative_buy("MSTZ")
        
        # If buy was successful, pause and close MSTU positions
        if success:
            self._pause()
            logger.info("Closing MSTU positions after successful MSTZ buy")
            self.client.close_positions("MSTU")
            self.state.set_successful_trade()
            return True
        
        logger.warning("Short signal strategy failed - could not buy any MSTZ shares")
        return False
    
    def iterative_buy(self, symbol):
        """
        Use iterative approach to buy as many shares as possible.
        Start with max_shares and keep trying to buy that amount.
        If buy fails, halve the quantity and try again.
        Continue until even a single share cannot be bought.
        
        Args:
            symbol (str): The stock symbol to buy
            
        Returns:
            bool: Whether any shares were successfully bought
        """
        logger.info(f"Starting iterative buy for {symbol}")
        
        quantity = self.max_shares
        any_success = False
        total_bought = 0
        
        # Continue until we can't buy even 1 share
        while quantity >= 1:
            logger.info(f"Trying to buy {quantity} shares of {symbol}")
            
            _, success = self.client.buy(symbol, quantity)
            
            if success:
                logger.info(f"Successfully bought {quantity} shares of {symbol}")
                total_bought += quantity
                any_success = True
                # Try to buy the same quantity again
                # No need to change quantity here
            else:
                logger.info(f"Failed to buy {quantity} shares of {symbol}")
                # Halve the quantity
                quantity = quantity // 2
            
            # Pause before next attempt
            self._pause()
        
        logger.info(f"Iterative buy complete. Total shares bought: {total_bought}")
        return any_success
    
    def _pause(self, seconds=None):
        """
        Pause execution for the specified number of seconds.
        
        Args:
            seconds (int, optional): Number of seconds to pause
        """
        pause_time = seconds if seconds is not None else self.pause_seconds
        logger.debug(f"Pausing for {pause_time} seconds")
        time.sleep(pause_time)
