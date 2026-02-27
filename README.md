# PrimetradeAI — Binance Futures Trading Bot

> **Python 3.x · CCXT · Typer CLI · FastAPI · Next.js 16 Dashboard**

A professional trading bot that places **Market**, **Limit**, and **Stop-Limit** orders on Binance Futures (USDT-M), with structured logging, input validation, and a dark-mode web dashboard.

---

## ✅ Requirement Checklist

| # | Requirement | Status | Details |
|---|-------------|--------|---------|
| 1 | Place **Market** and **Limit** orders | ✅ Done | MARKET BUY filled, LIMIT SELL placed — see logs below |
| 2 | Support **BUY** and **SELL** sides | ✅ Done | Both sides tested and verified |
| 3 | CLI input: symbol, side, type, qty, price | ✅ Done | Typer CLI with `--symbol`, `--side`, `--type`, `--quantity`, `--price` |
| 4 | Clear output: request summary + response | ✅ Done | Boxed CLI output with orderId, status, executedQty, avgPrice |
| 5 | Structured code (client + CLI layers) | ✅ Done | `bot/client.py` → `bot/orders.py` → `cli.py` (3-layer separation) |
| 6 | Logging to file | ✅ Done | `app.log` — all API calls, responses, and errors |
| 7 | Exception handling | ✅ Done | Input validation, API errors, network failures — all caught and logged |
| 8 | `README.md` with setup + examples | ✅ Done | You're reading it |
| 9 | `requirements.txt` | ✅ Done | 6 pinned dependencies |
| 10 | Log files (≥1 MARKET, ≥1 LIMIT) | ✅ Done | 3 log files included (market, limit, stop-limit) |
| **Bonus** | Stop-Limit order type | ✅ Done | Full end-to-end: validator → client → CLI → API → frontend |
| **Bonus** | Lightweight UI | ✅ Done | Next.js 16 + Shadcn UI dark-mode trading dashboard |

---

## ⚠️ Important: API Migration Note

> **Binance deprecated the Futures Testnet** (`testnet.binancefuture.com`) and migrated all testnet functionality to their new **Demo Trading** system ([Binance FAQ](https://www.binance.com/en/support/faq/detail/9be58f73e5e14338809e3b705b9687dd)).
>
> The `python-binance` library **does not support** the new Demo Trading endpoint. After hitting `Invalid API-key` errors with every approach using `python-binance`, I migrated to **[CCXT](https://github.com/ccxt/ccxt)** — a battle-tested exchange library that supports the new system natively via `exchange.enable_demo_trading(True)`.
>
> **The task was not impossible — it just needed a different library.** Everything else (structured code, CLI, validation, logging) is unchanged. CCXT wraps the same Binance REST API under the hood.

---

## Project Structure

```
primetradeAi/
├── backend/
│   ├── bot/
│   │   ├── __init__.py            # Package exports
│   │   ├── client.py              # BinanceClient wrapper (CCXT + Demo Trading)
│   │   ├── orders.py              # Validates → delegates to client
│   │   ├── validators.py          # Pure input validation (no side effects)
│   │   └── logging_config.py      # File + console structured logging
│   ├── logs/
│   │   ├── market_order.log       # ✅ Real MARKET order log
│   │   ├── limit_order.log        # ✅ Real LIMIT order log
│   │   └── stop_limit_order.log   # ✅ Real STOP-LIMIT order log (bonus)
│   ├── cli.py                     # Typer CLI entry point
│   ├── main.py                    # FastAPI REST bridge for frontend
│   ├── requirements.txt
│   └── .env.example
├── client-tradingBot/             # Next.js 16 frontend (bonus)
│   ├── app/                       # App Router pages
│   ├── components/                # Dashboard, order form, history, terminal
│   ├── lib/config.ts              # Centralised API URL config
│   └── package.json
├── .gitignore
└── README.md
```

### Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Bot core | **CCXT** (Binance) | Supports Demo Trading natively; `python-binance` does not |
| CLI | **Typer** | Typed CLI with auto `--help`, validation, and rich output |
| REST bridge | **FastAPI + Uvicorn** | Async, auto-docs at `/docs`, bridges CLI logic to frontend |
| Validation | **Pydantic v2** + custom fns | Schema validation (API) + pure functions (CLI) |
| Frontend | **Next.js 16**, Shadcn UI, Tailwind | High-density dark dashboard inspired by Binance UI |
| Config | **python-dotenv** | Secrets in `.env`, never committed |

---

## Setup

### Prerequisites

- **Python 3.10+** with `pip`
- **Node.js 18+** with `npm` (only for frontend)
- **Binance Demo Trading** API keys → [Generate here](https://demo.binance.com/en/my/settings/api-management)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate              # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env → paste your BINANCE_API_KEY and BINANCE_API_SECRET
```

### Frontend (optional)

```bash
cd client-tradingBot
npm install
```

---

## Usage

### CLI (run from `backend/`)

```bash
# MARKET BUY
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.005

# LIMIT SELL
python cli.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.003 --price 72000

# STOP-LIMIT SELL (bonus)
python cli.py order --symbol BTCUSDT --side SELL --type STOP --quantity 0.002 --price 65000 --stop-price 65500

# Account balance
python cli.py balance

# Help
python cli.py --help
```

**Sample CLI output (real execution):**

```
====================================================
  Order Request Summary
====================================================
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.005
====================================================

✅  Order placed successfully!

====================================================
  Order Response
====================================================
  Order ID      : 12550241182
  Symbol        : BTCUSDT
  Status        : FILLED
  Side          : BUY
  Type          : MARKET
  Orig Qty      : 0.005
  Executed Qty  : 0.005
  Avg Price     : 68169.70000
====================================================
```

### FastAPI Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Swagger docs → [http://localhost:8000/docs](http://localhost:8000/docs)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/balance` | Futures account balance |
| `POST` | `/order` | Place order (MARKET / LIMIT / STOP) |
| `GET` | `/logs?lines=100` | Tail `app.log` |

**POST /order body:**

```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "order_type": "MARKET",
  "quantity": 0.005
}
```

### Frontend Dashboard

```bash
cd client-tradingBot
npm run dev                         # → http://localhost:3000
```

**Features:** BUY/SELL toggle · conditional price fields · toast notifications · execution history table · live terminal · dark mode

---

## Log Files (Deliverable)

All three log files are in [`backend/logs/`](backend/logs/) — captured from **real orders executed on 2026-02-26**:

### `market_order.log` — MARKET BUY 0.005 BTC → FILLED

```log
2026-02-26 18:38:19 [INFO] bot.client: Initialising Binance Futures Demo Trading client…
2026-02-26 18:38:19 [INFO] bot.client: Binance Futures Demo Trading client ready
2026-02-26 18:38:19 [INFO] bot.orders: Order request — symbol=BTCUSDT, side=BUY, type=MARKET, qty=0.005
2026-02-26 18:38:19 [INFO] bot.client: Placing order — {symbol: BTCUSDT, side: BUY, type: MARKET, quantity: 0.005}
2026-02-26 18:38:26 [INFO] bot.client: Order placed — orderId=12550241182, status=FILLED
```

### `limit_order.log` — LIMIT SELL 0.003 BTC @ $72,000 → NEW

```log
2026-02-26 18:39:02 [INFO] bot.client: Initialising Binance Futures Demo Trading client…
2026-02-26 18:39:02 [INFO] bot.client: Binance Futures Demo Trading client ready
2026-02-26 18:39:02 [INFO] bot.orders: Order request — symbol=BTCUSDT, side=SELL, type=LIMIT, qty=0.003, price=72000.0
2026-02-26 18:39:02 [INFO] bot.client: Placing order — {symbol: BTCUSDT, side: SELL, type: LIMIT, quantity: 0.003, price: 72000.0}
2026-02-26 18:39:06 [INFO] bot.client: Order placed — orderId=12550242484, status=NEW
```

### `stop_limit_order.log` — STOP SELL 0.002 BTC, trigger $65,500 → OPEN *(bonus)*

```log
2026-02-26 18:39:59 [INFO] bot.client: Initialising Binance Futures Demo Trading client…
2026-02-26 18:39:59 [INFO] bot.client: Binance Futures Demo Trading client ready
2026-02-26 18:39:59 [INFO] bot.orders: Order request — symbol=BTCUSDT, side=SELL, type=STOP, qty=0.002, price=65000.0, stopPrice=65500.0
2026-02-26 18:39:59 [INFO] bot.client: Placing order — {symbol: BTCUSDT, side: SELL, type: STOP, quantity: 0.002, stopPrice: 65500.0}
2026-02-26 18:40:03 [INFO] bot.client: Order placed — orderId=1000000017291126, status=OPEN
```

---

## Bonus: Stop-Limit Orders

Implemented end-to-end across all layers:

| Layer | What was added |
|-------|---------------|
| `validators.py` | `validate_stop_price()` — requires positive `stop_price` for STOP orders |
| `client.py` | Sends `price` + `stopPrice` + `timeInForce=GTC` to Binance |
| `cli.py` | `--stop-price` option |
| `main.py` | `stop_price` field in `OrderRequest` Pydantic schema |
| Frontend | Conditional Stop Trigger Price input when "Stop-Limit" is selected |

---

## Assumptions

1. All orders target **Binance Futures Demo Trading** at `https://demo-fapi.binance.com`  
   *(migrated from the now-deprecated `testnet.binancefuture.com`)*
2. LIMIT and STOP orders use `timeInForce=GTC` (Good Till Cancelled)
3. Binance lot-size rules apply — BTCUSDT accepts up to 3 decimal places
4. Credentials stored in `backend/.env` (git-ignored; only `.env.example` is committed)
5. CORS is set to `allow_origins=["*"]` — acceptable for demo/testnet usage

---

## Security

- `.env` is **git-ignored** — the repo ships only `.env.example` with placeholders
- All credentials target the **Demo Trading** system — never use mainnet keys

---

## Quick Verification (3 commands)

```bash
cd backend && source .venv/bin/activate   # Windows: .venv\Scripts\activate

python cli.py balance                     # Confirm API connection + funds
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.005
python cli.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.003 --price 72000
```

All three should succeed with real order IDs and status output.
