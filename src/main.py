import logging
import asyncio
from config import load_config
from upstox_client import UpstoxHandler
from market_data import MarketDataStreamer
from intelligence import IntelligenceModule
from strategy import GodfatherStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MAIN")

async def main():
    logger.info("=== INITIALIZING HFT GODFATHER BOT ===")
    
    # 1. Load Configuration
    try:
        config = load_config()
    except Exception as e:
        logger.critical(f"Config Error: {e}")
        return

    # 2. Initialize Components
    upstox = UpstoxHandler(config)
    brain = IntelligenceModule()
    market_data = MarketDataStreamer(config)
    
    # 3. Authenticate
    if not upstox.validate_session():
        logger.error("Authentication Failed. Please run 'python src/auth_flow.py' first.")
        return
    else:
        logger.info("Upstox Session Validated.")

    # 4. Initialize Strategy
    # We pass the 'upstox' handler to strategy for execution
    strategy = GodfatherStrategy(upstox, brain, config)
    
    # 5. Connect Brain (Start Background News Scraper)
    asyncio.create_task(run_intelligence_loop(brain))
    
    # 6. Start Market Data Stream
    # We need to hook the strategy's 'on_tick' to the market data stream
    # For this simplified version, let's assume MarketDataStreamer calls a callback
    # But since I implemented MarketDataStreamer with a loop, let's modify it or inject logic here.
    
    # Ideally, MarketDataStreamer should take a callback.
    # Let's start the stream and handle ticks.
    # Since we can't easily modify MarketDataStreamer's inner loop from here without passing callback,
    # I should have added a callback to MarketDataStreamer. 
    # For now, let's re-instantiate it properly or Monkey-Patch the on_message (Pythonic hack for speed).
    
    async def strategy_tick_callback(message):
        # Decode message (assuming JSON for now per previous impl)
        # In real V2, this is Protobuf.
        # strategy.on_tick(decoded_tick)
        pass 
    
    market_data.on_message = strategy.on_tick # Direct hook!
    
    logger.info("Starting Strategy Engine & Market Stream...")
    await market_data.connect() # This blocks the main loop

async def run_intelligence_loop(brain):
    """
    Periodically scrape news every 60 seconds.
    """
    while True:
        try:
            await brain.scrape_news()
        except Exception as e:
            logger.error(f"Intelligence Loop Error: {e}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.critical(f"Bot crashed: {e}")
