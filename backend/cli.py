#!/usr/bin/env python3
"""CLI entry point — place orders and check balance on Binance Futures Testnet."""
import sys
from typing import Optional

import typer
from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.logging_config import setup_logging
from bot.orders import place_order as _place_order

load_dotenv()

LOG_FILE = "app.log"
logger = setup_logging(LOG_FILE)

app = typer.Typer(
    name="trading-bot",
    help="Binance Futures Testnet Trading Bot — place MARKET and LIMIT orders via CLI.",
    add_completion=False,
)

_DIVIDER = "=" * 52


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _print_response(response: dict) -> None:
    avg_price = response.get("avgPrice") or response.get("price") or "N/A"
    typer.echo(f"\n{_DIVIDER}")
    typer.echo("  Order Response")
    typer.echo(_DIVIDER)
    typer.echo(f"  Order ID      : {response.get('orderId')}")
    typer.echo(f"  Symbol        : {response.get('symbol')}")
    typer.echo(f"  Status        : {response.get('status')}")
    typer.echo(f"  Side          : {response.get('side')}")
    typer.echo(f"  Type          : {response.get('type')}")
    typer.echo(f"  Orig Qty      : {response.get('origQty')}")
    typer.echo(f"  Executed Qty  : {response.get('executedQty')}")
    typer.echo(f"  Avg Price     : {avg_price}")
    typer.echo(f"{_DIVIDER}\n")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def order(
    symbol: str = typer.Option(..., help="Trading pair, e.g. BTCUSDT"),
    side: str = typer.Option(..., help="BUY or SELL"),
    order_type: str = typer.Option(..., "--type", "-t", help="MARKET, LIMIT, or STOP"),
    quantity: float = typer.Option(..., help="Order quantity (e.g. 0.001)"),
    price: Optional[float] = typer.Option(
        None, help="Limit price — required for LIMIT and STOP orders"
    ),
    stop_price: Optional[float] = typer.Option(
        None, "--stop-price", help="Stop trigger price — required for STOP orders"
    ),
) -> None:
    """Place a futures order on Binance Futures Testnet."""
    typer.echo(f"\n{_DIVIDER}")
    typer.echo("  Order Request Summary")
    typer.echo(_DIVIDER)
    typer.echo(f"  Symbol     : {symbol.upper()}")
    typer.echo(f"  Side       : {side.upper()}")
    typer.echo(f"  Type       : {order_type.upper()}")
    typer.echo(f"  Quantity   : {quantity}")
    if price is not None:
        typer.echo(f"  Price      : {price}")
    if stop_price is not None:
        typer.echo(f"  Stop Price : {stop_price}")
    typer.echo(f"{_DIVIDER}\n")

    try:
        client = BinanceClient()
        response = _place_order(client, symbol, side, order_type, quantity, price, stop_price)
        typer.echo(
            typer.style("✅  Order placed successfully!", fg=typer.colors.GREEN, bold=True)
        )
        _print_response(response)
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        typer.echo(
            typer.style(f"❌  Validation Error: {exc}", fg=typer.colors.RED, bold=True),
            err=True,
        )
        raise typer.Exit(code=1)
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error placing order: %s", exc)
        typer.echo(
            typer.style(f"❌  Error: {exc}", fg=typer.colors.RED, bold=True),
            err=True,
        )
        raise typer.Exit(code=1)


@app.command()
def balance() -> None:
    """Fetch and display the futures account balance."""
    try:
        client = BinanceClient()
        balances = client.get_account_balance()

        typer.echo(f"\n{_DIVIDER}")
        typer.echo("  Account Balance")
        typer.echo(_DIVIDER)
        non_zero = [b for b in balances if float(b.get("balance", 0)) != 0]
        if non_zero:
            for b in non_zero:
                typer.echo(
                    f"  {b['asset']:<8}: {b['balance']:>18}  "
                    f"(available: {b['availableBalance']})"
                )
        else:
            typer.echo("  No non-zero balances found.")
        typer.echo(f"{_DIVIDER}\n")
    except Exception as exc:  # noqa: BLE001
        logger.error("Error fetching balance: %s", exc)
        typer.echo(
            typer.style(f"❌  Error: {exc}", fg=typer.colors.RED, bold=True),
            err=True,
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
