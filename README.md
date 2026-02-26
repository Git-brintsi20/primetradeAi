# PrimetradeAI — Binance Futures Testnet Trading Bot

A production-grade Python trading bot for **Binance Futures Testnet (USDT-M)**, featuring a Typer CLI, a FastAPI REST bridge, and a Next.js dark-mode trading dashboard.

---

## Architecture

```
primetradeAi/
├── backend/                       # Python backend
│   ├── bot/
│   │   ├── __init__.py            # Package exports
│   │   ├── client.py              # BinanceClient wrapper (testnet)
│   │   ├── orders.py              # Order placement + validation orchestration
│   │   ├── validators.py          # Pure input validation helpers
│   │   └── logging_config.py      # Structured logging (file + console)
│   ├── logs/
│   │   ├── market_order.log       # Sample MARKET order log
│   │   └── limit_order.log        # Sample LIMIT order log
│   ├── cli.py                     # Typer CLI entry point
│   ├── main.py                    # FastAPI server (REST bridge)
│   ├── requirements.txt
│   └── .env.example
├── client-tradingBot/             # Next.js 16 frontend
│   ├── app/                       # App Router pages
│   ├── components/                # Dashboard, order form, history, terminal
│   ├── components/ui/             # Shadcn UI primitives
│   ├── lib/                       # Utilities + config
│   ├── hooks/                     # Custom React hooks
│   ├── package.json
│   └── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

### Design decisions

| Layer        | Technology                | Rationale                                                  |
| ------------ | ------------------------- | ---------------------------------------------------------- |
| Bot core     | `python-binance`          | Official, well-maintained SDK with full futures support     |
| CLI          | Typer                     | Typed CLI with auto-generated help — meets the "must-have"  |
| REST bridge  | FastAPI + Uvicorn         | Async, auto-documented API (`/docs`) for the frontend      |
| Validation   | Pydantic v2 + custom fns  | Schema validation in FastAPI; pure-function validation in CLI|
| Frontend     | Next.js 16, Shadcn UI, Tailwind CSS | High-density dark-mode dashboard inspired by Binance UI |
| Config       | python-dotenv / `.env`    | Secrets stay out of source control                         |

---

## Quick start

### Prerequisites

- **Python 3.10+** and `pip`
- **Node.js 18+** and `npm` (for the frontend)
- A **Binance Futures Demo Trading** account with API credentials  
  → Generate at <https://demo.binance.com/en/my/settings/api-management>

### 1 — Backend setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env → set BINANCE_API_KEY and BINANCE_API_SECRET
```

### 2 — Frontend setup

```bash
cd client-tradingBot
npm install

# (Optional) copy and edit .env.example → .env.local if backend is on a different URL
```

---

## Usage

### CLI

Run from the `backend/` directory.

```bash
# MARKET BUY
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# LIMIT SELL
python cli.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000

# STOP-LIMIT BUY (bonus feature)
python cli.py order --symbol BTCUSDT --side BUY --type STOP --quantity 0.001 --price 69500 --stop-price 69000

# Check balance
python cli.py balance

# Help
python cli.py --help
```

**Sample output:**

```
====================================================
  Order Request Summary
====================================================
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
====================================================

✅  Order placed successfully!

====================================================
  Order Response
====================================================
  Order ID      : 4204474429
  Symbol        : BTCUSDT
  Status        : FILLED
  Side          : BUY
  Type          : MARKET
  Orig Qty      : 0.001
  Executed Qty  : 0.001
  Avg Price     : 64231.50
====================================================
```

### FastAPI server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Interactive Swagger docs → <http://localhost:8000/docs>

| Method | Path       | Description                     |
| ------ | ---------- | ------------------------------- |
| GET    | `/`        | Health check                    |
| GET    | `/balance` | Futures account balance         |
| POST   | `/order`   | Place MARKET / LIMIT / STOP order |
| GET    | `/logs`    | Tail `app.log` (last N lines)  |

**POST /order example:**

```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "order_type": "MARKET",
  "quantity": 0.001
}
```

### Frontend dashboard

```bash
cd client-tradingBot
npm run dev
```

Open <http://localhost:3000>. The dashboard connects to the FastAPI backend at `localhost:8000`.

**Features:**

- Side toggle (green BUY / red SELL) with Binance-style colour coding
- Conditional fields: price appears for Limit; price + stop-price appear for Stop-Limit
- Disabled submit button until all required fields are valid
- Toast notifications (sonner) for success / error / network failures
- Execution history table showing real API response data (orderId, status, avgPrice)
- Live terminal panel rendering request/response JSON in real time

---

## Logging

All API requests, responses, and errors are written to `backend/app.log` **and** to stdout.

Committed sample logs:

| File                          | Content                    |
| ----------------------------- | -------------------------- |
| `backend/logs/market_order.log` | BUY MARKET 0.001 BTCUSDT  |
| `backend/logs/limit_order.log`  | SELL LIMIT 0.001 BTCUSDT @ 70 000 |

---

## Bonus: Stop-Limit orders

A **STOP** (stop-limit) order type has been implemented end-to-end:

1. **Validator** — `validate_stop_price()` ensures `stop_price` is required and positive for STOP orders.
2. **Client** — sends `price`, `stopPrice`, and `timeInForce=GTC` to the Binance Futures API.
3. **CLI** — accepts `--stop-price` option.
4. **FastAPI** — `stop_price` field in the `OrderRequest` schema.
5. **Frontend** — conditionally renders the Stop Trigger Price input when "Stop-Limit" is selected.

---

## Assumptions

- All orders target the **USDT-M Futures Demo Trading** endpoint at `https://demo-fapi.binance.com`.
  (Migrated from the deprecated `testnet.binancefuture.com` — see [Binance FAQ](https://www.binance.com/en/support/faq/detail/9be58f73e5e14338809e3b705b9687dd)).
- LIMIT and STOP orders use `timeInForce=GTC` (Good Till Cancelled).
- Binance lot-size rules apply — for BTCUSDT use quantities like `0.001` (3 decimal places max).
- `BINANCE_API_KEY` and `BINANCE_API_SECRET` are stored in `backend/.env` and never committed.

---

## Security

- **`.env` is git-ignored.** The repo only ships `.env.example` with placeholder values.
- These keys are for the **testnet only** — never use mainnet credentials here.
