"""Input validation helpers for the trading bot."""
from typing import Optional

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_symbol(symbol: str) -> str:
    """Validate and normalise a trading symbol (e.g., BTCUSDT)."""
    if not symbol or not symbol.isalpha():
        raise ValueError(
            f"Invalid symbol: '{symbol}'. "
            "Must be a non-empty alphabetic string (e.g., BTCUSDT)."
        )
    return symbol.upper()


def validate_side(side: str) -> str:
    """Validate order side (BUY or SELL)."""
    side_upper = side.upper()
    if side_upper not in VALID_SIDES:
        raise ValueError(
            f"Invalid side: '{side}'. Must be one of {sorted(VALID_SIDES)}."
        )
    return side_upper


def validate_order_type(order_type: str) -> str:
    """Validate order type (MARKET or LIMIT)."""
    order_type_upper = order_type.upper()
    if order_type_upper not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type: '{order_type}'. "
            f"Must be one of {sorted(VALID_ORDER_TYPES)}."
        )
    return order_type_upper


def validate_quantity(quantity: float) -> float:
    """Validate that quantity is a positive number."""
    if quantity <= 0:
        raise ValueError(
            f"Invalid quantity: {quantity}. Must be a positive number."
        )
    return quantity


def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    """Validate price field.

    Price is required and must be positive for LIMIT orders.
    For MARKET orders it is ignored.
    """
    if order_type.upper() == "LIMIT":
        if price is None or price <= 0:
            raise ValueError(
                "Price is required and must be a positive number for LIMIT orders."
            )
    return price
