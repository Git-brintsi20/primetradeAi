"""Binance Futures Demo Trading client wrapper (CCXT).

Binance deprecated the old Futures Testnet in favour of "Demo Trading".
CCXT supports this natively via ``exchange.enable_demo_trading(True)``.
See: https://www.binance.com/en/support/faq/detail/9be58f73e5e14338809e3b705b9687dd
"""
import logging
import os
from typing import Any, Dict, List, Optional

import ccxt

logger = logging.getLogger(__name__)


class BinanceClient:
    """Thin wrapper around CCXT targeting Binance Futures Demo Trading (USDT-M)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("BINANCE_API_KEY", "")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET", "")

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API credentials are missing. "
                "Set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file "
                "or pass them explicitly."
            )

        logger.info("Initialising Binance Futures Demo Trading client…")

        self._exchange = ccxt.binance({
            "apiKey": self.api_key,
            "secret": self.api_secret,
            "options": {"defaultType": "future"},
            "enableRateLimit": True,
        })
        self._exchange.enable_demo_trading(True)

        logger.info(
            "Binance Futures Demo Trading client ready (base: %s).",
            self._exchange.urls.get("api", {}).get("fapiPrivate", "demo"),
        )

    # ------------------------------------------------------------------
    # Account
    # ------------------------------------------------------------------

    def get_account_balance(self) -> List[Dict[str, Any]]:
        """Return the list of asset balances for the futures account."""
        logger.info("Fetching account balance…")
        try:
            balance = self._exchange.fetch_balance({"type": "future"})
            # Flatten into a list similar to the old python-binance format
            result: List[Dict[str, Any]] = []
            for asset, amounts in balance.get("total", {}).items():
                total = float(amounts) if amounts else 0.0
                free = float(balance.get("free", {}).get(asset, 0))
                if total != 0 or free != 0:
                    result.append({
                        "asset": asset,
                        "balance": str(total),
                        "availableBalance": str(free),
                    })
            logger.info("Balance fetched — %d asset(s) returned.", len(result))
            return result
        except ccxt.BaseError as exc:
            logger.error("Error fetching balance: %s", exc)
            raise

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Place a futures order on Demo Trading.

        Args:
            symbol:     Trading pair (e.g. BTCUSDT).
            side:       BUY or SELL.
            order_type: MARKET, LIMIT, or STOP (stop-limit).
            quantity:   Order quantity.
            price:      Limit price (required for LIMIT and STOP orders).
            stop_price: Stop trigger price (required for STOP orders).

        Returns:
            Normalised order response dict.
        """
        # Map our order types to CCXT types
        ccxt_type = order_type.lower()  # ccxt expects 'market', 'limit'
        ccxt_side = side.lower()        # ccxt expects 'buy', 'sell'

        params: Dict[str, Any] = {}

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders.")
            ccxt_type = "limit"
        elif order_type == "STOP":
            if price is None:
                raise ValueError("Price is required for STOP orders.")
            if stop_price is None:
                raise ValueError("Stop price is required for STOP orders.")
            ccxt_type = "limit"
            params["stopPrice"] = stop_price
        else:
            ccxt_type = "market"
            price = None  # CCXT ignores price for market orders

        log_detail = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if price is not None:
            log_detail["price"] = price
        if stop_price is not None:
            log_detail["stopPrice"] = stop_price

        logger.info("Placing order — %s", log_detail)

        try:
            # CCXT expects symbol in "BTC/USDT:USDT" format for futures
            ccxt_symbol = self._to_ccxt_symbol(symbol)
            response = self._exchange.create_order(
                symbol=ccxt_symbol,
                type=ccxt_type,
                side=ccxt_side,
                amount=quantity,
                price=price,
                params=params,
            )
            # Normalise to a flat dict matching what our CLI/API expects
            result = self._normalise_response(response, order_type)
            logger.info(
                "Order placed — orderId=%s, status=%s",
                result.get("orderId"),
                result.get("status"),
            )
            return result
        except ccxt.BaseError as exc:
            logger.error("Error placing order: %s", exc)
            raise

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_ccxt_symbol(symbol: str) -> str:
        """Convert 'BTCUSDT' → 'BTC/USDT:USDT' for CCXT futures."""
        # Handle common USDT-M pairs
        if symbol.upper().endswith("USDT"):
            base = symbol[:-4]
            return f"{base}/USDT:USDT"
        if symbol.upper().endswith("BUSD"):
            base = symbol[:-4]
            return f"{base}/BUSD:BUSD"
        # Fallback: return as-is, CCXT might still handle it
        return symbol

    @staticmethod
    def _normalise_response(
        raw: Dict[str, Any], order_type: str
    ) -> Dict[str, Any]:
        """Map CCXT's unified order response to a flat dict for the CLI/API."""
        info = raw.get("info", {})
        return {
            "orderId": info.get("orderId", raw.get("id")),
            "symbol": info.get("symbol", raw.get("symbol", "")),
            "status": info.get("status", raw.get("status", "").upper()),
            "side": info.get("side", raw.get("side", "").upper()),
            "type": info.get("type", order_type),
            "origQty": info.get("origQty", str(raw.get("amount", ""))),
            "executedQty": info.get("executedQty", str(raw.get("filled", ""))),
            "avgPrice": info.get("avgPrice", str(raw.get("average", "") or "")),
            "price": info.get("price", str(raw.get("price", "") or "")),
        }
