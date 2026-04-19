from typing import List, Dict, Any, Callable, Optional
import asyncio
import websockets
import json
import logging
import time

logger = logging.getLogger("sats.binance_ws")

async def _connect_ws(uri: str, on_message: Callable, on_error: Callable, on_close: Callable):
    try:
        async with websockets.connect(uri) as ws:
            logger.info(f"WebSocket connected to {uri}")
            try:
                while True:
                    message = await ws.recv()
                    on_message(message)
            except websockets.exceptions.ConnectionClosedOK:
                logger.info("WebSocket connection closed normally.")
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"WebSocket connection closed with error: {e}")
                on_error(e)
            finally:
                on_close()
    except Exception as e:
        logger.error(f"WebSocket connection failed: {e}")
        on_error(e)

class BinanceWSManager:
    def __init__(self, symbols: List[str], interval: str, on_kline_callback: Callable, reconnect_delay: int = 5, max_reconnect: int = 10):
        self.symbols = symbols
        self.interval = interval
        self.on_kline_callback = on_kline_callback
        self.reconnect_delay = reconnect_delay
        self.max_reconnect = max_reconnect
        self._ws_uri = "wss://fstream.binance.com/ws"
        self._ws_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def start(self):
        self._is_running = True
        self._ws_task = asyncio.create_task(
            _connect_ws(self._ws_uri, self._on_message, self._on_error, self._on_close)
        )
        await self._subscribe_all_symbols()

    async def stop(self):
        self._is_running = False
        if self._ws_task:
            self._ws_task.cancel()
            await self._ws_task

    async def _subscribe_all_symbols(self):
        if not self.symbols:
            logger.warning("No symbols to subscribe.")
            return
        
        streams = []
        for symbol in self.symbols:
            streams.append(f"{symbol.lower()}@kline_{self.interval}")
        
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": 1
        }
        
        # This part needs a live websocket connection to send the message
        # For now, we'll just log it.
        logger.info(f"Subscribing to: {subscribe_message}")

    def _on_message(self, message: str):
        data = json.loads(message)
        if "e" in data and data["e"] == "kline":
            kline_data = data["k"]
            kline = {
                "open": float(kline_data["o"]),
                "high": float(kline_data["h"]),
                "low": float(kline_data["l"]),
                "close": float(kline_data["c"]),
                "volume": float(kline_data["v"]),
                "is_closed": kline_data["x"]
            }
            self.on_kline_callback(kline_data["s"], kline)

    def _on_error(self, error: Any):
        logger.error(f"WebSocket error: {error}")

    def _on_close(self):
        logger.info("WebSocket connection closed.")
        if self._is_running:
            logger.info("Attempting to reconnect WebSocket...")
            # In a real implementation, you'd want a more robust reconnection strategy
            asyncio.create_task(self.start())

import requests

BINANCE_FUTURES_API_URL = "https://fapi.binance.com/fapi/v1/klines"

def fetch_historical_klines(symbol: str, interval: str, limit: int) -> List[Dict[str, Any]]:
    try:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        response = requests.get(BINANCE_FUTURES_API_URL, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        klines = response.json()

        formatted_klines = []
        for kline in klines:
            formatted_klines.append({
                "open_time": kline[0],
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5]),
                "close_time": kline[6],
                "quote_asset_volume": float(kline[7]),
                "number_of_trades": int(kline[8]),
                "taker_buy_base_asset_volume": float(kline[9]),
                "taker_buy_quote_asset_volume": float(kline[10]),
                "ignore": float(kline[11])
            })
        return formatted_klines
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching historical klines for {symbol}: {e}")
        return []

def validate_symbols(symbols: List[str], interval: str) -> tuple[List[str], List[str]]:
    # Placeholder for validating symbols
    logger.warning(f"Symbol validation for {symbols} is not fully implemented. Assuming all are valid for now.")
    # In a real scenario, you would check each symbol against the exchange's available symbols
    # For now, return all as valid and an empty list for invalid
    return symbols, []

def fetch_top_symbols(top_n: int, quote: str) -> List[str]:
    # Placeholder for fetching top symbols
    logger.warning(f"Fetching top {top_n} symbols with quote {quote} is not implemented.")
    return []
