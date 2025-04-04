# Webhook Trading Service

A simple webhook service that receives long/short signals and executes trading strategies via the Signal Stack API.

## Features

- Receives webhook signals for long/short trading strategies
- Uses iterative approach to buy maximum possible shares
- Implements cooldown period after successful trades
- Detailed logging for debugging
- Stateless design with no database dependency

## Buy Strategy

The service uses the following approach to buy shares:
- Start with a quantity of MAX_SHARES (default: 5000)
- Try to buy that quantity
- If successful, try to buy the same quantity again
- If unsuccessful, halve the quantity and try again
- Continue until a single share cannot be bought

## Deployment on Render

### Environment Variables

Set the following environment variables in the Render dashboard:

| Variable | Description | Default |
|----------|-------------|---------|
| `SIGNAL_STACK_WEBHOOK_URL` | URL for the Signal Stack API | https://app.signalstack.com/hook/eL6vejLLAiy1cDd888gevK |
| `MAX_SHARES` | Initial number of shares to attempt to buy | 5000 |
| `COOLDOWN_PERIOD_HOURS` | Hours after a successful trade to close all positions | 12 |
| `PAUSE_SECONDS` | Seconds to pause between API calls | 1 |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `PORT` | Port for the web server | 5000 |

### Build Command

```
pip install -r requirements.txt
```

### Start Command

```
gunicorn app:app
```

## Endpoints

- `POST /webhook`: Receive trading signals
  - Expected payload: `{"signal": "long"}` or `{"signal": "short"}`
- `GET /health`: Health check endpoint

## Testing Locally

To run locally:

```bash
# Set environment variables (optional)
export MAX_SHARES=5000
export LOG_LEVEL=DEBUG

# Run the application
python app.py
```

To test the webhook:

```bash
# Test long signal
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"long"}'

# Test short signal
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"short"}'

# Check health status
curl http://localhost:5000/health
```
