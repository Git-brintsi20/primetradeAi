# PrimetradeAI — Binance Futures Testnet Trading Bot

A clean, production-ready Python trading bot for **Binance Futures Testnet (USDT-M)**.  
It ships with both a **CLI** (Typer) and a **REST API** (FastAPI) so a frontend can connect to it.

---

## Project Structure

```
primetradeAi/
├── backend/
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── client.py          # BinanceClient wrapper
│   │   ├── orders.py          # Order placement logic
│   │   ├── validators.py      # Input validation
│   │   └── logging_config.py  # Structured logging setup
│   ├── logs/
│   │   ├── market_order.log   # Sample MARKET order log
│   │   └── limit_order.log    # Sample LIMIT order log
│   ├── cli.py                 # Typer CLI entry point
│   ├── main.py                # FastAPI server
│   ├── requirements.txt
│   └── .env.example
├── frontend/                  # (Next.js UI — add separately)
├── .gitignore
└── README.md
```

---

## Setup

### 1 — Get Binance Futures Testnet credentials

1. Go to <https://testnet.binancefuture.com> and sign in.
2. Generate an API key + secret under **Account → API Management**.

### 2 — Configure credentials

```bash
cd backend
cp .env.example .env
# Edit .env and fill in BINANCE_API_KEY and BINANCE_API_SECRET
```

### 3 — Create a virtual environment and install dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Usage — CLI

Run all commands from the `backend/` directory.

### Place a MARKET order

```bash
python cli.py order \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.001
```

### Place a LIMIT order

```bash
python cli.py order \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.001 \
  --price 70000
```

### Check account balance

```bash
python cli.py balance
```

### Get help

```bash
python cli.py --help
python cli.py order --help
```

---

## Usage — FastAPI Server

### Start the server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs are available at <http://localhost:8000/docs>.

### Endpoints

| Method | Path       | Description                          |
|--------|-----------|--------------------------------------|
| GET    | `/`       | Health check                         |
| GET    | `/balance`| Futures account balance              |
| POST   | `/order`  | Place a MARKET or LIMIT order        |
| GET    | `/logs`   | Last N lines from `app.log`          |

### POST /order — example body

```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "order_type": "MARKET",
  "quantity": 0.001
}
```

```json
{
  "symbol": "BTCUSDT",
  "side": "SELL",
  "order_type": "LIMIT",
  "quantity": 0.001,
  "price": 70000
}
```

---

## Logging

All API requests, responses, and errors are logged to `backend/app.log` **and** printed to stdout.

Sample log files for a MARKET and a LIMIT order are included in `backend/logs/`.

---

## Assumptions

- All orders target the **USDT-M Futures Testnet** at `https://testnet.binancefuture.com`.
- LIMIT orders use `timeInForce=GTC` (Good Till Cancelled).
- Binance lot-size rules apply — for BTCUSDT use quantities like `0.001` (3 decimal places max).
- `BINANCE_API_KEY` and `BINANCE_API_SECRET` must be set in a `.env` file inside `backend/`.

---

## Tech Stack

| Layer     | Technology      | Why                                                        |
|-----------|-----------------|------------------------------------------------------------|
| Bot logic | python-binance  | Official, well-maintained SDK for Binance                  |
| CLI       | Typer           | Clean, typed CLI with built-in help generation             |
| API       | FastAPI + Uvicorn | Async, auto-documented REST API for the frontend         |
| Validation | Pydantic v2    | Schema-level validation in FastAPI models                  |
| Config    | python-dotenv   | Keeps secrets out of source control                        |

---

## Security Notes

- **Never commit your `.env` file.** It is listed in `.gitignore`.
- These keys are for the **testnet only**; do not use mainnet keys here.
