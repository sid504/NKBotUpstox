import os
from dotenv import load_dotenv

def load_config():
    """
    Load configuration from .env file and environment variables.
    """
    load_dotenv()
    
    config = {
        "UPSTOX_API_KEY": os.getenv("UPSTOX_API_KEY"),
        "UPSTOX_API_SECRET": os.getenv("UPSTOX_API_SECRET"),
        "UPSTOX_REDIRECT_URI": os.getenv("UPSTOX_REDIRECT_URI", "http://localhost:3000"),
        "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN"),  # Optionally store token to reuse
        "RISK_MAX_DAILY_LOSS": float(os.getenv("RISK_MAX_DAILY_LOSS", 2.0)), # Percentage
        "TRADING_SYMBOL_LIST": os.getenv("TRADING_SYMBOL_LIST", "NSE_EQ|RELIANCE,NSE_EQ|TCS").split(","),
    }
    
    if not config["UPSTOX_API_KEY"] or not config["UPSTOX_API_SECRET"]:
        raise ValueError("Missing UPSTOX_API_KEY or UPSTOX_API_SECRET in .env file")
        
    return config
