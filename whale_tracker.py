"""
whale_tracker.py — Smart Money Wallet Tracker (Phase 6)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A free-stack implementation of wallet-level "smart money" intelligence —
the missing piece from the "862 whales out of 26,589" system described
in the video. No Nansen subscription needed.

HOW IT WORKS (the full pipeline):
──────────────────────────────────
1. CONTRACT LOOKUP
   Given a token symbol ("LINK", "EDU", "AAVE"), resolve its Ethereum
   contract address from the local _SYMBOL_TO_CONTRACT map, or fall
   back to a live CoinGecko search.

2. TOP HOLDER BOOTSTRAP
   Etherscan free API → get top 50 holders of the token contract.
   CEX hot wallets, DEX routers, burn addresses are filtered out.
   These are the pool we'll score as potential "smart money."

3. WIN RATE CALCULATION (the core algorithm)
   For each wallet address:
   a) Pull their last 180 days of ERC-20 token transfers (Etherscan)
   b) Identify BUY events: tokens received FROM a known DEX router
   c) Identify SELL events: tokens sent TO a known DEX router
   d) Match buys → sells chronologically (FIFO) to form round-trips
   e) For each round-trip: fetch price at buy time + sell time (Binance klines)
   f) PnL% = (sell_price - buy_price) / buy_price
   g) WIN if PnL > 5%, LOSS if PnL < -5%, NEUTRAL otherwise
   h) win_rate = wins / (wins + losses)
   i) Flag as SMART MONEY if: win_rate >= 55% AND completed_trades >= 10

4. WALLET DB CACHING (SQLite, local file)
   Win rates are expensive to compute (many API calls). Results are cached
   with a 24h TTL so subsequent runs for the same wallets are instant.
   DB persists across Streamlit restarts.

5. RECENT ACTION DETECTION (the signal)
   For each smart-money wallet: check their last 7 days of activity on
   the specific token. Are they BUYING, SELLING, or holding?
   BUY  = recently received tokens from a DEX router
   SELL = recently sent tokens to a DEX router
   HOLD = no DEX activity on this token in the lookback window

6. SIGNAL SCORING
   score = (n_buying - n_selling) / total_smart_money * 10
   Clamped to [-10, +10] for composite blending with other Phase modules.

   +8 to +10: Smart money strongly accumulating → STRONGLY BULLISH
   +3 to +7:  Net accumulation                  → ACCUMULATING
   -2 to +2:  Balanced / no strong view         → NEUTRAL
   -3 to -7:  Net distribution                  → DISTRIBUTING
   -8 to -10: Smart money strongly selling       → STRONGLY BEARISH

FREE API USAGE:
──────────────
  Etherscan free tier: 5 calls/sec, ~100K/day
    - No key: works for token transfers (slower, no holder list endpoint)
    - Free key (etherscan.io/register): unlocks tokenholderlist, 5x faster
  Binance klines: completely free, no key
  CoinGecko: free tier, used only for contract lookup fallback

INTEGRATION:
────────────
  This module is designed as Phase 6 for pulse_intel.py.
  Main entry: get_token_whale_signal(symbol, etherscan_api_key="")
  Returns the same standardized dict format as all other Phase modules:
    {ok, supported, score, label, color, detail, data}

  In pulse_intel.get_pulse_intel(), add it with 15% weight,
  adjusting the existing weight distribution accordingly.

HONEST CAVEATS:
───────────────
  - Win rate based on DEX swaps only — OTC trades and CEX activity missed
  - Price lookup is daily candle close (not exact swap price) → small PnL error
  - Token holder list may include locked/vesting wallets (not active traders)
  - A wallet that holds many tokens but rarely trades won't be flagged
  - This is a probabilistic signal, not a deterministic copy-trade system
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

# ─────────────────────────────────────────────────────────────────────────────
# Thresholds — tweak these to tighten/loosen the "smart money" filter
# ─────────────────────────────────────────────────────────────────────────────
SMART_MONEY_WIN_RATE_THRESHOLD = 0.55   # 55%+ win rate required
SMART_MONEY_MIN_TRADES         = 10     # must have ≥10 completed DEX round-trips
SMART_MONEY_MIN_PNL_PCT        = 0.05   # trade must move ≥5% to count as WIN/LOSS
WALLET_SCORE_TTL               = 86_400  # 24h — wallet win rates don't change hourly
TOKEN_SIGNAL_TTL               = 900    # 15min — recent action cache

# How many top holders to analyze per token (more = better signal, slower)
MAX_HOLDERS_TO_SCORE = 30

# ─────────────────────────────────────────────────────────────────────────────
# Known DEX router addresses — used to classify transfers as swaps
# ─────────────────────────────────────────────────────────────────────────────
_DEX_ROUTERS: set[str] = {
    "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2 Router
    "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3 Router
    "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",  # Uniswap V3 Router 2
    "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad",  # Uniswap Universal Router
    "0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b",  # Uniswap Universal Router (v1)
    "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",  # SushiSwap Router
    "0x1111111254eeb25477b68fb85ed929f73a960582",  # 1inch V5
    "0x1111111254fb6c44bac0bed2854e76f90643097d",  # 1inch V4
    "0xdef1c0ded9bec7f1a1670819833240f027b25eff",  # 0x Exchange Proxy
    "0x00000000009726632680fb29d3f7a9734e3010e2",  # ParaSwap V5
    "0x111111125421ca6dc452d289314280a0f8842a65",  # 1inch V6
    "0xe66b31678d6c16e9ebf358268a790b763c133750",  # Cowswap Settlement
    "0x9008d19f58aabd9ed0d60971565aa8510560ab41",  # Cowswap V2
}

# Known CEX hot/cold wallet addresses — exclude from smart-money pool
# (CEX wallets are custodial, not individual traders)
_CEX_ADDRESSES: set[str] = {
    "0x28c6c06298d514db089934071355e5743bf21d60",  # Binance 14
    "0x21a31ee1afc51d94c2efccaa2092ad1028285549",  # Binance Cold
    "0xdfd5293d8e347dfe59e90efd55b2956a1343963d",  # Binance 7
    "0x56eddb7aa87536c09ccc2793473599fd21a8b17f",  # Binance 8
    "0x9696f59e4d72e237be84ffd425dcad154bf96976",  # Binance 9
    "0x5041ed759dd4afc3a72b8192c143f72f4724081f",  # Binance 10
    "0xae2d4617c862309a3d75a0ffb358c7a5009c673f",  # Kraken 1
    "0x2910543af39aba0cd09dbb2d50200b3e800a63d2",  # Kraken 2
    "0x0a869d79a7052c7f1b55a8ebabbea3420f0d1e13",  # Kraken 3
    "0xa1d8d972560c2f8144af871db508f0b0b10a3fbf",  # Coinbase Cold 1
    "0x503828976d22510aad0201ac7ec88293211d23da",  # Coinbase 2
    "0x3cd751e6b0078be393132286c442345e5dc49699",  # Coinbase 3
    "0x71660c4005ba85c37ccec55d0c4493e66fe775d3",  # Coinbase 4
    "0x2b5634c42055806a59e9107ed44d43c426e58258",  # OKX
    "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b",  # OKX 2
    "0x236f9f97e0e62388479bf9e5ba4889e46b0273c3",  # Bitfinex
    "0x742d35cc6634c0532925a3b844bc454e4438f44e",  # Bitfinex 2
}

# Stablecoins and wrapped tokens to skip in win rate calculation
_SKIP_SYMBOLS: set[str] = {
    "USDT", "USDC", "DAI", "BUSD", "FRAX", "TUSD", "GUSD", "LUSD",
    "USDD", "FDUSD", "PYUSD", "USDP", "MIM", "CRVUSD", "EURC",
    "WETH", "WBTC", "WBNB", "WMATIC", "WAVAX", "STETH", "WSTETH",
    "CBETH", "RETH", "BETH", "FRXETH",
}

# ─────────────────────────────────────────────────────────────────────────────
# Token contract map: base symbol → Ethereum ERC-20 contract address
# Extend freely — CoinGecko lookup fills gaps at runtime but is slower
# ─────────────────────────────────────────────────────────────────────────────
_SYMBOL_TO_CONTRACT: dict[str, str] = {
    "AAVE":   "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9",
    "UNI":    "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    "LINK":   "0x514910771af9ca656af840dff83e8264ecf986ca",
    "MKR":    "0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2",
    "CRV":    "0xd533a949740bb3306d119cc777fa900ba034cd52",
    "LDO":    "0x5a98fcbea516cf06857215779fd812ca3bef1b32",
    "SNX":    "0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f",
    "COMP":   "0xc00e94cb662c3520282e6f5717214004a7f26888",
    "BAL":    "0xba100000625a3754423978a60c9317c58a424e3d",
    "1INCH":  "0x111111111117dc0aa78b770fa6a738034120c302",
    "SUSHI":  "0x6b3595068778dd592e39a122f4f5a5cf09c90fe2",
    "YFI":    "0x0bc529c00c6401aef6d220be8c6ea1667f6ad93e",
    "DYDX":   "0x92d6c1e31e14520e676a687f0a93788b716beff5",
    "PENDLE": "0x808507121b80c02388fad14726482e061b8da827",
    "ONDO":   "0xfaba6f8e4a5e8ab82f62fe7c39859fa577269be3",
    "ENA":    "0x57e114b691db790c35207b2e685d4a43181e6061",
    "ETHFI":  "0xfe0c30065b384f05761f15d0cc899d4f9f9cc0eb",
    "MORPHO": "0x58d97b57bb95320f9a05dc918aef65434969c2b2",
    "EIGEN":  "0xec53bf9167f50cdeb3ae105f56099aaab9061f83",
    "GRT":    "0xc944e90c64b2c07662a292be6244bdf05cda44a7",
    "RPL":    "0xd33526068d116ce69f19a9ee46f0bd304f21a51f",
    "ZRX":    "0xe41d2489571d322189246dafa5ebde1f4699f498",
    "ENS":    "0xc18360217d8f7ab5e7c516566761ea12ce7f9d72",
    "BLUR":   "0x5283d291dbcf85356a21ba090e6db59121208b44",
    "FXS":    "0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0",
    "STG":    "0xaf5191b0de278c7286d6c7cc6ab6bb8a73ba2cd6",
    "APE":    "0x4d224452801aced8b2f0aebe155379bb5d594381",
    "IMX":    "0xf57e7e7c23978c3caec3c3548e3d615c346e79ff",
    "CHZ":    "0x3506424f91fd33084466f402d5d97f05f8e3b4af",
    "MANA":   "0x0f5d2fb29fb7d3cfee444a200298f468908cc942",
    "SAND":   "0x3845badade8e6dff049820680d1f14bd3903a5d0",
    "AXS":    "0xbb0e17ef65f82ab018d8edd776e8dd940327b28b",
    "GALA":   "0xd1d2eb1b1e90b638588728b4130137d262c87cae",
    "EDU":    "0xb4d749e0d4f9ab1f919878e98e44a4f99ba2f234",
    "ASTRO":  "0x0000000000000000000000000000000000000000",  # Cosmos-based, placeholder
    "GMX":    "0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a",
    "GNO":    "0x6810e776880c02933d47db1b9fc05908e5386b96",
    "ZRO":    "0x6985884c4392d348587b19cb9eaaf157f13271cd",
    "W":      "0xb0ffa8000886e57f86dd5264b9582b2ad87b2b91",
    "TNSR":   "0x282d8efce846a88b159800bd4130ad77443fa1a1",
    "STRK":   "0xcaa004418eb42cdf00cb057b7c9e28f0ffd840a5",
    "ARB":    "0xb50721bcf8d664c30412cfbc6cf7a15145234ad1",
    "OP":     "0x4200000000000000000000000000000000000042",
}

# ─────────────────────────────────────────────────────────────────────────────
# SQLite — persistent wallet analytics database
# ─────────────────────────────────────────────────────────────────────────────
_DB_PATH = Path(__file__).parent / "whale_tracker.db"
_DB_LOCK = threading.Lock()


def _get_db() -> sqlite3.Connection:
    """Open (or create) the local SQLite database in WAL mode."""
    conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS wallet_scores (
            address        TEXT PRIMARY KEY,
            win_rate       REAL    DEFAULT 0,
            wins           INTEGER DEFAULT 0,
            losses         INTEGER DEFAULT 0,
            n_trades       INTEGER DEFAULT 0,
            n_tokens       INTEGER DEFAULT 0,
            avg_hold_days  REAL    DEFAULT 0,
            is_smart_money INTEGER DEFAULT 0,
            last_updated   INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS token_signals (
            symbol         TEXT,
            contract       TEXT,
            n_whales_buy   INTEGER DEFAULT 0,
            n_whales_sell  INTEGER DEFAULT 0,
            n_whales_hold  INTEGER DEFAULT 0,
            total_whales   INTEGER DEFAULT 0,
            score          REAL    DEFAULT 0,
            label          TEXT    DEFAULT '',
            detail         TEXT    DEFAULT '',
            last_updated   INTEGER DEFAULT 0,
            PRIMARY KEY (symbol, contract)
        );
        CREATE INDEX IF NOT EXISTS idx_wallet_smart ON wallet_scores(is_smart_money);
        CREATE INDEX IF NOT EXISTS idx_wallet_updated ON wallet_scores(last_updated);
    """)
    conn.commit()
    return conn


# ─────────────────────────────────────────────────────────────────────────────
# Etherscan API — rate-limited wrapper
# ─────────────────────────────────────────────────────────────────────────────
_ES_RATE_LOCK   = threading.Lock()
_ES_LAST_CALL   = 0.0
_ES_MIN_INTERVAL = 0.22   # ~4.5 calls/sec (free tier is 5/sec; leave headroom)
_ES_BASE         = "https://api.etherscan.io/api"


def _es_call(params: dict, api_key: str = "") -> Optional[list | dict]:
    """
    Rate-limited Etherscan API call.
    Returns the `result` field of the response, or None on any failure.
    """
    global _ES_LAST_CALL
    with _ES_RATE_LOCK:
        elapsed = time.time() - _ES_LAST_CALL
        if elapsed < _ES_MIN_INTERVAL:
            time.sleep(_ES_MIN_INTERVAL - elapsed)
        _ES_LAST_CALL = time.time()

    if api_key:
        params = {**params, "apikey": api_key}

    try:
        r = requests.get(
            _ES_BASE, params=params, timeout=12,
            headers={"User-Agent": "WhaleTracker/PhaseVI"},
        )
        if r.status_code != 200:
            return None
        body = r.json()
        # Etherscan uses "1" for success, "0" for error
        # But "OK" on some endpoints that return empty lists legitimately
        if body.get("status") == "0" and body.get("message") not in ("No transactions found", "No records found"):
            return None
        return body.get("result")
    except Exception:
        return None


def _get_top_holders(contract: str, api_key: str = "",
                     top_n: int = 50) -> list[str]:
    """
    Returns up to top_n wallet addresses that hold the token.

    Strategy A (requires key): tokenholderlist endpoint
    Strategy B (no key): extract unique non-DEX addresses from recent transfers
    """
    contract_lower = contract.lower()

    if api_key:
        result = _es_call({
            "module":          "token",
            "action":          "tokenholderlist",
            "contractaddress": contract_lower,
            "page":            1,
            "offset":          top_n,
        }, api_key=api_key)
        if result and isinstance(result, list):
            addrs = [r.get("TokenHolderAddress", "").lower() for r in result]
            return _filter_addresses(addrs)[:top_n]

    # Fallback: mine recent transfer events for unique addresses
    result = _es_call({
        "module":          "account",
        "action":          "tokentx",
        "contractaddress": contract_lower,
        "sort":            "desc",
        "page":            1,
        "offset":          200,
    }, api_key=api_key)

    if not result or not isinstance(result, list):
        return []

    seen: set[str] = set()
    addrs: list[str] = []
    for tx in result:
        for key in ("from", "to"):
            a = tx.get(key, "").lower()
            if a and a not in seen:
                seen.add(a)
                addrs.append(a)
    return _filter_addresses(addrs)[:top_n]


def _filter_addresses(addrs: list[str]) -> list[str]:
    """Remove DEX routers, CEX wallets, zero addresses, and obvious contracts."""
    return [
        a for a in addrs
        if a
        and a not in _DEX_ROUTERS
        and a not in _CEX_ADDRESSES
        and not a.startswith("0x000000000000000000000000000000000000")
        and a != "0x0000000000000000000000000000000000000000"
    ]


def _get_wallet_transfers(address: str, api_key: str = "",
                           days_back: int = 180) -> list[dict]:
    """Get ERC-20 token transfers for a wallet over the last N days."""
    cutoff_ts = int(time.time()) - (days_back * 86_400)
    result = _es_call({
        "module":    "account",
        "action":    "tokentx",
        "address":   address.lower(),
        "startblock": 0,
        "endblock":  99_999_999,
        "sort":      "asc",
        "page":      1,
        "offset":    1000,
    }, api_key=api_key)

    if not result or not isinstance(result, list):
        return []
    return [tx for tx in result if int(tx.get("timeStamp", 0)) >= cutoff_ts]


# ─────────────────────────────────────────────────────────────────────────────
# Price lookup — Binance klines (free, no key)
# ─────────────────────────────────────────────────────────────────────────────
_PRICE_CACHE: dict[str, float] = {}   # "SYMBOL:YYYY-MM-DD" → close price


def _price_at(symbol: str, unix_ts: int) -> Optional[float]:
    """
    Return the daily close price of `symbol` (vs USDT) on the date of unix_ts.
    Uses Binance 1d klines. Caches results in-process to avoid redundant calls.
    """
    # Snap to midnight UTC
    dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc)
    date_key = dt.strftime("%Y-%m-%d")
    cache_key = f"{symbol}:{date_key}"

    if cache_key in _PRICE_CACHE:
        return _PRICE_CACHE[cache_key]

    start_ms = int(datetime(dt.year, dt.month, dt.day,
                             tzinfo=timezone.utc).timestamp() * 1000)
    end_ms   = start_ms + 86_400_000

    try:
        r = requests.get(
            "https://api.binance.com/api/v3/klines",
            params={
                "symbol":    f"{symbol}USDT",
                "interval":  "1d",
                "startTime": start_ms,
                "endTime":   end_ms,
                "limit":     1,
            },
            timeout=8,
            headers={"User-Agent": "WhaleTracker/PhaseVI"},
        )
        if r.status_code == 200:
            data = r.json()
            if data and isinstance(data, list):
                price = float(data[0][4])  # candle close
                _PRICE_CACHE[cache_key] = price
                return price
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Win Rate Calculator
# ─────────────────────────────────────────────────────────────────────────────

def _score_wallet(address: str, transfers: list[dict]) -> dict:
    """
    Compute a wallet's trading win rate from its ERC-20 transfer history.

    Algorithm:
      1. Group transfers by token contract
      2. For each token: identify buy (received from DEX) and sell (sent to DEX) events
      3. Match FIFO: each buy is paired with the next sell that follows it
      4. Fetch daily price at buy + sell timestamps from Binance
      5. PnL% per trade; WIN if >+5%, LOSS if <-5%, else NEUTRAL
      6. win_rate = wins / (wins + losses)

    Returns dict with win_rate, wins, losses, n_trades, n_tokens, avg_hold_days, is_smart_money
    """
    addr_lower = address.lower()

    # Group by token contract
    by_token: dict[str, dict] = {}
    for tx in transfers:
        contract = tx.get("contractAddress", "").lower()
        if not contract:
            continue
        sym = tx.get("tokenSymbol", "").upper().strip()
        # Skip stables and wrapped assets
        if sym in _SKIP_SYMBOLS or not sym:
            continue
        try:
            decimals = int(tx.get("tokenDecimal", 18))
            value    = int(tx.get("value", 0)) / (10 ** decimals)
        except (ValueError, ZeroDivisionError):
            continue
        if value <= 0:
            continue

        ts     = int(tx.get("timeStamp", 0))
        from_  = tx.get("from", "").lower()
        to_    = tx.get("to", "").lower()

        if contract not in by_token:
            by_token[contract] = {"sym": sym, "buys": [], "sells": []}

        # BUY: wallet receives tokens FROM a DEX router
        if to_ == addr_lower and from_ in _DEX_ROUTERS:
            by_token[contract]["buys"].append({"ts": ts, "value": value, "sym": sym})
        # SELL: wallet sends tokens TO a DEX router
        elif from_ == addr_lower and to_ in _DEX_ROUTERS:
            by_token[contract]["sells"].append({"ts": ts, "value": value, "sym": sym})

    wins      = 0
    losses    = 0
    neutrals  = 0
    hold_days_list: list[float] = []

    for contract, data in by_token.items():
        sym   = data["sym"]
        buys  = sorted(data["buys"],  key=lambda x: x["ts"])
        sells = sorted(data["sells"], key=lambda x: x["ts"])

        if not buys or not sells:
            continue

        buy_q = list(buys)
        for sell in sells:
            if not buy_q:
                break
            # Find the oldest buy that precedes this sell
            buy = None
            for i, b in enumerate(buy_q):
                if b["ts"] < sell["ts"]:
                    buy = buy_q.pop(i)
                    break
            if buy is None:
                continue

            hold_d = (sell["ts"] - buy["ts"]) / 86_400
            hold_days_list.append(hold_d)

            # Fetch prices
            buy_price  = _price_at(sym, buy["ts"])
            sell_price = _price_at(sym, sell["ts"])

            if not buy_price or not sell_price or buy_price <= 0:
                neutrals += 1
                continue

            pnl = (sell_price - buy_price) / buy_price
            if pnl > SMART_MONEY_MIN_PNL_PCT:
                wins += 1
            elif pnl < -SMART_MONEY_MIN_PNL_PCT:
                losses += 1
            else:
                neutrals += 1

    completed = wins + losses
    win_rate  = wins / completed if completed > 0 else 0.0
    avg_hold  = sum(hold_days_list) / len(hold_days_list) if hold_days_list else 0.0

    return {
        "win_rate":      win_rate,
        "wins":          wins,
        "losses":        losses,
        "n_trades":      wins + losses + neutrals,
        "n_tokens":      len(by_token),
        "avg_hold_days": avg_hold,
        "is_smart_money": (
            win_rate  >= SMART_MONEY_WIN_RATE_THRESHOLD
            and completed >= SMART_MONEY_MIN_TRADES
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Recent Action Detector — what did this smart money wallet do RECENTLY?
# ─────────────────────────────────────────────────────────────────────────────

def _recent_action(address: str, contract: str,
                    api_key: str = "",
                    lookback_days: int = 7) -> str:
    """
    Determine if a wallet is currently buying, selling, or holding a token.

    Returns: "BUY" | "SELL" | "HOLD" | "UNKNOWN"

    Logic: compare net DEX buy volume vs sell volume over the last 7 days.
    If buys dominate (>1.5x sells by token quantity): BUY
    If sells dominate (>1.5x buys): SELL
    Otherwise: HOLD (either balanced or inactive)
    """
    cutoff = int(time.time()) - (lookback_days * 86_400)
    result = _es_call({
        "module":          "account",
        "action":          "tokentx",
        "address":         address.lower(),
        "contractaddress": contract.lower(),
        "sort":            "desc",
        "page":            1,
        "offset":          50,
    }, api_key=api_key)

    if not result or not isinstance(result, list):
        return "UNKNOWN"

    addr_lower = address.lower()
    buy_vol = sell_vol = 0.0

    for tx in result:
        if int(tx.get("timeStamp", 0)) < cutoff:
            continue
        try:
            decimals = int(tx.get("tokenDecimal", 18))
            value    = int(tx.get("value", 0)) / (10 ** decimals)
        except Exception:
            continue

        from_ = tx.get("from", "").lower()
        to_   = tx.get("to",   "").lower()

        if to_ == addr_lower and from_ in _DEX_ROUTERS:
            buy_vol += value
        elif from_ == addr_lower and to_ in _DEX_ROUTERS:
            sell_vol += value

    if buy_vol == 0 and sell_vol == 0:
        return "HOLD"
    if buy_vol > sell_vol * 1.5:
        return "BUY"
    if sell_vol > buy_vol * 1.5:
        return "SELL"
    return "HOLD"   # roughly balanced


# ─────────────────────────────────────────────────────────────────────────────
# Contract Lookup — CoinGecko fallback when symbol not in local map
# ─────────────────────────────────────────────────────────────────────────────

_CG_CACHE: dict[str, Optional[str]] = {}


def _lookup_contract_coingecko(symbol: str) -> Optional[str]:
    """
    Resolve an Ethereum ERC-20 contract address for a symbol via CoinGecko.
    Free endpoint, rate-limited at ~30 calls/min on the public tier.
    """
    sym = symbol.upper()
    if sym in _CG_CACHE:
        return _CG_CACHE[sym]

    try:
        # Search for coin ID
        r = requests.get(
            "https://api.coingecko.com/api/v3/search",
            params={"query": sym},
            timeout=10,
            headers={"User-Agent": "WhaleTracker/PhaseVI"},
        )
        if r.status_code != 200:
            _CG_CACHE[sym] = None
            return None

        coins = r.json().get("coins", [])
        # Pick the best symbol match
        candidates = [c for c in coins if c.get("symbol", "").upper() == sym]
        if not candidates:
            candidates = coins[:1]
        if not candidates:
            _CG_CACHE[sym] = None
            return None

        coin_id = candidates[0]["id"]

        # Get contract addresses
        time.sleep(0.5)  # CoinGecko rate limit buffer
        r2 = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}",
            params={"localization": "false", "sparkline": "false",
                    "market_data": "false", "developer_data": "false"},
            timeout=12,
            headers={"User-Agent": "WhaleTracker/PhaseVI"},
        )
        if r2.status_code != 200:
            _CG_CACHE[sym] = None
            return None

        platforms = r2.json().get("platforms", {})
        contract = (platforms.get("ethereum")
                    or platforms.get("binance-smart-chain")
                    or "")
        result = contract.lower() if contract else None
        _CG_CACHE[sym] = result
        return result
    except Exception:
        _CG_CACHE[sym] = None
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Score → label + color helpers
# ─────────────────────────────────────────────────────────────────────────────

def _score_label(score: float) -> tuple[str, str]:
    """Return (label, hex_color) for a [-10, +10] score."""
    if score >= 7:
        return "STRONG ACCUMULATION", "#3fb950"
    if score >= 3:
        return "ACCUMULATING",        "#64ffda"
    if score <= -7:
        return "STRONG DISTRIBUTION", "#f85149"
    if score <= -3:
        return "DISTRIBUTING",        "#f0883e"
    return "NEUTRAL",                 "#8892b0"


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point — Phase 6 module API
# ─────────────────────────────────────────────────────────────────────────────

def get_token_whale_signal(symbol: str, etherscan_api_key: str = "") -> dict:
    """
    Phase 6 main entry point. Returns smart-money wallet intelligence for symbol.

    Drop-in replacement for other pulse_intel Phase modules.
    Call from get_pulse_intel() and include in composite score at ~15% weight.

    Returned dict shape (same contract as all Phase modules):
    {
        "ok":        bool,          # True if we got a usable signal
        "supported": bool,          # True if we have a contract for this token
        "score":     float,         # -10 to +10
        "label":     str,           # "ACCUMULATING" / "NEUTRAL" / "DISTRIBUTING" etc
        "color":     str,           # hex color matching label
        "detail":    str,           # human-readable explanation
        "data": {
            "n_whales_buy":  int,
            "n_whales_sell": int,
            "n_whales_hold": int,
            "total_whales":  int,
            "avg_win_rate":  float,     # average win rate of tracked smart wallets
            "wallets":       list[dict] # truncated wallet list for UI display
        }
    }
    """
    # Normalize symbol
    base = symbol.upper().strip()
    for suffix in ("USDT", "USDC", "BUSD", "FDUSD", "TUSD", "DAI"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break

    # Resolve contract
    contract = _SYMBOL_TO_CONTRACT.get(base)
    if not contract or contract == "0x0000000000000000000000000000000000000000":
        # Try CoinGecko live lookup
        contract = _lookup_contract_coingecko(base)

    if not contract:
        return {
            "ok": False, "supported": False,
            "score": 0, "label": "NOT MAPPED", "color": "#8892b0",
            "detail": (f"{base} not in the contract map. "
                       f"Add its Ethereum ERC-20 address to _SYMBOL_TO_CONTRACT "
                       f"in whale_tracker.py to enable Phase 6 tracking."),
            "data": _empty_data(),
        }

    # ── Check token signal cache ────────────────────────────────────────────
    with _DB_LOCK:
        db  = _get_db()
        row = db.execute(
            "SELECT * FROM token_signals WHERE symbol=? AND contract=?",
            (base, contract.lower()),
        ).fetchone()

    if row and (time.time() - row["last_updated"]) < TOKEN_SIGNAL_TTL:
        label, color = _score_label(row["score"])
        return {
            "ok": True, "supported": True,
            "score":  row["score"],
            "label":  row["label"] or label,
            "color":  color,
            "detail": row["detail"],
            "data": {
                "n_whales_buy":  row["n_whales_buy"],
                "n_whales_sell": row["n_whales_sell"],
                "n_whales_hold": row["n_whales_hold"],
                "total_whales":  row["total_whales"],
                "avg_win_rate":  0.0,
                "wallets":       [],
            },
        }

    # ── Step 1: Get top token holders ──────────────────────────────────────
    addresses = _get_top_holders(contract, api_key=etherscan_api_key,
                                  top_n=MAX_HOLDERS_TO_SCORE + 20)
    if not addresses:
        return {
            "ok": False, "supported": True,
            "score": 0, "label": "NO DATA", "color": "#8892b0",
            "detail": "Etherscan returned no holder data. Check rate limits or add an API key.",
            "data": _empty_data(),
        }

    # ── Step 2: Score each wallet (with DB cache) ───────────────────────────
    smart_money: list[dict] = []

    with _DB_LOCK:
        db = _get_db()
        for addr in addresses[:MAX_HOLDERS_TO_SCORE]:
            cached_row = db.execute(
                "SELECT * FROM wallet_scores WHERE address=?", (addr,)
            ).fetchone()

            if cached_row and (time.time() - cached_row["last_updated"]) < WALLET_SCORE_TTL:
                if cached_row["is_smart_money"]:
                    smart_money.append({
                        "address":  addr,
                        "win_rate": cached_row["win_rate"],
                        "wins":     cached_row["wins"],
                        "losses":   cached_row["losses"],
                        "n_trades": cached_row["n_trades"],
                    })
                continue

            # Fresh computation
            transfers = _get_wallet_transfers(addr, api_key=etherscan_api_key, days_back=180)
            if not transfers:
                continue

            stats = _score_wallet(addr, transfers)

            # Persist to DB
            db.execute("""
                INSERT OR REPLACE INTO wallet_scores
                (address, win_rate, wins, losses, n_trades, n_tokens,
                 avg_hold_days, is_smart_money, last_updated)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                addr,
                stats["win_rate"],
                stats["wins"],
                stats["losses"],
                stats["n_trades"],
                stats["n_tokens"],
                stats["avg_hold_days"],
                int(stats["is_smart_money"]),
                int(time.time()),
            ))
            db.commit()

            if stats["is_smart_money"]:
                smart_money.append({
                    "address":  addr,
                    "win_rate": stats["win_rate"],
                    "wins":     stats["wins"],
                    "losses":   stats["losses"],
                    "n_trades": stats["n_trades"],
                })

    # ── Step 3: Check recent action of each smart-money wallet ──────────────
    n_buy = n_sell = n_hold = 0

    for wallet in smart_money:
        action = _recent_action(
            wallet["address"], contract,
            api_key=etherscan_api_key,
            lookback_days=7,
        )
        wallet["action"] = action
        if action == "BUY":
            n_buy  += 1
        elif action == "SELL":
            n_sell += 1
        else:
            n_hold += 1

    # ── Step 4: Build signal ────────────────────────────────────────────────
    total_sm = len(smart_money)

    if total_sm < 3:
        # Not enough smart wallets tracked — signal too noisy
        result = {
            "ok": True, "supported": True,
            "score": 0, "label": "LOW COVERAGE", "color": "#8892b0",
            "detail": (
                f"Only {total_sm} smart-money wallets identified among "
                f"top {len(addresses)} {base} holders — need ≥3 for a signal. "
                f"Database is building; signal improves over time."
            ),
            "data": {
                "n_whales_buy":  n_buy,
                "n_whales_sell": n_sell,
                "n_whales_hold": n_hold,
                "total_whales":  total_sm,
                "avg_win_rate":  0.0,
                "wallets":       [],
            },
        }
    else:
        net       = n_buy - n_sell
        score_raw = (net / total_sm) * 10
        score     = round(max(-10.0, min(10.0, score_raw)), 1)
        label, color = _score_label(score)

        avg_wr = (
            sum(w["win_rate"] for w in smart_money) / total_sm * 100
        )

        detail = (
            f"{total_sm} smart-money wallets tracked (avg win rate {avg_wr:.0f}%). "
            f"Last 7 days: {n_buy} accumulating · {n_sell} distributing · {n_hold} holding. "
            f"Net score {score:+.1f}/10 → {label}."
        )

        # Truncate wallet list for UI display (no full addresses in UI)
        wallets_for_ui = [
            {
                "address_short": w["address"][:6] + "..." + w["address"][-4:],
                "win_rate":      round(w["win_rate"] * 100, 1),
                "n_trades":      w["n_trades"],
                "action":        w.get("action", "HOLD"),
            }
            for w in sorted(smart_money, key=lambda x: x["win_rate"], reverse=True)[:12]
        ]

        result = {
            "ok": True, "supported": True,
            "score":  score,
            "label":  label,
            "color":  color,
            "detail": detail,
            "data": {
                "n_whales_buy":  n_buy,
                "n_whales_sell": n_sell,
                "n_whales_hold": n_hold,
                "total_whales":  total_sm,
                "avg_win_rate":  avg_wr,
                "wallets":       wallets_for_ui,
            },
        }

    # ── Cache token signal ──────────────────────────────────────────────────
    with _DB_LOCK:
        db = _get_db()
        db.execute("""
            INSERT OR REPLACE INTO token_signals
            (symbol, contract, n_whales_buy, n_whales_sell, n_whales_hold,
             total_whales, score, label, detail, last_updated)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            base,
            contract.lower(),
            result["data"]["n_whales_buy"],
            result["data"]["n_whales_sell"],
            result["data"]["n_whales_hold"],
            result["data"]["total_whales"],
            result["score"],
            result["label"],
            result["detail"],
            int(time.time()),
        ))
        db.commit()

    return result


def _empty_data() -> dict:
    return {
        "n_whales_buy":  0, "n_whales_sell": 0,
        "n_whales_hold": 0, "total_whales":  0,
        "avg_win_rate":  0.0, "wallets":      [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Database admin helpers — exposed for Streamlit UI widgets
# ─────────────────────────────────────────────────────────────────────────────

def get_db_stats() -> dict:
    """Return summary stats about the local whale database for the UI dashboard."""
    try:
        with _DB_LOCK:
            db = _get_db()
            total  = db.execute("SELECT COUNT(*) FROM wallet_scores").fetchone()[0]
            smart  = db.execute(
                "SELECT COUNT(*) FROM wallet_scores WHERE is_smart_money=1"
            ).fetchone()[0]
            avg_wr_row = db.execute(
                "SELECT AVG(win_rate) FROM wallet_scores WHERE is_smart_money=1"
            ).fetchone()
            avg_wr = float(avg_wr_row[0] or 0)
            n_tokens = db.execute("SELECT COUNT(*) FROM token_signals").fetchone()[0]
            top_wallets = db.execute("""
                SELECT address, win_rate, n_trades, avg_hold_days
                FROM wallet_scores
                WHERE is_smart_money=1
                ORDER BY win_rate DESC
                LIMIT 10
            """).fetchall()
        return {
            "total_wallets_scanned":    total,
            "smart_money_wallets":      smart,
            "avg_smart_money_win_rate": round(avg_wr * 100, 1),
            "tokens_with_signals":      n_tokens,
            "top_wallets": [
                {
                    "address_short": row["address"][:6] + "..." + row["address"][-4:],
                    "win_rate":      round(row["win_rate"] * 100, 1),
                    "n_trades":      row["n_trades"],
                    "avg_hold_days": round(row["avg_hold_days"], 1),
                }
                for row in top_wallets
            ],
        }
    except Exception as e:
        return {
            "total_wallets_scanned": 0, "smart_money_wallets": 0,
            "avg_smart_money_win_rate": 0.0, "tokens_with_signals": 0,
            "top_wallets": [], "error": str(e),
        }


def clear_signal_cache(symbol: str = "") -> int:
    """
    Clear cached token signals (forces re-fetch on next call).
    If symbol is provided, clears only that token. Otherwise clears all.
    Returns number of rows deleted.
    """
    with _DB_LOCK:
        db = _get_db()
        if symbol:
            base = symbol.upper().replace("USDT", "").replace("USDC", "")
            db.execute("DELETE FROM token_signals WHERE symbol=?", (base,))
        else:
            db.execute("DELETE FROM token_signals")
        db.commit()
        return db.execute("SELECT changes()").fetchone()[0]


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test — python whale_tracker.py LINK [etherscan_key]
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sym = sys.argv[1] if len(sys.argv) > 1 else "LINK"
    key = sys.argv[2] if len(sys.argv) > 2 else ""

    print(f"\n{'=' * 60}")
    print(f"  Whale Tracker — Phase 6 — {sym}")
    print(f"{'=' * 60}\n")

    signal = get_token_whale_signal(sym, etherscan_api_key=key)
    print(json.dumps(signal, indent=2, default=str))

    print(f"\n{'─' * 40}")
    print("  Wallet DB Stats:")
    print(json.dumps(get_db_stats(), indent=2, default=str))
