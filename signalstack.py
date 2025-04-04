# /signalstack.py
import requests
import json
from config import SIGNAL_STACK_WEBHOOK_URL, logger

class SignalStackClient:
    """Client for interacting with the Signal Stack API."""
    
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or SIGNAL_STACK_WEBHOOK_URL
        logger.info(f"Initialized SignalStackClient with webhook URL: {self.webhook_url}")
    
    def buy(self, symbol, quantity):
        """
        Send a buy order to Signal Stack.
        
        Args:
            symbol (str): The stock symbol to buy
            quantity (int): The number of shares to buy
            
        Returns:
            tuple: (response_data, success_flag)
        """
        payload = {
            "symbol": symbol,
            "action": "buy",
            "quantity": quantity
        }
        
        logger.info(f"Attempting to buy {quantity} shares of {symbol}")
        
        try:
            response = self._send_request(payload)
            success = self._is_successful(response)
            
            if success:
                logger.info(f"Successfully bought {quantity} shares of {symbol}")
            else:
                logger.warning(f"Failed to buy {quantity} shares of {symbol}")
            
            return response, success
        
        except Exception as e:
            logger.error(f"Error buying {quantity} shares of {symbol}: {str(e)}")
            return {"error": str(e)}, False
    
    def close_positions(self, symbol):
        """
        Close all positions for a given symbol.
        
        Args:
            symbol (str): The stock symbol to close positions for
            
        Returns:
            dict: The API response
        """
        payload = {
            "symbol": symbol,
            "action": "close"
        }
        
        logger.info(f"Closing all positions for {symbol}")
        
        try:
            response = self._send_request(payload)
            logger.info(f"Close positions response for {symbol}: {response}")
            return response
        except Exception as e:
            logger.error(f"Error closing positions for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _send_request(self, payload):
        """
        Send a request to the Signal Stack API.
        
        Args:
            payload (dict): The request payload
            
        Returns:
            dict: The API response
        """
        logger.debug(f"Sending request to SignalStack: {payload}")
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            self.webhook_url,
            headers=headers,
            data=json.dumps(payload)
        )
        
        # Raise an exception for HTTP errors
        response.raise_for_status()
        
        # Parse and return the JSON response
        try:
            response_data = response.json()
        except ValueError:
            # If response is not JSON, create a dict with the response text
            response_data = {"response": response.text}
        
        logger.debug(f"Received response from SignalStack: {response_data}")
        
        return response_data
    
    def _is_successful(self, response):
        """
        Determine if an API response indicates a successful operation.
        
        Args:
            response (dict): The API response
            
        Returns:
            bool: Whether the operation was successful
        """
        # Check for common error indicators in the response
        if isinstance(response, dict):
            # Check for explicit success/error fields
            if response.get("success") is False:
                return False
            if "error" in response or "errors" in response:
                return False
            if response.get("status") == "error":
                return False
            
            # Check for HTTP status codes included in the response
            if response.get("status_code", 200) >= 400:
                return False
                
        # If no error indicators, assume success
        return True
