# /app.py
import os
from flask import Flask, request, jsonify
import logging
from config import logger
from trader import BinarySearchTrader

app = Flask(__name__)
trader = BinarySearchTrader()

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle incoming webhook signals.
    
    Expected JSON format:
    {
        "signal": "long" or "short"
    }
    """
    try:
        data = request.json
        logger.info(f"Received webhook data: {data}")
        
        if not data or "signal" not in data:
            logger.warning("Invalid webhook data: 'signal' field is missing")
            return jsonify({"status": "error", "message": "Invalid data format. 'signal' field is required."}), 400
        
        signal = data["signal"].lower()
        
        if signal == "long":
            logger.info("Processing LONG signal")
            status = trader.execute_long_signal()
            return jsonify({"status": "success", "message": "Long signal processed", "cooldown": trader.is_in_cooldown()})
        
        elif signal == "short":
            logger.info("Processing SHORT signal")
            status = trader.execute_short_signal()
            return jsonify({"status": "success", "message": "Short signal processed", "cooldown": trader.is_in_cooldown()})
        
        else:
            logger.warning(f"Unknown signal type: {signal}")
            return jsonify({"status": "error", "message": f"Unknown signal type: {signal}"}), 400
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"Internal error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint.
    """
    return jsonify({"status": "ok", "cooldown": trader.is_in_cooldown()})

if __name__ == '__main__':
    # Use PORT environment variable if available, otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
