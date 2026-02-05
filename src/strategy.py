import logging
import pandas as pd
import asyncio
from indicators import TechnicalIndicators
from datetime import datetime

logger = logging.getLogger("StrategyEngine")

class GodfatherStrategy:
    """
    The 'Godfather' HFT Strategy.
    Pillars:
    1. Trend (VWAP)
    2. Momentum (RSI + Volume)
    3. Intelligence (Sentiment)
    4. Time (Decay protection)
    """
    def __init__(self, client, intelligence_module, config):
        self.client = client
        self.brain = intelligence_module
        self.config = config
        self.positions = {} # Symbol -> Position Data
        self.active_orders = {}
        
        # Parameters
        self.timeframe = '1min' # HFT requires fast candles
        self.rsi_period = 14
        self.atr_period = 14
        self.vol_ma_period = 20
        self.min_sentiment_score = 0.1
        
    async def on_tick(self, tick_data):
        """
        Called on every WebSocket tick.
        HFT Logic: Check if we need to escape immediately.
        """
        symbol = tick_data['symbol']
        current_price = tick_data['ltp']
        
        if symbol in self.positions:
            await self.manage_risk(symbol, current_price)

    async def on_candle(self, symbol, df_candles):
        """
        Called when a new 1-min candle is closed.
        Main Entry Logic.
        """
        # 1. Calculate Indicators
        df = df_candles.copy()
        
        # Check sufficient data
        if len(df) < 50:
            return # Need history for MA/RSI
            
        df['vwap'] = TechnicalIndicators.calculate_vwap(df)
        df['rsi'] = TechnicalIndicators.calculate_rsi(df, self.rsi_period)
        df['atr'] = TechnicalIndicators.calculate_atr(df, self.atr_period)
        df['vol_sma'] = TechnicalIndicators.calculate_sma_volume(df, self.vol_ma_period)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Get Global Sentiment
        sentiment_score = self.brain.sentiment_cache.get('market', 0.0)
        
        # 2. LONG Signal Logic
        # Condition A: Price > VWAP (Trend is Up)
        cond_trend_up = latest['close'] > latest['vwap']
        
        # Condition B: High Volume (Volume Spike > 200% of Avg)
        cond_vol_surge = latest['volume'] > (latest['vol_sma'] * 2.0)
        
        # Condition C: RSI not overbought (< 70) but rising
        cond_rsi_ok = 50 < latest['rsi'] < 75
        
        # Condition D: Sentiment Positive
        cond_sent_ok = sentiment_score > self.min_sentiment_score
        
        if cond_trend_up and cond_vol_surge and cond_rsi_ok and cond_sent_ok:
            if symbol not in self.positions:
                logger.info(f"GODFATHER SIGNAL [LONG]: {symbol} @ {latest['close']}")
                await self.execute_trade(symbol, "BUY", latest['close'], latest['atr'])

        # 3. SHORT Signal Logic
        # Condition A: Price < VWAP (Trend is Down)
        cond_trend_down = latest['close'] < latest['vwap']
        
        # Condition D: Sentiment Negative
        cond_sent_neg = sentiment_score < -self.min_sentiment_score
        
        if cond_trend_down and cond_vol_surge and (latest['rsi'] < 50) and cond_sent_neg:
             if symbol not in self.positions:
                logger.info(f"GODFATHER SIGNAL [SHORT]: {symbol} @ {latest['close']}")
                await self.execute_trade(symbol, "SELL", latest['close'], latest['atr'])

    async def execute_trade(self, symbol, side, price, atr):
        """
        Execute trade with automated Stop Loss and Target.
        """
        # Position Sizing (Risk 1% of capital per trade - Example placeholder)
        quantity = 1 # TODO: Calculate based on Risk Manager
        
        sl_price = price - (1.5 * atr) if side == "BUY" else price + (1.5 * atr)
        tgt_price = price + (3.0 * atr) if side == "BUY" else price - (3.0 * atr)
        
        logger.info(f"Placing {side} Order: {symbol} Qty: {quantity} SL: {sl_price:.2f} TGT: {tgt_price:.2f}")
        
        # Place Main Order
        # order_id = await self.client.place_order(...) 
        
        # Store in self.positions
        self.positions[symbol] = {
            "side": side,
            "entry_price": price,
            "entry_time": datetime.now(),
            "quantity": quantity,
            "sl": sl_price,
            "tgt": tgt_price
        }

    async def manage_risk(self, symbol, current_ltp):
        """
        Active Position Management.
        """
        pos = self.positions[symbol]
        
        # 1. Hard Stop Loss Check
        if pos['side'] == "BUY" and current_ltp <= pos['sl']:
            await self.close_position(symbol, "SL Hit")
        elif pos['side'] == "SELL" and current_ltp >= pos['sl']:
            await self.close_position(symbol, "SL Hit")
            
        # 2. Target Hit Check
        if pos['side'] == "BUY" and current_ltp >= pos['tgt']:
            await self.close_position(symbol, "Target Hit")
        elif pos['side'] == "SELL" and current_ltp <= pos['tgt']:
            await self.close_position(symbol, "Target Hit")
            
        # 3. Time Decay (Escape Logic)
        # If trade is open > 5 mins and profit is < 0.2%, KILL IT.
        time_elapsed = (datetime.now() - pos['entry_time']).total_seconds() / 60
        if time_elapsed > 5.0:
            # Check pnl
            pnl_pct = (current_ltp - pos['entry_price']) / pos['entry_price']
            if pos['side'] == "SELL": pnl_pct *= -1
            
            if pnl_pct < 0.002: # Less than 0.2% profit after 5 mins
                logger.info(f"Time Decay Escape: {symbol} stagnant for 5 mins.")
                await self.close_position(symbol, "Time Stop")

    async def close_position(self, symbol, reason):
        logger.info(f"Closing Position {symbol}: {reason}")
        # await self.client.exit_position(...)
        del self.positions[symbol]

