from dotenv import load_dotenv
import os
import asyncio
from api_gateway import ResilientAlpacaGateway

load_dotenv()  # This loads your .env file
print("APCA_API_KEY_ID:", os.getenv("APCA_API_KEY_ID"))
print("APCA_API_SECRET_KEY:", os.getenv("APCA_API_SECRET_KEY"))

# === API CONFIGURATION ===
API_CONFIG = {
    'alpaca_key_id': os.getenv('APCA_API_KEY_ID'),
    'alpaca_secret_key': os.getenv('APCA_API_SECRET_KEY'),
    'paper_trading': True,
    'request_timeout': 15,
    'max_retries': 3,
    'retry_backoff_factor': 2,
    'websocket_heartbeat_interval': 30
}

async def test():
    gateway = ResilientAlpacaGateway()
    success = await gateway.initialize()
    print(f'API Connection: {"SUCCESS" if success else "FAILED"}')
    await gateway.shutdown()

asyncio.run(test())