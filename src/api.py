import logging
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from contextlib import asynccontextmanager

# Import Bot Components
from config import load_config
from upstox_client import UpstoxHandler
from market_data import MarketDataStreamer
from intelligence import IntelligenceModule
from strategy import GodfatherStrategy

logger = logging.getLogger("API")

# Global Bot State
bot_state = {
    "upstox": None,
    "brain": None,
    "strategy": None,
    "market_data": None,
    "running": False
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting HFT Bot API...")
    config = load_config()
    
    bot_state["upstox"] = UpstoxHandler(config)
    bot_state["brain"] = IntelligenceModule()
    bot_state["market_data"] = MarketDataStreamer(config)
    
    # Check Auth
    if bot_state["upstox"].validate_session():
        logger.info("Auth Valid.")
        bot_state["strategy"] = GodfatherStrategy(
            bot_state["upstox"], 
            bot_state["brain"], 
            config
        )
        # Hook Data
        bot_state["market_data"].on_message = bot_state["strategy"].on_tick
        
        # Start Background Tasks
        asyncio.create_task(run_intelligence_loop(bot_state["brain"]))
        asyncio.create_task(bot_state["market_data"].connect())
        bot_state["running"] = True
    else:
        logger.warning("Auth Invalid. Bot paused.")
        
    yield
    # Shutdown logic if needed

app = FastAPI(lifespan=lifespan)

# CORS for React App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow Netlify/Localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def run_intelligence_loop(brain):
    while True:
        try:
            await brain.scrape_news()
        except Exception as e:
            logger.error(f"Intelligence Loop Error: {e}")
        await asyncio.sleep(60)

@app.get("/")
def read_root():
    return {"status": "Godfather Bot Online", "running": bot_state["running"]}

@app.get("/metrics")
def get_metrics():
    """
    Get current bot metrics for the dashboard.
    """
    if not bot_state["strategy"]:
        return {"error": "Bot not initialized (Auth missing)"}
        
    strat = bot_state["strategy"]
    brain = bot_state["brain"]
    
    return {
        "positions": strat.positions,
        "sentiment": brain.sentiment_cache.get("market", 0.0),
        "active_orders": len(strat.active_orders),
        "pnl": 0.0 # TODO: Calculate Real PnL
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Push updates every second
            metrics = get_metrics()
            await websocket.send_json(metrics)
            await asyncio.sleep(1)
    except Exception as e:
        logger.info(f"WebSocket disconnected: {e}")
