"""Order placement logic — validates inputs then delegates to BinanceClient."""
import logging
from typing import Any, Dict, Optional

from .client import BinanceClient
from .validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = logging.getLogger(__name__)


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> Dict[str, Any]:
    """Validate inputs and place a futures order via *client*.

    Args:
        client:     An initialised :class:`BinanceClient`.
        symbol:     Trading pair, e.g. ``BTCUSDT``.
        side:       ``BUY`` or ``SELL``.
        order_type: ``MARKET``, ``LIMIT``, or ``STOP`` (stop-limit).
        quantity:   Order quantity (must be positive).
        price:      Limit price — required for ``LIMIT`` and ``STOP`` orders.
        stop_price: Stop trigger price — required for ``STOP`` orders.

    Returns:
        Raw order response dict from the Binance API.

    Raises:
        ValueError: On invalid input.
        BinanceAPIException: On API-level errors.
        BinanceRequestException: On network-level errors.
    """
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)
    stop_price = validate_stop_price(stop_price, order_type)

    logger.info(
        "Order request — symbol=%s, side=%s, type=%s, qty=%s, price=%s, stopPrice=%s",
        symbol,
        side,
        order_type,
        quantity,
        price,
        stop_price,
    )

    return client.place_order(symbol, side, order_type, quantity, price, stop_price)
