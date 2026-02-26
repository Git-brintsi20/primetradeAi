#!/usr/bin/env python3
"""FastAPI server — bridges the Python trading-bot backend to the frontend."""
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.logging_config import setup_logging
from bot.orders import place_order as _place_order

load_dotenv()

LOG_FILE = str(Path(__file__).parent / "app.log")
logger = setup_logging(LOG_FILE)

app = FastAPI(
    title="PrimetradeAI – Binance Futures Bot",
    description="REST API that wraps Binance Futures Demo Trading order placement.",
    version="1.0.0",
)

# Allow all origins so the frontend (any port / domain) can talk to this server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _get_client() -> BinanceClient:
    """Return a cached BinanceClient singleton (credentials from env-vars)."""
    return BinanceClient()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class OrderRequest(BaseModel):
    symbol: str = Field(..., examples=["BTCUSDT"], description="Trading pair")
    side: str = Field(..., examples=["BUY"], description="BUY or SELL")
    order_type: str = Field(
        ..., examples=["MARKET"], description="MARKET, LIMIT, or STOP"
    )
    quantity: float = Field(..., gt=0, examples=[0.001], description="Order quantity")
    price: Optional[float] = Field(
        None, gt=0, examples=[30000.0],
        description="Limit price (required for LIMIT and STOP orders)",
    )
    stop_price: Optional[float] = Field(
        None, gt=0, examples=[29000.0],
        description="Stop trigger price (required for STOP orders)",
    )


class OrderResponse(BaseModel):
    success: bool
    order: Dict[str, Any]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", tags=["Health"])
def root() -> Dict[str, str]:
    """Health check."""
    return {"message": "PrimetradeAI Trading Bot API", "status": "running"}


@app.get("/balance", tags=["Account"])
def get_balance() -> Dict[str, List[Dict[str, Any]]]:
    """Retrieve the futures account balance for all assets."""
    try:
        client = _get_client()
        balances = client.get_account_balance()
        logger.info("/balance — returned %d asset(s)", len(balances))
        return {"balances": balances}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("/balance error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/order", response_model=OrderResponse, tags=["Orders"])
def create_order(order: OrderRequest) -> OrderResponse:
    """Place a MARKET or LIMIT futures order on Binance Testnet."""
    try:
        client = _get_client()
        response = _place_order(
            client,
            order.symbol,
            order.side,
            order.order_type,
            order.quantity,
            order.price,
            order.stop_price,
        )
        logger.info(
            "/order — placed orderId=%s status=%s",
            response.get("orderId"),
            response.get("status"),
        )
        return OrderResponse(
            success=True,
            order={
                "orderId": response.get("orderId"),
                "symbol": response.get("symbol"),
                "status": response.get("status"),
                "side": response.get("side"),
                "type": response.get("type"),
                "origQty": response.get("origQty"),
                "executedQty": response.get("executedQty"),
                "avgPrice": response.get("avgPrice") or response.get("price"),
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("/order error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/logs", tags=["Logs"])
def get_logs(lines: int = 100) -> Dict[str, List[str]]:
    """Return the last *lines* entries from app.log."""
    if not os.path.exists(LOG_FILE):
        return {"logs": []}
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as fh:
            all_lines = fh.readlines()
        return {"logs": [line.rstrip() for line in all_lines[-lines:]]}
    except OSError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
