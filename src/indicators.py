import pandas as pd
import pandas_ta as ta

class TechnicalIndicators:
    """
    Wrapper for Technical Analysis calculations.
    Uses pandas_ta for speed and reliability.
    """
    
    @staticmethod
    def calculate_vwap(df):
        """
        Calculate Volume Weighted Average Price (VWAP).
        Expects DataFrame with 'high', 'low', 'close', 'volume'.
        """
        # Pandas-TA vwap requires datetime index or specific config, 
        # usually it's ta.vwap(high, low, close, volume)
        try:
            vwap = ta.vwap(df['high'], df['low'], df['close'], df['volume'])
            return vwap
        except Exception as e:
            print(f"Error calculating VWAP: {e}")
            return None

    @staticmethod
    def calculate_atr(df, length=14):
        """
        Calculate Average True Range (ATR) for volatility.
        """
        try:
            atr = ta.atr(df['high'], df['low'], df['close'], length=length)
            return atr
        except Exception as e:
            print(f"Error calculating ATR: {e}")
            return None

    @staticmethod
    def calculate_rsi(df, length=14):
        """
        Calculate Relative Strength Index (RSI).
        """
        try:
            rsi = ta.rsi(df['close'], length=length)
            return rsi
        except Exception as e:
            print(f"Error calculating RSI: {e}")
            return None

    @staticmethod
    def calculate_sma_volume(df, length=20):
        """
        Calculate Simple Moving Average of Volume.
        """
        try:
            vol_sma = ta.sma(df['volume'], length=length)
            return vol_sma
        except Exception as e:
            print(f"Error calculating Vol SMA: {e}")
            return None
