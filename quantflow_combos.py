"""
quantflow_combos.py — Top 5 backtest-validated trade-plan combos
=================================================================

Validated by oos_audit_v3a/v3c/v3d on 134 coins, 107,682 filled trades,
date range 2021-11-08 → 2026-04-21 (~4.45 years).

Each combo is a (body × volume × ADX × regime) filter set with a
recommended trade plan (timeframe × direction × entry × TP) backed
by audit statistics: PF, mean R, sample size, and recent-period
verification.

Used by:
  - Scanner UI: 5 checkboxes filter scanner results by combo match
  - Signal cards: show which combo(s) match + audit metrics + sizing
  - AI prompt: audit context injected so Grok/Claude can decide trade/no-trade
                based on full historical evidence
"""
from __future__ import annotations

from typing import Optional


# ============================================================================
# AUDIT METADATA — date range and dataset size (for UI context)
# ============================================================================

AUDIT_DATA_START = "2021-11-08"
AUDIT_DATA_END   = "2026-04-21"
AUDIT_TIMESPAN_YEARS = 4.45
AUDIT_TOTAL_FILLED_TRADES = 107_682
AUDIT_TOTAL_COINS = 134
AUDIT_DATA_SOURCE = "Bybit spot OHLCV (v3a/v3c/v3d audit pipeline)"
AUDIT_VERSION = "v3d (Apr 27, 2026)"


# ============================================================================
# THE 5 COMBOS
# ============================================================================
# Each entry contains:
#   name       — short label used in UI badges
#   tier       — 1 = highest PF, 5 = lowest of the top 5
#   criteria   — body / vol / adx ranges + regime mode
#   rollup     — combo-as-single-strategy backtest stats
#   primary    — best-deployable trade plan (n>=30, recent-confirmed where possible)
#   tf_eligible— which timeframes show this combo on (1d/4h)
#   long_warning — note about long signals (1D longs are weak across all 5)
#   recent_check — recent period vs earlier period stats for the primary plan
# ============================================================================

COMBOS = [
    # ────────────────────────────────────────────────────────────────────
    # C6A-N — top by PF, 4H short Sniper TP2.5 strongest plan
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "C6A-N",
        "tier":  1,
        "label_short": "C6A-N (4H/1D short, body 0.7-0.8, vol 2-2.5, ADX 30-40, no regime filter)",
        "criteria": {
            "body_min":   0.70, "body_max":   0.80,
            "vol_min":    2.00, "vol_max":    2.50,
            "adx_min":    30.0, "adx_max":    40.0,
            "regime_mode": "N",        # N = no regime filter, A = aligned only
            "directions": ["long", "short"],
        },
        "tf_eligible": ["1d", "4h"],
        "rollup": {
            "n":       2058,
            "wr":      58.7,
            "mean_r": +0.259,
            "sharpe": +0.20,
            "pf":      1.58,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "short",
            "entry_zone": "Sniper",
            "tp_R":        2.5,
            "n":           51,
            "wr":          60.8,
            "mean_r":     +0.457,
            "pf":          2.02,
            "sizing":     "LARGE",     # 0.75% risk per trade
        },
        "by_timeframe": {
            "1d": {"n": 222,  "wr": 55.4, "mean_r": +0.238, "pf": 1.52},
            "4h": {"n": 1836, "wr": 59.2, "mean_r": +0.262, "pf": 1.59},
        },
        "by_direction_1d": {
            "long":  {"n": 144, "mean_r": +0.012, "pf": 1.02, "warn": True},
            "short": {"n": 78,  "mean_r": +0.655, "pf": 3.54, "warn": False},
        },
        "by_direction_4h": {
            "long":  {"n": 870, "mean_r": +0.189, "pf": 1.39, "warn": False},
            "short": {"n": 966, "mean_r": +0.328, "pf": 1.79, "warn": False},
        },
        "long_warning": "1D LONG mean R is barely positive (+0.012); avoid sizing up.",
        "recent_check": {
            "earlier": "Nov23-Jun25: rollup mean +0.224 PF 1.48",
            "recent":  "Jul25-Apr26: rollup mean +0.344 PF 1.84",
            "verdict": "GETTING STRONGER recently",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # C6A-A — same as C6A-N but regime-aligned. 1D dominates here.
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "C6A-A",
        "tier":  2,
        "label_short": "C6A-A (1D/4H short, body 0.7-0.8, vol 2-2.5, ADX 30-40, regime aligned)",
        "criteria": {
            "body_min":   0.70, "body_max":   0.80,
            "vol_min":    2.00, "vol_max":    2.50,
            "adx_min":    30.0, "adx_max":    40.0,
            "regime_mode": "A",
            "directions": ["long", "short"],
        },
        "tf_eligible": ["1d", "4h"],
        "rollup": {
            "n":       1728,
            "wr":      56.8,
            "mean_r": +0.216,
            "sharpe": +0.17,
            "pf":      1.46,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "short",
            "entry_zone": "Sniper",
            "tp_R":        3.0,
            "n":           41,
            "wr":          56.1,
            "mean_r":     +0.413,
            "pf":          1.81,
            "sizing":     "LARGE",
        },
        "by_timeframe": {
            "1d": {"n": 198,  "wr": 62.1, "mean_r": +0.397, "pf": 2.03},
            "4h": {"n": 1530, "wr": 56.1, "mean_r": +0.192, "pf": 1.40},
        },
        "by_direction_1d": {
            "long":  {"n": 132, "mean_r": +0.115, "pf": 1.22, "warn": False},
            "short": {"n": 66,  "mean_r": +0.961, "pf": 9.23, "warn": False},
        },
        "by_direction_4h": {
            "long":  {"n": 777, "mean_r": +0.142, "pf": 1.28, "warn": False},
            "short": {"n": 753, "mean_r": +0.244, "pf": 1.53, "warn": False},
        },
        "long_warning": None,
        "recent_check": {
            "earlier": "Nov23-Jun25: rollup mean +0.161 PF 1.32",
            "recent":  "Jul25-Apr26: rollup mean +0.346 PF 1.86",
            "verdict": "MUCH STRONGER recently",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # C5B-A — body 0.7-0.8 + vol 1.5-2.0 + ADX 40-50 aligned
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "C5B-A",
        "tier":  3,
        "label_short": "C5B-A (1D short, body 0.7-0.8, vol 1.5-2, ADX 40-50, regime aligned)",
        "criteria": {
            "body_min":   0.70, "body_max":   0.80,
            "vol_min":    1.50, "vol_max":    2.00,
            "adx_min":    40.0, "adx_max":    50.0,
            "regime_mode": "A",
            "directions": ["long", "short"],
        },
        "tf_eligible": ["1d", "4h"],
        "rollup": {
            "n":       1869,
            "wr":      55.9,
            "mean_r": +0.183,
            "sharpe": +0.15,
            "pf":      1.39,
        },
        "primary": {
            "tf":         "1d",
            "direction":  "short",
            "entry_zone": "Aggressive",
            "tp_R":        3.0,
            "n":           31,
            "wr":          61.3,
            "mean_r":     +0.374,
            "pf":          2.02,
            "sizing":     "LARGE",
        },
        "by_timeframe": {
            "1d": {"n": 336,  "wr": 57.1, "mean_r": +0.216, "pf": 1.51},
            "4h": {"n": 1533, "wr": 55.6, "mean_r": +0.176, "pf": 1.37},
        },
        "by_direction_1d": {
            "long":  {"n": 99,  "mean_r": -0.087, "pf": 0.86, "warn": True},
            "short": {"n": 237, "mean_r": +0.343, "pf": 2.01, "warn": False},
        },
        "by_direction_4h": {
            "long":  {"n": 615, "mean_r": +0.106, "pf": 1.21, "warn": False},
            "short": {"n": 918, "mean_r": +0.223, "pf": 1.50, "warn": False},
        },
        "long_warning": "1D LONG is NEGATIVE (-0.087 mean, PF 0.86); avoid 1D longs entirely.",
        "recent_check": {
            "earlier": "Nov23-Jun25: rollup mean +0.246 PF 1.54",
            "recent":  "Jul25-Apr26: rollup mean +0.081 PF 1.17",
            "verdict": "STILL POSITIVE but weaker recently",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # C5B-N — same as C5B-A without regime filter
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "C5B-N",
        "tier":  4,
        "label_short": "C5B-N (1D short, body 0.7-0.8, vol 1.5-2, ADX 40-50, no regime filter)",
        "criteria": {
            "body_min":   0.70, "body_max":   0.80,
            "vol_min":    1.50, "vol_max":    2.00,
            "adx_min":    40.0, "adx_max":    50.0,
            "regime_mode": "N",
            "directions": ["long", "short"],
        },
        "tf_eligible": ["1d", "4h"],
        "rollup": {
            "n":       2094,
            "wr":      54.6,
            "mean_r": +0.148,
            "sharpe": +0.12,
            "pf":      1.31,
        },
        "primary": {
            "tf":         "1d",
            "direction":  "short",
            "entry_zone": "Aggressive",
            "tp_R":        3.0,
            "n":           31,
            "wr":          61.3,
            "mean_r":     +0.374,
            "pf":          2.02,
            "sizing":     "LARGE",
        },
        "by_timeframe": {
            "1d": {"n": 336,  "wr": 57.1, "mean_r": +0.216, "pf": 1.51},
            "4h": {"n": 1758, "wr": 54.1, "mean_r": +0.135, "pf": 1.28},
        },
        "by_direction_1d": {
            "long":  {"n": 99,  "mean_r": -0.087, "pf": 0.86, "warn": True},
            "short": {"n": 237, "mean_r": +0.343, "pf": 2.01, "warn": False},
        },
        "by_direction_4h": {
            "long":  {"n": 672,  "mean_r": +0.076, "pf": 1.15, "warn": False},
            "short": {"n": 1086, "mean_r": +0.171, "pf": 1.36, "warn": False},
        },
        "long_warning": "1D LONG is NEGATIVE (-0.087 mean, PF 0.86); avoid 1D longs entirely.",
        "recent_check": {
            "earlier": "Nov23-Jun25: rollup mean +0.198 PF 1.42",
            "recent":  "Jul25-Apr26: rollup mean +0.059 PF 1.12",
            "verdict": "STILL POSITIVE but weaker recently",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # C1A-A — body 0.5-0.6, the highest mean R per trade in primary plan
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "C1A-A",
        "tier":  5,
        "label_short": "C1A-A (1D short, body 0.5-0.6, vol 1.5-2, ADX 30-40, regime aligned) ⭐BEST mean R",
        "criteria": {
            "body_min":   0.50, "body_max":   0.60,
            "vol_min":    1.50, "vol_max":    2.00,
            "adx_min":    30.0, "adx_max":    40.0,
            "regime_mode": "A",
            "directions": ["long", "short"],
        },
        "tf_eligible": ["1d", "4h"],
        "rollup": {
            "n":       4236,
            "wr":      55.3,
            "mean_r": +0.137,
            "sharpe": +0.12,
            "pf":      1.30,
        },
        "primary": {
            "tf":         "1d",
            "direction":  "short",
            "entry_zone": "Standard",
            "tp_R":        2.5,
            "n":           40,
            "wr":          72.5,
            "mean_r":     +0.482,    # highest mean R of all 5 primary plans
            "pf":          2.89,
            "sizing":     "LARGE",
        },
        "by_timeframe": {
            "1d": {"n": 726,  "wr": 62.8, "mean_r": +0.309, "pf": 1.83},
            "4h": {"n": 3510, "wr": 53.8, "mean_r": +0.102, "pf": 1.21},
        },
        "by_direction_1d": {
            "long":  {"n": 309, "mean_r": +0.214, "pf": 1.47, "warn": False},
            "short": {"n": 417, "mean_r": +0.379, "pf": 2.23, "warn": False},
        },
        "by_direction_4h": {
            "long":  {"n": 1812, "mean_r": +0.053, "pf": 1.10, "warn": False},
            "short": {"n": 1698, "mean_r": +0.153, "pf": 1.34, "warn": False},
        },
        "long_warning": None,
        "recent_check": {
            "earlier": "Nov23-Jun25: rollup mean +0.134 PF 1.28",
            "recent":  "Jul25-Apr26: rollup mean +0.143 PF 1.34",
            "verdict": "STABLE — held up well in recent period",
        },
    },

    # ════════════════════════════════════════════════════════════════════════
    # TIER 2 — RANK 6-10 in v3c rollup ranking. Lower PF (1.14-1.23) but
    # still positive expectancy. Use as SECONDARY filter when no Tier 1
    # match available. Honest caveats apply: most have weakened in recent
    # period (rollup Δ -0.08 to -0.20R Jul 2025+). Treat as exploratory
    # rather than primary.
    # ════════════════════════════════════════════════════════════════════════

    # ────────────────────────────────────────────────────────────────────
    # C2A-A — Tier 2 #1 (rank 6 overall). 4H short carries the edge.
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "C2A-A",
        "tier":  6,
        "label_short": "C2A-A (4H short, body 0.5-0.6, vol 2-2.5, ADX 30-40, aligned) — TIER 2",
        "criteria": {
            "body_min":   0.50, "body_max":   0.60,
            "vol_min":    2.00, "vol_max":    2.50,
            "adx_min":    30.0, "adx_max":    40.0,
            "regime_mode": "A",
            "directions": ["long", "short"],
        },
        "tf_eligible": ["1d", "4h"],
        "rollup": {
            "n":       2127,
            "wr":      53.2,
            "mean_r": +0.116,
            "sharpe": +0.09,
            "pf":      1.23,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "short",
            "entry_zone": "Aggressive",
            "tp_R":        2.0,
            "n":           106,
            "wr":          63.2,
            "mean_r":     +0.365,
            "pf":          1.99,
            "sizing":     "LARGE",
        },
        "by_timeframe": {
            "1d": {"n": 246,  "wr": 47.6, "mean_r": -0.078, "pf": 0.86},
            "4h": {"n": 1881, "wr": 53.9, "mean_r": +0.141, "pf": 1.29},
        },
        "by_direction_1d": {
            "long":  {"n": 111, "mean_r": -0.403, "pf": 0.43, "warn": True},
            "short": {"n": 135, "mean_r": +0.190, "pf": 1.44, "warn": False},
        },
        "by_direction_4h": {
            "long":  {"n": 975, "mean_r": +0.020, "pf": 1.04, "warn": False},
            "short": {"n": 906, "mean_r": +0.272, "pf": 1.63, "warn": False},
        },
        "long_warning": "1D LONG is CATASTROPHIC (-0.403 mean, PF 0.43); avoid 1D longs entirely.",
        "recent_check": {
            "earlier": "Nov23-Jun25: rollup mean +0.183 PF 1.38",
            "recent":  "Jul25-Apr26: rollup mean -0.015 PF 0.97",
            "verdict": "WEAKER recently (Δ -0.20R) — exercise caution",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # C2B-A — Tier 2 #2 (rank 7). ADX 40-50 narrows it. 4H long surprise winner.
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "C2B-A",
        "tier":  7,
        "label_short": "C2B-A (4H long, body 0.5-0.6, vol 2-2.5, ADX 40-50, aligned) — TIER 2",
        "criteria": {
            "body_min":   0.50, "body_max":   0.60,
            "vol_min":    2.00, "vol_max":    2.50,
            "adx_min":    40.0, "adx_max":    50.0,
            "regime_mode": "A",
            "directions": ["long", "short"],
        },
        "tf_eligible": ["1d", "4h"],
        "rollup": {
            "n":       1200,
            "wr":      53.0,
            "mean_r": +0.094,
            "sharpe": +0.08,
            "pf":      1.19,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "long",
            "entry_zone": "Aggressive",
            "tp_R":        2.5,
            "n":           38,
            "wr":          57.9,
            "mean_r":     +0.234,
            "pf":          1.54,
            "sizing":     "FULL",   # mean R 0.15-0.30 → FULL not LARGE
        },
        "by_timeframe": {
            "1d": {"n": 114,  "wr": 52.0, "mean_r": +0.058, "pf": 1.13},
            "4h": {"n": 1086, "wr": 53.1, "mean_r": +0.098, "pf": 1.20},
        },
        "by_direction_1d": {
            "long":  {"n": 6,   "mean_r": -0.250, "pf": 0.45, "warn": True},
            "short": {"n": 108, "mean_r": +0.076, "pf": 1.17, "warn": False},
        },
        "by_direction_4h": {
            "long":  {"n": 348, "mean_r": +0.130, "pf": 1.26, "warn": False},
            "short": {"n": 738, "mean_r": +0.082, "pf": 1.17, "warn": False},
        },
        "long_warning": None,
        "recent_check": {
            "earlier": "Nov23-Jun25: rollup mean +0.122 PF 1.24",
            "recent":  "Jul25-Apr26: rollup mean +0.037 PF 1.08",
            "verdict": "WEAKER recently (Δ -0.09R) — still positive",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # C2B-N — Tier 2 #3 (rank 8). C2B-A without regime filter. 4H long.
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "C2B-N",
        "tier":  8,
        "label_short": "C2B-N (4H long, body 0.5-0.6, vol 2-2.5, ADX 40-50, no filter) — TIER 2",
        "criteria": {
            "body_min":   0.50, "body_max":   0.60,
            "vol_min":    2.00, "vol_max":    2.50,
            "adx_min":    40.0, "adx_max":    50.0,
            "regime_mode": "N",
            "directions": ["long", "short"],
        },
        "tf_eligible": ["1d", "4h"],
        "rollup": {
            "n":       1407,
            "wr":      52.5,
            "mean_r": +0.082,
            "sharpe": +0.07,
            "pf":      1.17,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "long",
            "entry_zone": "Aggressive",
            "tp_R":        2.5,
            "n":           48,
            "wr":          56.2,
            "mean_r":     +0.240,
            "pf":          1.53,
            "sizing":     "FULL",
        },
        "by_timeframe": {
            "1d": {"n": 126,  "wr": 51.6, "mean_r": +0.060, "pf": 1.14},
            "4h": {"n": 1281, "wr": 52.6, "mean_r": +0.085, "pf": 1.17},
        },
        "by_direction_1d": {
            "long":  {"n": 18,  "mean_r": -0.180, "pf": 0.55, "warn": True},
            "short": {"n": 108, "mean_r": +0.076, "pf": 1.17, "warn": False},
        },
        "by_direction_4h": {
            "long":  {"n": 441, "mean_r": +0.141, "pf": 1.28, "warn": False},
            "short": {"n": 840, "mean_r": +0.055, "pf": 1.11, "warn": False},
        },
        "long_warning": None,
        "recent_check": {
            "earlier": "Nov23-Jun25: rollup mean +0.119 PF 1.24",
            "recent":  "Jul25-Apr26: rollup mean +0.016 PF 1.03",
            "verdict": "WEAKER recently (Δ -0.10R) — caution",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # C1A-N — Tier 2 #4 (rank 9). Largest sample, MOST STABLE recent.
    #         Note: 1D timeframe is the strong slice here, not 4H.
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "C1A-N",
        "tier":  9,
        "label_short": "C1A-N (1D short, body 0.5-0.6, vol 1.5-2, ADX 30-40, no filter) — TIER 2 ✓most stable",
        "criteria": {
            "body_min":   0.50, "body_max":   0.60,
            "vol_min":    1.50, "vol_max":    2.00,
            "adx_min":    30.0, "adx_max":    40.0,
            "regime_mode": "N",
            "directions": ["long", "short"],
        },
        "tf_eligible": ["1d", "4h"],
        "rollup": {
            "n":       5355,
            "wr":      52.7,
            "mean_r": +0.081,
            "sharpe": +0.07,
            "pf":      1.16,
        },
        "primary": {
            "tf":         "1d",
            "direction":  "short",
            "entry_zone": "Standard",
            "tp_R":        2.5,
            "n":           43,
            "wr":          72.1,
            "mean_r":     +0.505,
            "pf":          2.94,
            "sizing":     "LARGE",
        },
        "by_timeframe": {
            "1d": {"n": 777,  "wr": 60.2, "mean_r": +0.328, "pf": 1.90},
            "4h": {"n": 4578, "wr": 51.4, "mean_r": +0.039, "pf": 1.08},
        },
        "by_direction_1d": {
            "long":  {"n": 330, "mean_r": +0.237, "pf": 1.55, "warn": False},
            "short": {"n": 447, "mean_r": +0.395, "pf": 2.26, "warn": False},
        },
        "by_direction_4h": {
            "long":  {"n": 2217, "mean_r": -0.031, "pf": 0.94, "warn": True},
            "short": {"n": 2361, "mean_r": +0.104, "pf": 1.22, "warn": False},
        },
        "long_warning": "4H LONG is mean-NEGATIVE (-0.031, PF 0.94). 1D longs are OK; 4H longs are not.",
        "recent_check": {
            "earlier": "Nov23-Jun25: rollup mean +0.096 PF 1.19",
            "recent":  "Jul25-Apr26: rollup mean +0.051 PF 1.11",
            "verdict": "STABLE — held up well, only Tier 2 to do so",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # C2A-N — Tier 2 #5 (rank 10). 4H short carries it. 1D is dangerous.
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "C2A-N",
        "tier":  10,
        "label_short": "C2A-N (4H short, body 0.5-0.6, vol 2-2.5, ADX 30-40, no filter) — TIER 2",
        "criteria": {
            "body_min":   0.50, "body_max":   0.60,
            "vol_min":    2.00, "vol_max":    2.50,
            "adx_min":    30.0, "adx_max":    40.0,
            "regime_mode": "N",
            "directions": ["long", "short"],
        },
        "tf_eligible": ["1d", "4h"],
        "rollup": {
            "n":       2637,
            "wr":      52.0,
            "mean_r": +0.073,
            "sharpe": +0.06,
            "pf":      1.14,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "short",
            "entry_zone": "Aggressive",
            "tp_R":        2.0,
            "n":           135,
            "wr":          61.5,
            "mean_r":     +0.281,
            "pf":          1.72,
            "sizing":     "LARGE",
        },
        "by_timeframe": {
            "1d": {"n": 267,  "wr": 47.2, "mean_r": -0.040, "pf": 0.93},
            "4h": {"n": 2370, "wr": 52.5, "mean_r": +0.086, "pf": 1.17},
        },
        "by_direction_1d": {
            "long":  {"n": 120, "mean_r": -0.460, "pf": 0.37, "warn": True},
            "short": {"n": 147, "mean_r": +0.304, "pf": 1.77, "warn": False},
        },
        "by_direction_4h": {
            "long":  {"n": 1197, "mean_r": -0.021, "pf": 0.96, "warn": True},
            "short": {"n": 1173, "mean_r": +0.194, "pf": 1.42, "warn": False},
        },
        "long_warning": "1D LONG is CATASTROPHIC (-0.460 mean, PF 0.37); 4H LONG is also negative. Avoid all longs.",
        "recent_check": {
            "earlier": "Nov23-Jun25: rollup mean +0.126 PF 1.25",
            "recent":  "Jul25-Apr26: rollup mean -0.030 PF 0.94",
            "verdict": "WEAKER recently (Δ -0.16R) — caution",
        },
    },
]

# ════════════════════════════════════════════════════════════════════════════
# TIER 3 — COUNTERTREND / MEAN-REVERSION COMBOS (v3e + v3f audit)
# ════════════════════════════════════════════════════════════════════════════
#
# Fundamentally different from Tier 1/2 (trend-following). These combos look
# for STRONG-MOMENTUM candles (body 75%+ AND vol 3x+ as universal min) that
# represent EXHAUSTION of the current move — and recommend a COUNTERTREND
# trade in the OPPOSITE direction:
#
#   Strong BULLISH candle  →  COUNTERTREND combo says: SHORT the next wick UP
#   Strong BEARISH candle  →  COUNTERTREND combo says: LONG  the next wick DOWN
#
# Each combo has its own optimal:
#   - body band         (0.80-0.85, 0.85-0.90, 0.90+)
#   - vol band          (4-5x, 5-6x, 6-7x, 8x+)
#   - entry retrace     (0.00, -0.05, -0.10, -0.15, -0.20, -0.27)
#                        Negative retrace = wick AGAINST the signal candle's direction
#   - SL method         (fixed 1.5%, 1.5x ATR, wick anchor)
#   - TP target         (2.0R, 2.5R, 3.0R)
#
# These primary plans were curated by v3f to require BOTH:
#   - all-time mean R > 0.20
#   - recent mean R > 0.20 (Jul 2025+)
#   - recent n >= 13 (some are smaller, treat exploratory)
#
# IMPORTANT — CLASSIFIER DIFFERENCE:
# The scanner emits LONG signals on bullish candles, SHORT signals on bearish.
# A countertrend combo on a bullish candle would receive `direction='long'`
# from scanner (because scanner views it as long-momentum). The combo's
# `signal_direction_required` field tells us WHICH scanner direction this
# countertrend combo cares about. Then the combo's `primary.direction` says
# what actual trade to take (the OPPOSITE of the scanner's view).
#
# All combos here use combo_type="countertrend" — Tier 1/2 default to
# combo_type="trend_following".
#
# ════════════════════════════════════════════════════════════════════════════

COUNTERTREND_COMBOS = [
    # ────────────────────────────────────────────────────────────────────
    # CT1 — strongest by recent mean R: 4H long after strong BEAR candle
    #         Bucket: body 0.85-0.90 + vol 6-7x bear candles → fade with LONG
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "CT1",
        "tier":  11,
        "combo_type": "countertrend",
        "label_short": "CT1 (4H LONG after strong BEAR candle, body 0.85-0.90, vol 6-7×) — TIER 3 COUNTERTREND",
        "criteria": {
            "body_min":   0.85, "body_max":   0.90,
            "vol_min":    6.00, "vol_max":    7.00,
            "adx_min":    0.0,  "adx_max":    999.0,   # ADX not a filter for countertrend
            "regime_mode": "N",                         # no regime filter
            "directions": ["short"],                    # scanner emits SHORT on bearish-momentum
            "signal_direction_required": "short",       # we look for scanner SHORT signals
            "trade_direction":           "long",        # but execute LONG (countertrend)
        },
        "tf_eligible": ["4h"],
        "rollup": {
            "n":       1206,
            "wr":      54.4,
            "mean_r": +0.315,
            "sharpe": +0.21,
            "pf":      1.60,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "long",                        # COUNTERTREND
            "entry_retrace": -0.050,                     # wick down 5% of body
            "sl_method":     "wick_anchor",
            "tp_R":          3.0,
            "n":             28,
            "wr":            57.1,
            "mean_r":       +0.765,
            "pf":            2.45,
            "sizing":       "LARGE",
        },
        "recent_check": {
            "earlier": "Jul21-Jun25: rollup mean +0.181 PF 1.36",
            "recent":  "Jul25-Apr26: rollup mean +0.534 PF 2.19",
            "verdict": "MUCH STRONGER recently — exhaustion fades intensifying",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # CT2 — 4H long after strong BEAR candle, body 0.80-0.85, vol 5-6x
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "CT2",
        "tier":  12,
        "combo_type": "countertrend",
        "label_short": "CT2 (4H LONG after strong BEAR candle, body 0.80-0.85, vol 5-6×) — TIER 3 COUNTERTREND",
        "criteria": {
            "body_min":   0.80, "body_max":   0.85,
            "vol_min":    5.00, "vol_max":    6.00,
            "adx_min":    0.0,  "adx_max":    999.0,
            "regime_mode": "N",
            "directions": ["short"],
            "signal_direction_required": "short",
            "trade_direction":           "long",
        },
        "tf_eligible": ["4h"],
        "rollup": {
            "n":       2169,
            "wr":      52.1,
            "mean_r": +0.180,
            "sharpe": +0.13,
            "pf":      1.31,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "long",
            "entry_retrace": -0.100,                     # wick down 10% of body
            "sl_method":     "wick_anchor",
            "tp_R":          3.0,
            "n":             44,
            "wr":            54.5,
            "mean_r":       +0.702,
            "pf":            2.23,
            "sizing":       "LARGE",
        },
        "recent_check": {
            "earlier": "Jul21-Jun25: rollup mean +0.165 PF 1.28",
            "recent":  "Jul25-Apr26: rollup mean +0.204 PF 1.40",
            "verdict": "STABLE / mildly stronger recently",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # CT3 — 4H long after strong BEAR candle, body 0.85-0.90, vol 4-5x
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "CT3",
        "tier":  13,
        "combo_type": "countertrend",
        "label_short": "CT3 (4H LONG after strong BEAR candle, body 0.85-0.90, vol 4-5×) — TIER 3 COUNTERTREND",
        "criteria": {
            "body_min":   0.85, "body_max":   0.90,
            "vol_min":    4.00, "vol_max":    5.00,
            "adx_min":    0.0,  "adx_max":    999.0,
            "regime_mode": "N",
            "directions": ["short"],
            "signal_direction_required": "short",
            "trade_direction":           "long",
        },
        "tf_eligible": ["4h"],
        "rollup": {
            "n":       3555,
            "wr":      50.0,
            "mean_r": +0.045,
            "sharpe": +0.03,
            "pf":      1.07,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "long",
            "entry_retrace": 0.000,                      # immediate at close
            "sl_method":     "wick_anchor",
            "tp_R":          3.0,
            "n":             83,
            "wr":            48.2,
            "mean_r":       +0.434,
            "pf":            1.68,
            "sizing":       "LARGE",
        },
        "recent_check": {
            "earlier": "Jul21-Jun25: rollup mean -0.057 PF 0.91",
            "recent":  "Jul25-Apr26: rollup mean +0.254 PF 1.45",
            "verdict": "TURNED POSITIVE recently — was a loser, now profitable",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # CT4 — 4H long after VERY strong BEAR candle (vol 8+) — biggest edge
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "CT4",
        "tier":  14,
        "combo_type": "countertrend",
        "label_short": "CT4 (4H LONG after VERY strong BEAR candle, body 0.90+, vol 8x+) — TIER 3 COUNTERTREND ⭐",
        "criteria": {
            "body_min":   0.90, "body_max":   1.01,
            "vol_min":    8.00, "vol_max":    99.0,
            "adx_min":    0.0,  "adx_max":    999.0,
            "regime_mode": "N",
            "directions": ["short"],
            "signal_direction_required": "short",
            "trade_direction":           "long",
        },
        "tf_eligible": ["4h"],
        "rollup": {
            "n":       2070,
            "wr":      53.1,
            "mean_r": +0.229,
            "sharpe": +0.16,
            "pf":      1.39,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "long",
            "entry_retrace": -0.270,                     # wait for deep wick down
            "sl_method":     "atr_1.5x",
            "tp_R":          3.0,
            "n":             26,
            "wr":            61.5,
            "mean_r":       +0.666,
            "pf":            2.56,
            "sizing":       "LARGE",
        },
        "recent_check": {
            "earlier": "Jul21-Jun25: rollup mean +0.080 PF 1.13",
            "recent":  "Jul25-Apr26: rollup mean +0.424 PF 1.80",
            "verdict": "MUCH STRONGER recently — extreme-vol fades work best",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # CT5 — 4H short after strong BULL candle, body 0.85-0.90, vol 6-7x
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "CT5",
        "tier":  15,
        "combo_type": "countertrend",
        "label_short": "CT5 (4H SHORT after strong BULL candle, body 0.85-0.90, vol 6-7×) — TIER 3 COUNTERTREND",
        "criteria": {
            "body_min":   0.85, "body_max":   0.90,
            "vol_min":    6.00, "vol_max":    7.00,
            "adx_min":    0.0,  "adx_max":    999.0,
            "regime_mode": "N",
            "directions": ["long"],                       # scanner emits LONG on bullish-momentum
            "signal_direction_required": "long",
            "trade_direction":           "short",         # but we SHORT (countertrend)
        },
        "tf_eligible": ["4h"],
        "rollup": {
            "n":       1494,
            "wr":      53.4,
            "mean_r": +0.320,
            "sharpe": +0.21,
            "pf":      1.61,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "short",
            "entry_retrace": -0.150,                      # wick up 15% of body
            "sl_method":     "fixed_1.5pct",
            "tp_R":          3.0,
            "n":             28,
            "wr":            50.0,
            "mean_r":       +0.586,
            "pf":            2.08,
            "sizing":       "LARGE",
        },
        "recent_check": {
            "earlier": "Jul21-Jun25: rollup mean +0.222 PF 1.41",
            "recent":  "Jul25-Apr26: rollup mean +0.405 PF 1.81",
            "verdict": "STRONGER recently — exhaustion fade alive",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # CT6 — 4H short after strong BULL candle, body 0.90+, vol 5-6x
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "CT6",
        "tier":  16,
        "combo_type": "countertrend",
        "label_short": "CT6 (4H SHORT after strong BULL candle, body 0.90+, vol 5-6×) — TIER 3 COUNTERTREND",
        "criteria": {
            "body_min":   0.90, "body_max":   1.01,
            "vol_min":    5.00, "vol_max":    6.00,
            "adx_min":    0.0,  "adx_max":    999.0,
            "regime_mode": "N",
            "directions": ["long"],
            "signal_direction_required": "long",
            "trade_direction":           "short",
        },
        "tf_eligible": ["4h"],
        "rollup": {
            "n":       3051,
            "wr":      48.9,
            "mean_r": +0.154,
            "sharpe": +0.10,
            "pf":      1.24,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "short",
            "entry_retrace": -0.270,                      # deep wick up
            "sl_method":     "fixed_1.5pct",
            "tp_R":          3.0,
            "n":             45,
            "wr":            44.4,
            "mean_r":       +0.422,
            "pf":            1.67,
            "sizing":       "LARGE",
        },
        "recent_check": {
            "earlier": "Jul21-Jun25: rollup mean -0.024 PF 0.96",
            "recent":  "Jul25-Apr26: rollup mean +0.421 PF 1.78",
            "verdict": "TURNED POSITIVE recently — extreme-body fades intensifying",
        },
    },

    # ────────────────────────────────────────────────────────────────────
    # CT7 — 4H short after strong BULL candle, body 0.80-0.85, vol 5-6x
    # ────────────────────────────────────────────────────────────────────
    {
        "name":  "CT7",
        "tier":  17,
        "combo_type": "countertrend",
        "label_short": "CT7 (4H SHORT after strong BULL candle, body 0.80-0.85, vol 5-6×) — TIER 3 COUNTERTREND",
        "criteria": {
            "body_min":   0.80, "body_max":   0.85,
            "vol_min":    5.00, "vol_max":    6.00,
            "adx_min":    0.0,  "adx_max":    999.0,
            "regime_mode": "N",
            "directions": ["long"],
            "signal_direction_required": "long",
            "trade_direction":           "short",
        },
        "tf_eligible": ["4h"],
        "rollup": {
            "n":       3114,
            "wr":      45.6,
            "mean_r": -0.106,
            "sharpe": -0.07,
            "pf":      0.85,
        },
        "primary": {
            "tf":         "4h",
            "direction":  "short",
            "entry_retrace": 0.000,                       # immediate fill
            "sl_method":     "fixed_1.5pct",
            "tp_R":          3.0,
            "n":             71,
            "wr":            47.9,
            "mean_r":       +0.346,
            "pf":            1.59,
            "sizing":       "FULL",                       # mean R 0.30-0.40, FULL not LARGE
        },
        "recent_check": {
            "earlier": "Jul21-Jun25: rollup mean -0.260 PF 0.69",
            "recent":  "Jul25-Apr26: rollup mean +0.172 PF 1.30",
            "verdict": "FLIPPED POSITIVE recently — earlier was very bad, now positive",
        },
    },
]

# Append countertrend combos to main list so existing iteration works
COMBOS = COMBOS + COUNTERTREND_COMBOS

# Map for fast lookup by name
COMBOS_BY_NAME = {c["name"]: c for c in COMBOS}


# ============================================================================
# CLASSIFIER — does a signal match a combo?
# ============================================================================

def _is_regime_aligned(direction: str, btc_regime: str) -> bool:
    """
    Regime alignment rule for combo *-A variants.
    Long is allowed in BULL or CHOP; short is allowed in BEAR or CHOP.
    Trades fighting the regime (long-in-BEAR, short-in-BULL) are excluded.
    """
    if direction == "long":  return btc_regime in ("BULL", "CHOP")
    if direction == "short": return btc_regime in ("BEAR", "CHOP")
    return False


def signal_matches_combo(sig: dict, combo: dict, btc_regime: str = None) -> bool:
    """
    Check whether a scanner signal matches a combo's criteria.

    Inputs:
      sig          a signal dict from _scanner_score_signal — must contain
                   body_pct (signed), vol_mult, adx, direction, timeframe
      combo        one entry from COMBOS
      btc_regime   "BULL"/"BEAR"/"CHOP" — required for *-A combos. If None,
                   *-A combos return False (cannot verify alignment).

    Two combo types are supported:
      - "trend_following" (default for Tier 1/2): the scanner's direction IS
        the trade direction. Combo matches when the signal's body/vol/adx fall
        in range AND scanner direction is in `criteria.directions`.
      - "countertrend"    (Tier 3): the scanner's direction is the SETUP
        direction (i.e. scanner sees a bullish-momentum candle = LONG signal),
        but the combo recommends the OPPOSITE trade. The combo's
        `signal_direction_required` field specifies which scanner direction
        triggers it; `trade_direction` is what to actually execute.
        ADX is NOT a filter for countertrend (criteria.adx_min/max set wide).
        Body and vol bands are tighter and based on momentum exhaustion.

    Returns True only if all criteria pass.
    """
    crit = combo["criteria"]
    combo_type = combo.get("combo_type", "trend_following")

    # Timeframe must be in the eligible list (case-insensitive normalize)
    tf_norm = (sig.get("timeframe", "") or "").lower()
    if tf_norm not in combo["tf_eligible"]:
        return False

    # Direction check differs by combo type
    sig_dir = sig.get("direction", "")
    if combo_type == "countertrend":
        # Scanner direction MUST equal the combo's signal_direction_required
        # (i.e. for a "fade bullish exhaustion" combo, scanner must have
        # emitted a LONG signal because that's how it labeled the bullish
        # candle — we then take the OPPOSITE trade).
        if sig_dir != crit.get("signal_direction_required", ""):
            return False
    else:
        if sig_dir not in crit["directions"]:
            return False

    # Body / vol / adx within range. body_pct is signed in scanner — use absolute.
    try:
        body_abs = abs(float(sig.get("body_pct", 0)))
        vol_mult = float(sig.get("vol_mult", 0))
        adx      = float(sig.get("adx", 0))
    except (TypeError, ValueError):
        return False
    if not (crit["body_min"] <= body_abs   < crit["body_max"]):  return False
    if not (crit["vol_min"]  <= vol_mult   < crit["vol_max"]):   return False
    if not (crit["adx_min"]  <= adx        < crit["adx_max"]):   return False

    # Regime check for *-A combos (only trend-following uses regime_mode "A")
    if crit["regime_mode"] == "A":
        if btc_regime is None: return False
        if not _is_regime_aligned(sig["direction"], btc_regime): return False
    return True


def get_matching_combos(sig: dict, enabled_combos: list[str],
                        btc_regime: str = None,
                        allowed_levels=None) -> list[dict]:
    """
    Return the list of combos this signal matches, restricted to combos
    in `enabled_combos` (the user's checkbox selection).
    Sorted by tier (lowest tier first = highest PF first).

    `allowed_levels` (bar-offset age filter) is accepted for API compatibility
    but is intentionally unused here — age filtering is applied to the signal
    list before this function is called, so it has no effect on combo matching.
    """
    matches = []
    for combo in COMBOS:
        if combo["name"] not in enabled_combos: continue
        if signal_matches_combo(sig, combo, btc_regime=btc_regime):
            matches.append(combo)
    matches.sort(key=lambda c: c["tier"])
    return matches


def get_primary_combo(matches: list[dict]) -> Optional[dict]:
    """Highest-PF combo from a match list (lowest tier number)."""
    if not matches: return None
    return matches[0]   # already sorted by tier


# ============================================================================
# UI HTML RENDERING
# ============================================================================

def _sizing_badge_html(sizing: str) -> str:
    """Color-coded sizing badge for the trade plan."""
    colors = {
        "LARGE": ("#1a4731", "#34d399"),   # bg, text
        "FULL":  ("#1e3a5f", "#60a5fa"),
        "HALF":  ("#3f3a16", "#fbbf24"),
        "SMALL": ("#3f1d1d", "#f87171"),
    }
    bg, fg = colors.get(sizing, ("#22272e", "#ccd6f6"))
    sizing_pct = {
        "LARGE": "0.75%", "FULL": "0.50%", "HALF": "0.25%", "SMALL": "0.15%",
    }.get(sizing, "0.50%")
    return (
        f'<span style="display:inline-block;background:{bg};color:{fg};'
        f'padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;'
        f'letter-spacing:0.5px;">{sizing} · {sizing_pct} risk</span>'
    )


def render_combo_panel_html(matches: list[dict], sig: dict) -> str:
    """
    Render a panel showing all matching combos with full audit metrics.
    Used in scanner cards. Highlights the primary (highest-PF) combo first.
    """
    if not matches:
        return ""

    primary = matches[0]
    overlap = matches[1:]   # other combos that also match

    sig_dir = sig.get("direction", "?")
    sig_tf  = (sig.get("timeframe", "") or "").lower()

    # Header — primary combo
    p = primary
    pp = p["primary"]
    rollup = p["rollup"]
    combo_type = p.get("combo_type", "trend_following")
    is_countertrend = (combo_type == "countertrend")

    # Direction agreement check.
    # For trend-following: signal direction = trade direction. ✅ when matched.
    # For countertrend: signal direction is the SETUP (e.g. scanner emits LONG
    # for bullish-momentum candle), but the combo plan says trade the OPPOSITE.
    # So a "match" means the scanner's direction equals signal_direction_required
    # AND the combo's plan direction is the opposite.
    if is_countertrend:
        plan_matches_signal = True   # by construction (combo classifier already validated)
        plan_match_marker = "🔄"     # countertrend marker
    else:
        plan_matches_signal = (sig_tf == pp["tf"] and sig_dir == pp["direction"])
        plan_match_marker = "✅" if plan_matches_signal else "⚠️"

    # Long warning (only applies to trend-following combos that have one)
    long_warn_html = ""
    if not is_countertrend and p.get("long_warning") and sig_dir == "long":
        long_warn_html = (
            f'<div style="background:#3f1d1d;border-left:3px solid #f87171;'
            f'padding:6px 10px;margin-top:6px;border-radius:4px;color:#fca5a5;'
            f'font-size:11px;">⚠️ {p["long_warning"]}</div>'
        )

    sizing_html = _sizing_badge_html(pp["sizing"])

    # Direction-specific stats for this signal's tf+direction.
    # Countertrend combos don't have by_direction_* breakdowns — they're
    # uni-directional by construction, so just skip this section for them.
    dir_stats_html = ""
    if not is_countertrend:
        by_tf_dir = p[f"by_direction_{sig_tf}" if sig_tf in ("1d","4h") else "by_direction_1d"]
        sig_dir_stats = by_tf_dir.get(sig_dir)
        if sig_dir_stats:
            warn_icon = "⚠️" if sig_dir_stats.get("warn") else "✓"
            mean_color = "#f87171" if sig_dir_stats["mean_r"] < 0 else (
                         "#fbbf24" if sig_dir_stats["mean_r"] < 0.10 else "#34d399")
            dir_stats_html = (
                f'<div style="margin-top:6px;font-size:11px;color:#8892b0;">'
                f'<b>{sig_tf.upper()} {sig_dir}</b> in this combo: '
                f'n={sig_dir_stats["n"]}, mean R '
                f'<span style="color:{mean_color};font-weight:700;">'
                f'{sig_dir_stats["mean_r"]:+.3f}</span>, '
                f'PF {sig_dir_stats["pf"]:.2f} {warn_icon}'
                f'</div>'
            )

    # Build trade plan section. Trend-following uses (tf, direction, entry_zone, tp_R).
    # Countertrend uses (tf, direction, entry_retrace, sl_method, tp_R) — different fields.
    if is_countertrend:
        # The header explains we're FADING the bullish/bearish exhaustion candle
        ct_setup_dir = ("BULL" if pp["direction"] == "short" else "BEAR")
        ct_trade_dir = pp["direction"].upper()
        plan_header = ("⭐ COUNTERTREND TRADE PLAN — fade the exhaustion 🔄")
        retrace_str = (f"at close" if pp["entry_retrace"] == 0.0 else
                       f"wick {abs(pp['entry_retrace'])*100:.0f}% past close")
        plan_body_html = (
            f'<div style="font-size:12px;color:#fbbf24;margin-bottom:6px;'
            f'font-style:italic;">⚠️ Setup is a strong {ct_setup_dir} candle. '
            f'Recommended action: COUNTERTREND {ct_trade_dir} (fade the move).</div>'
            f'{pp["tf"].upper()} <b>{pp["direction"]}</b>'
            f' · entry retrace <b>{pp["entry_retrace"]:+.3f}</b> ({retrace_str})'
            f' · SL <b>{pp["sl_method"]}</b>'
            f' · TP <b>{pp["tp_R"]}R</b><br>'
        )
    else:
        plan_header = f"⭐ RECOMMENDED TRADE PLAN {plan_match_marker}"
        plan_body_html = (
            f'{pp["tf"].upper()} <b>{pp["direction"]}</b>'
            f' · entry <b>{pp["entry_zone"]}</b>'
            f' · TP <b>{pp["tp_R"]}R</b><br>'
        )

    # Recent check
    rc = p["recent_check"]
    recent_color = ("#34d399" if "STRONG" in rc["verdict"].upper()
                    or "STABLE" in rc["verdict"].upper()
                    else "#fbbf24" if "POSITIVE" in rc["verdict"].upper()
                    else "#f87171")
    recent_html = (
        f'<div style="margin-top:8px;padding:6px 10px;background:#0d1f2d;'
        f'border-radius:4px;font-size:11px;color:#8892b0;">'
        f'<b style="color:#58a6ff;">Recent verification:</b><br>'
        f'• {rc["earlier"]}<br>'
        f'• {rc["recent"]}<br>'
        f'<span style="color:{recent_color};font-weight:700;">→ {rc["verdict"]}</span>'
        f'</div>'
    )

    # Overlap section
    overlap_html = ""
    if overlap:
        items = []
        for o in overlap:
            op = o["primary"]
            oo_marker = "✅" if (sig_tf == op["tf"] and sig_dir == op["direction"]) else "↪"
            items.append(
                f'<div style="margin-top:4px;font-size:11px;color:#8892b0;">'
                f'{oo_marker} <b style="color:#a78bfa;">{o["name"]}</b> — '
                f'rollup PF {o["rollup"]["pf"]:.2f}, '
                f'mean R {o["rollup"]["mean_r"]:+.3f} '
                f'<span style="opacity:0.7;">(primary plan: {op["tf"]} {op["direction"]} '
                f'{op["entry_zone"]} TP{op["tp_R"]}R, mean {op["mean_r"]:+.3f})</span>'
                f'</div>'
            )
        overlap_html = (
            f'<div style="margin-top:10px;padding-top:8px;border-top:1px dashed #30363d;">'
            f'<div style="font-size:10px;color:#8892b0;letter-spacing:0.6px;'
            f'margin-bottom:4px;">ALSO MATCHES (lower PF, shown for context):</div>'
            f'{"".join(items)}'
            f'</div>'
        )

    # Audit metadata footer
    audit_meta = (
        f'<div style="margin-top:8px;padding-top:6px;border-top:1px solid #30363d;'
        f'font-size:10px;color:#6e7c95;font-style:italic;">'
        f'Audit: {AUDIT_DATA_START} → {AUDIT_DATA_END} '
        f'({AUDIT_TIMESPAN_YEARS:.1f} yrs · {AUDIT_TOTAL_COINS} coins · '
        f'{AUDIT_TOTAL_FILLED_TRADES:,} filled trades · {AUDIT_VERSION})'
        f'</div>'
    )

    # Color theme by combo type:
    #   trend_following: blue (#58a6ff border, blue badge, "🎯 TIER N TREND")
    #   countertrend:    orange (#fb8500 border, orange badge, "🔄 TIER N COUNTERTREND")
    if is_countertrend:
        border_color  = "#fb8500"
        title_color   = "#fb8500"
        badge_bg      = "#9a3412"
        title_emoji   = "🔄"
        title_text    = f"COUNTERTREND COMBO MATCH — TIER {p['tier']}"
        adx_str       = "(ADX not filtered for countertrend)"
    else:
        border_color  = "#58a6ff"
        title_color   = "#58a6ff"
        badge_bg      = "#1f6feb"
        title_emoji   = "🎯"
        title_text    = f"QUANTFLOW COMBO MATCH — TIER {p['tier']}"
        adx_str       = (f"· ADX {int(p['criteria']['adx_min'])}-"
                         f"{int(p['criteria']['adx_max'])}")

    panel = f"""
    <div style="margin:12px 0;padding:14px 16px;background:#161b22;
         border:2px solid {border_color};border-radius:8px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <span style="font-size:18px;">{title_emoji}</span>
            <span style="color:{title_color};font-weight:800;font-size:14px;
                  letter-spacing:0.5px;">{title_text}</span>
            <span style="background:{badge_bg};color:#fff;padding:2px 8px;
                  border-radius:10px;font-size:11px;font-weight:700;">{p["name"]}</span>
            {sizing_html}
        </div>
        <div style="font-size:12px;color:#ccd6f6;margin-bottom:6px;">
            <b>Criteria:</b> body {p["criteria"]["body_min"]:.2f}-{p["criteria"]["body_max"]:.2f}
            · vol {p["criteria"]["vol_min"]:.1f}-{p["criteria"]["vol_max"]:.1f}×
            {adx_str}
            · regime {"ALIGNED" if p["criteria"]["regime_mode"]=="A" else "no filter"}
        </div>

        <div style="background:#0d1f2d;border-radius:6px;padding:10px 12px;
             margin-top:8px;font-size:12px;color:#ccd6f6;">
            <div style="color:#58a6ff;font-weight:700;font-size:11px;
                 letter-spacing:0.6px;margin-bottom:6px;">📊 ROLLUP BACKTEST (combo as single strategy)</div>
            n = <b>{rollup["n"]:,}</b> trades ·
            WR <b>{rollup["wr"]:.1f}%</b> ·
            mean R <b style="color:{"#34d399" if rollup["mean_r"]>0 else "#f87171"};">{rollup["mean_r"]:+.3f}</b> ·
            Sharpe <b>{rollup["sharpe"]:+.2f}</b> ·
            PF <b style="color:#fbbf24;">{rollup["pf"]:.2f}</b>
        </div>

        <div style="background:#0d1f2d;border-radius:6px;padding:10px 12px;
             margin-top:6px;font-size:12px;color:#ccd6f6;">
            <div style="color:#58a6ff;font-weight:700;font-size:11px;
                 letter-spacing:0.6px;margin-bottom:6px;">{plan_header}</div>
            {plan_body_html}
            <span style="font-size:11px;color:#8892b0;">
            n = {pp["n"]} · WR <b>{pp["wr"]:.1f}%</b> ·
            mean R <b style="color:#34d399;">{pp["mean_r"]:+.3f}</b> ·
            PF <b style="color:#fbbf24;">{pp["pf"]:.2f}</b>
            </span>
            {dir_stats_html}
            {long_warn_html}
        </div>

        {recent_html}
        {overlap_html}
        {audit_meta}
    </div>
    """
    return panel


# ============================================================================
# AI PROMPT INJECTION
# ============================================================================

def build_ai_prompt_block(matches: list[dict], sig: dict) -> str:
    """
    Build a text block describing combo matches + full audit context for
    injection into the AI verdict prompt. Returns empty string if no matches.

    The AI will use this to weight its trade/no-trade decision based on
    historical evidence specific to the matched combinations.
    """
    if not matches:
        return ""

    sig_dir = sig.get("direction", "?")
    sig_tf  = (sig.get("timeframe", "") or "").lower()

    lines = []
    lines.append("=== QUANTFLOW BACKTEST CONTEXT (HISTORICAL AUDIT EVIDENCE) ===")
    lines.append(f"Audit dataset: {AUDIT_TOTAL_COINS} coins · "
                 f"{AUDIT_TOTAL_FILLED_TRADES:,} filled trades · "
                 f"{AUDIT_DATA_START} → {AUDIT_DATA_END} "
                 f"({AUDIT_TIMESPAN_YEARS:.1f} years)")
    lines.append(f"This signal matches {len(matches)} backtest-validated "
                 f"combo(s) — listed by historical PF (highest first):")
    lines.append("")

    for i, c in enumerate(matches, 1):
        cp = c["primary"]
        rollup = c["rollup"]
        crit = c["criteria"]
        c_type = c.get("combo_type", "trend_following")
        is_ct = (c_type == "countertrend")

        prefix = "★ PRIMARY" if i == 1 else f"  ALSO #{i}"
        type_tag = " [COUNTERTREND]" if is_ct else ""
        lines.append(f"{prefix}: {c['name']} (Tier {c['tier']}){type_tag}")
        # Criteria differs (no ADX in countertrend)
        if is_ct:
            lines.append(f"  Criteria: body {crit['body_min']:.2f}-{crit['body_max']:.2f}, "
                         f"vol {crit['vol_min']:.1f}-{crit['vol_max']:.1f}x "
                         f"(ADX not filtered for countertrend)")
        else:
            lines.append(f"  Criteria: body {crit['body_min']:.2f}-{crit['body_max']:.2f}, "
                         f"vol {crit['vol_min']:.1f}-{crit['vol_max']:.1f}x, "
                         f"ADX {int(crit['adx_min'])}-{int(crit['adx_max'])}, "
                         f"regime {'aligned' if crit['regime_mode']=='A' else 'no filter'}")
        lines.append(f"  Rollup: n={rollup['n']:,}, WR={rollup['wr']:.1f}%, "
                     f"mean R={rollup['mean_r']:+.3f}, "
                     f"Sharpe={rollup['sharpe']:+.2f}, PF={rollup['pf']:.2f}")
        # Trade plan format differs
        if is_ct:
            setup_dir = "BULL" if cp["direction"] == "short" else "BEAR"
            lines.append(f"  COUNTERTREND PLAN: scanner shows strong {setup_dir} candle, "
                         f"FADE it. Take {cp['tf'].upper()} {cp['direction'].upper()} "
                         f"with entry retrace {cp['entry_retrace']:+.3f}, "
                         f"SL={cp['sl_method']}, TP={cp['tp_R']}R")
            lines.append(f"  Plan stats: n={cp['n']}, WR={cp['wr']:.1f}%, "
                         f"mean R={cp['mean_r']:+.3f}, PF={cp['pf']:.2f}, sizing={cp['sizing']}")
        else:
            lines.append(f"  Recommended plan: {cp['tf'].upper()} {cp['direction']}, "
                         f"entry={cp['entry_zone']}, TP={cp['tp_R']}R "
                         f"(n={cp['n']}, WR={cp['wr']:.1f}%, mean R={cp['mean_r']:+.3f}, "
                         f"PF={cp['pf']:.2f}, sizing={cp['sizing']})")

        # This signal's specific tf+direction stats (trend-following only)
        if not is_ct and sig_tf in ("1d", "4h"):
            dir_stats = c.get(f"by_direction_{sig_tf}", {}).get(sig_dir)
            if dir_stats:
                warn_str = " ⚠️ FLAGGED WEAK" if dir_stats.get("warn") else ""
                lines.append(f"  This signal's slice ({sig_tf.upper()} {sig_dir}) "
                             f"in this combo: n={dir_stats['n']}, "
                             f"mean R={dir_stats['mean_r']:+.3f}, "
                             f"PF={dir_stats['pf']:.2f}{warn_str}")

        # Long warning (trend-following only)
        if not is_ct and c.get("long_warning") and sig_dir == "long":
            lines.append(f"  ⚠️ {c['long_warning']}")

        # Recent check
        rc = c["recent_check"]
        lines.append(f"  Recent verification: {rc['earlier']} | {rc['recent']} → {rc['verdict']}")
        lines.append("")

    # Plan-vs-signal sanity. Trend-following: should match. Countertrend:
    # by construction, scanner direction is opposite of trade direction.
    primary = matches[0]
    pp = primary["primary"]
    primary_is_ct = (primary.get("combo_type") == "countertrend")
    if primary_is_ct:
        setup_dir_text = "BULL" if pp["direction"] == "short" else "BEAR"
        lines.append(f"🔄 COUNTERTREND SETUP: scanner detected a strong {setup_dir_text} "
                     f"candle ({sig_tf.upper()} {sig_dir}). The historical edge in "
                     f"this body/vol bucket is FADING the move — taking the OPPOSITE "
                     f"trade ({pp['tf'].upper()} {pp['direction']}). "
                     f"⚠️ This is INTENTIONAL — do NOT trade in the scanner direction.")
    elif sig_tf == pp["tf"] and sig_dir == pp["direction"]:
        lines.append("✅ This signal's timeframe and direction MATCH the primary "
                     "combo's recommended trade plan. Strongest backtest evidence applies.")
    else:
        lines.append(f"⚠️  This signal's tf/direction ({sig_tf.upper()} {sig_dir}) "
                     f"DIFFERS from primary combo's recommended plan "
                     f"({pp['tf'].upper()} {pp['direction']}). "
                     f"Use slice-specific stats above instead of the recommended plan.")
    lines.append("")
    lines.append("DECISION GUIDANCE FROM AUDIT:")
    lines.append("- LARGE sizing combos (mean R > 0.30) → take when slice is positive.")
    lines.append("- If this slice mean R is negative or marked WEAK → study only, do NOT trade.")
    lines.append("- 1D LONG signals are weak across most combos — apply extra scrutiny.")
    lines.append("- Combos verified STABLE or STRONGER recently are higher conviction.")
    lines.append("- Combos verified WEAKER recently → reduce sizing or skip.")
    lines.append("- COUNTERTREND combos (CT*): the recommended trade is OPPOSITE the "
                 "scanner direction; this is the whole point — fade exhaustion.")
    lines.append("=== END QUANTFLOW BACKTEST CONTEXT ===")
    return "\n".join(lines)
