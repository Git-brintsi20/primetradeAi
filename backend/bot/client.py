"""Binance Futures Testnet client wrapper."""
import logging
import os
from typing import Any, Dict, List, Optional

from binance import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = logging.getLogger(__name__)

# Binance Futures Testnet base URL
FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    """Thin wrapper around python-binance targeting the Futures Testnet (USDT-M)."""

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

        logger.info("Initialising Binance Futures Testnet client…")
        self._client = Client(self.api_key, self.api_secret)

        # Redirect all futures calls to the testnet endpoint
        self._client.FUTURES_URL = f"{FUTURES_TESTNET_BASE_URL}/fapi"
        logger.info("Binance Futures Testnet client ready.")

    # ------------------------------------------------------------------
    # Account
    # ------------------------------------------------------------------

    def get_account_balance(self) -> List[Dict[str, Any]]:
        """Return the list of asset balances for the futures account."""
        logger.info("Fetching account balance…")
        try:
            balance = self._client.futures_account_balance()
            logger.info("Balance fetched — %d asset(s) returned.", len(balance))
            return balance
        except BinanceAPIException as exc:
            logger.error("API error while fetching balance: %s", exc)
            raise
        except BinanceRequestException as exc:
            logger.error("Network error while fetching balance: %s", exc)
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
    ) -> Dict[str, Any]:
        """Place a futures order on the testnet.

        Args:
            symbol:     Trading pair (e.g. BTCUSDT).
            side:       BUY or SELL.
            order_type: MARKET or LIMIT.
            quantity:   Order quantity.
            price:      Limit price (required when order_type == LIMIT).

        Returns:
            Raw API response dict.
        """
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = "GTC"

        logger.info("Placing order — %s", params)

        try:
            response = self._client.futures_create_order(**params)
            logger.info(
                "Order placed — orderId=%s, status=%s",
                response.get("orderId"),
                response.get("status"),
            )
            return response
        except BinanceAPIException as exc:
            logger.error(
                "API error placing order: %s — %s", exc.status_code, exc.message
            )
            raise
        except BinanceRequestException as exc:
            logger.error("Network error placing order: %s", exc)
            raise
