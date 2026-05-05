# ============================================================================
# quantflow_combos.py — Backtest-validated combo definitions for QuantFlow
# ============================================================================
# Contains:
#   • 17 individual audit-validated combo dicts (COMBOS / COMBOS_BY_NAME)
#     — used as reference data and for the "similar to" annotation. These
#       are NOT removed. The scanner no longer filters directly on them
#       (Phase 4 unified-tier model), but they are required for:
#         - find_similar_combo() annotation on scanner cards
#         - _qf_get_matching_combos() fallback (custom combo builder)
#   • UNIFIED_TIERS (Phase 4, May 2026) — 3 wider-band tier filters that
#     consolidate the 17 combos and produce more daily setups.
# ============================================================================

from typing import Optional

# ── Audit window metadata ────────────────────────────────────────────────────
AUDIT_DATA_START            = "2020-01-01"
AUDIT_DATA_END              = "2024-06-30"
AUDIT_TIMESPAN_YEARS        = 4.5
AUDIT_TOTAL_COINS           = 134
AUDIT_TOTAL_FILLED_TRADES   = 107_682
AUDIT_VERSION               = "v3f"

# ── Individual combo definitions (17 combos) ─────────────────────────────────
# These stay in this file permanently. They serve as reference data for:
#   1. The "similar to" annotation on scanner cards (find_similar_combo).
#   2. The custom combo builder flow in app.py.
# The Phase 4 unified-tier scanner no longer iterates this list for primary
# filtering — UNIFIED_TIERS is used instead. But COMBOS and COMBOS_BY_NAME
# must remain populated and correct.

COMBOS = [
    # ── Tier 1: Top-conviction trend-following (PF ≥ 1.30) ──────────────────
    {
        "name":        "C6A-N",
        "tier":        1,
        "label_short": "Strong bull/bear 4H, no regime filter",
        "combo_type":  "trend_following",
        "criteria": {
            "body_min":    0.70, "body_max":   0.80,
            "vol_min":     1.50, "vol_max":    2.00,
            "adx_min":     30.0, "adx_max":    50.0,
            "regime_mode": "N",
            "directions":  ["long", "short"],
        },
        "tf_eligible": ["4h", "1d"],
        "rollup": {"n": 8_124, "wr": 0.565, "mean_r": 0.148, "sharpe": 1.21, "pf": 1.42},
        "primary": {
            "tf": "4h", "direction": "long", "entry_zone": "0%",
            "tp_R": 2.0, "sizing": "FULL",
            "n": 4_892, "wr": 0.571, "mean_r": 0.162, "pf": 1.45,
        },
        "recent_check": {"verdict": "STABLE"},
    },
    {
        "name":        "C6A-A",
        "tier":        2,
        "label_short": "Strong bull/bear 4H, BTC-aligned",
        "combo_type":  "trend_following",
        "criteria": {
            "body_min":    0.70, "body_max":   0.80,
            "vol_min":     1.50, "vol_max":    2.00,
            "adx_min":     30.0, "adx_max":    50.0,
            "regime_mode": "A",
            "directions":  ["long", "short"],
        },
        "tf_eligible": ["4h", "1d"],
        "rollup": {"n": 5_488, "wr": 0.582, "mean_r": 0.171, "sharpe": 1.34, "pf": 1.52},
        "primary": {
            "tf": "4h", "direction": "long", "entry_zone": "0%",
            "tp_R": 2.0, "sizing": "FULL",
            "n": 3_201, "wr": 0.590, "mean_r": 0.183, "pf": 1.56,
        },
        "recent_check": {"verdict": "STABLE"},
    },
    {
        "name":        "C5B-A",
        "tier":        3,
        "label_short": "Vol-elevated 4H trend, BTC-aligned",
        "combo_type":  "trend_following",
        "criteria": {
            "body_min":    0.72, "body_max":   0.80,
            "vol_min":     2.00, "vol_max":    2.50,
            "adx_min":     30.0, "adx_max":    50.0,
            "regime_mode": "A",
            "directions":  ["long", "short"],
        },
        "tf_eligible": ["4h", "1d"],
        "rollup": {"n": 3_876, "wr": 0.574, "mean_r": 0.155, "sharpe": 1.18, "pf": 1.38},
        "primary": {
            "tf": "4h", "direction": "long", "entry_zone": "0%",
            "tp_R": 2.0, "sizing": "FULL",
            "n": 2_103, "wr": 0.581, "mean_r": 0.164, "pf": 1.41,
        },
        "recent_check": {"verdict": "STABLE"},
    },
    {
        "name":        "C5B-N",
        "tier":        4,
        "label_short": "Vol-elevated 4H trend, no regime filter",
        "combo_type":  "trend_following",
        "criteria": {
            "body_min":    0.72, "body_max":   0.80,
            "vol_min":     2.00, "vol_max":    2.50,
            "adx_min":     30.0, "adx_max":    50.0,
            "regime_mode": "N",
            "directions":  ["long", "short"],
        },
        "tf_eligible": ["4h", "1d"],
        "rollup": {"n": 5_612, "wr": 0.558, "mean_r": 0.138, "sharpe": 1.09, "pf": 1.32},
        "primary": {
            "tf": "4h", "direction": "long", "entry_zone": "0%",
            "tp_R": 2.0, "sizing": "FULL",
            "n": 3_044, "wr": 0.563, "mean_r": 0.145, "pf": 1.34,
        },
        "recent_check": {"verdict": "STABLE"},
    },
    {
        "name":        "C1A-A",
        "tier":        5,
        "label_short": "1D trend, BTC-aligned",
        "combo_type":  "trend_following",
        "criteria": {
            "body_min":    0.70, "body_max":   0.80,
            "vol_min":     1.50, "vol_max":    2.50,
            "adx_min":     30.0, "adx_max":    50.0,
            "regime_mode": "A",
            "directions":  ["long", "short"],
        },
        "tf_eligible": ["1d"],
        "rollup": {"n": 2_941, "wr": 0.561, "mean_r": 0.143, "sharpe": 1.12, "pf": 1.34},
        "primary": {
            "tf": "1d", "direction": "long", "entry_zone": "0%",
            "tp_R": 2.0, "sizing": "FULL",
            "n": 1_587, "wr": 0.568, "mean_r": 0.151, "pf": 1.37,
        },
        "recent_check": {"verdict": "STABLE"},
    },
    # ── Tier 2: Mid-conviction trend-following (PF 1.14-1.23) ────────────────
    {
        "name":        "C2A-A",
        "tier":        6,
        "label_short": "Mid-body 4H trend, BTC-aligned",
        "combo_type":  "trend_following",
        "criteria": {
            "body_min":    0.50, "body_max":   0.60,
            "vol_min":     2.00, "vol_max":    2.50,
            "adx_min":     30.0, "adx_max":    50.0,
            "regime_mode": "A",
            "directions":  ["long", "short"],
        },
        "tf_eligible": ["1h", "4h", "1d"],
        "rollup": {"n": 6_834, "wr": 0.542, "mean_r": 0.112, "sharpe": 0.91, "pf": 1.23},
        "primary": {
            "tf": "4h", "direction": "long", "entry_zone": "0%",
            "tp_R": 2.0, "sizing": "HALF",
            "n": 3_712, "wr": 0.549, "mean_r": 0.120, "pf": 1.26,
        },
        "recent_check": {"verdict": "WEAKER"},
    },
    {
        "name":        "C2B-A",
        "tier":        7,
        "label_short": "Mid-body 1H trend, BTC-aligned",
        "combo_type":  "trend_following",
        "criteria": {
            "body_min":    0.50, "body_max":   0.60,
            "vol_min":     2.00, "vol_max":    2.50,
            "adx_min":     30.0, "adx_max":    50.0,
            "regime_mode": "A",
            "directions":  ["long", "short"],
        },
        "tf_eligible": ["1h", "4h"],
        "rollup": {"n": 7_219, "wr": 0.538, "mean_r": 0.108, "sharpe": 0.88, "pf": 1.20},
        "primary": {
            "tf": "4h", "direction": "long", "entry_zone": "0%",
            "tp_R": 2.0, "sizing": "HALF",
            "n": 3_891, "wr": 0.541, "mean_r": 0.113, "pf": 1.21,
        },
        "recent_check": {"verdict": "WEAKER"},
    },
    {
        "name":        "C2B-N",
        "tier":        8,
        "label_short": "Mid-body 4H trend, no regime filter",
        "combo_type":  "trend_following",
        "criteria": {
            "body_min":    0.50, "body_max":   0.60,
            "vol_min":     2.00, "vol_max":    2.50,
            "adx_min":     30.0, "adx_max":    50.0,
            "regime_mode": "N",
            "directions":  ["long", "short"],
        },
        "tf_eligible": ["1h", "4h"],
        "rollup": {"n": 9_104, "wr": 0.531, "mean_r": 0.098, "sharpe": 0.81, "pf": 1.18},
        "primary": {
            "tf": "4h", "direction": "long", "entry_zone": "0%",
            "tp_R": 2.0, "sizing": "HALF",
            "n": 4_892, "wr": 0.535, "mean_r": 0.103, "pf": 1.19,
        },
        "recent_check": {"verdict": "WEAKER"},
    },
    {
        "name":        "C1A-N",
        "tier":        9,
        "label_short": "1H/4H mid-body trend, no regime filter",
        "combo_type":  "trend_following",
        "criteria": {
            "body_min":    0.50, "body_max":   0.60,
            "vol_min":     2.00, "vol_max":    2.50,
            "adx_min":     30.0, "adx_max":    50.0,
            "regime_mode": "N",
            "directions":  ["long", "short"],
        },
        "tf_eligible": ["1h", "4h", "1d"],
        "rollup": {"n": 10_412, "wr": 0.535, "mean_r": 0.104, "sharpe": 0.86, "pf": 1.21},
        "primary": {
            "tf": "4h", "direction": "long", "entry_zone": "0%",
            "tp_R": 2.0, "sizing": "HALF",
            "n": 5_644, "wr": 0.541, "mean_r": 0.112, "pf": 1.23,
        },
        "recent_check": {"verdict": "STABLE"},
    },
    {
        "name":        "C2A-N",
        "tier":        10,
        "label_short": "Mid-body all-TF trend, no regime filter",
        "combo_type":  "trend_following",
        "criteria": {
            "body_min":    0.50, "body_max":   0.60,
            "vol_min":     2.00, "vol_max":    2.50,
            "adx_min":     30.0, "adx_max":    50.0,
            "regime_mode": "N",
            "directions":  ["long", "short"],
        },
        "tf_eligible": ["1h", "4h", "1d"],
        "rollup": {"n": 11_038, "wr": 0.528, "mean_r": 0.093, "sharpe": 0.77, "pf": 1.14},
        "primary": {
            "tf": "4h", "direction": "long", "entry_zone": "0%",
            "tp_R": 2.0, "sizing": "HALF",
            "n": 5_912, "wr": 0.532, "mean_r": 0.099, "pf": 1.15,
        },
        "recent_check": {"verdict": "WEAKER"},
    },
    # ── Tier 3: Countertrend / fade (7 combos, v3f audit) ────────────────────
    # signal_direction_required = "short" → detected a bear candle → trade LONG
    # signal_direction_required = "long"  → detected a bull candle → trade SHORT
    {
        "name":        "CT1",
        "tier":        11,
        "label_short": "CT: strong bear 4H exhaustion (fade long)",
        "combo_type":  "countertrend",
        "criteria": {
            "body_min":                0.80, "body_max":   1.01,
            "vol_min":                 4.00, "vol_max":    7.00,
            "adx_min":                 0.0,  "adx_max":    999.0,
            "regime_mode":             "N",
            "signal_direction_required": "short",
        },
        "tf_eligible": ["4h"],
        "rollup": {"n": 1_842, "wr": 0.561, "mean_r": 0.139, "sharpe": 1.08, "pf": 1.38},
        "primary": {
            "tf": "4h", "direction": "long",
            "entry_retrace": -0.10, "sl_method": "wick_anchor", "tp_R": 2.0,
            "sizing": "HALF",
            "n": 1_842, "wr": 0.561, "mean_r": 0.139, "pf": 1.38,
        },
        "recent_check": {"verdict": "MUCH STRONGER"},
    },
    {
        "name":        "CT2",
        "tier":        12,
        "label_short": "CT: very strong bear 4H (fade long)",
        "combo_type":  "countertrend",
        "criteria": {
            "body_min":                0.85, "body_max":   1.01,
            "vol_min":                 5.00, "vol_max":    10.00,
            "adx_min":                 0.0,  "adx_max":    999.0,
            "regime_mode":             "N",
            "signal_direction_required": "short",
        },
        "tf_eligible": ["4h"],
        "rollup": {"n": 1_104, "wr": 0.572, "mean_r": 0.151, "sharpe": 1.19, "pf": 1.45},
        "primary": {
            "tf": "4h", "direction": "long",
            "entry_retrace": -0.10, "sl_method": "wick_anchor", "tp_R": 2.0,
            "sizing": "HALF",
            "n": 1_104, "wr": 0.572, "mean_r": 0.151, "pf": 1.45,
        },
        "recent_check": {"verdict": "MUCH STRONGER"},
    },
    {
        "name":        "CT3",
        "tier":        13,
        "label_short": "CT: bear 4H moderate vol (fade long)",
        "combo_type":  "countertrend",
        "criteria": {
            "body_min":                0.80, "body_max":   1.01,
            "vol_min":                 6.00, "vol_max":    12.00,
            "adx_min":                 0.0,  "adx_max":    999.0,
            "regime_mode":             "N",
            "signal_direction_required": "short",
        },
        "tf_eligible": ["4h"],
        "rollup": {"n": 892, "wr": 0.558, "mean_r": 0.132, "sharpe": 1.02, "pf": 1.32},
        "primary": {
            "tf": "4h", "direction": "long",
            "entry_retrace": -0.10, "sl_method": "wick_anchor", "tp_R": 2.0,
            "sizing": "HALF",
            "n": 892, "wr": 0.558, "mean_r": 0.132, "pf": 1.32,
        },
        "recent_check": {"verdict": "STRONGER"},
    },
    {
        "name":        "CT4",
        "tier":        14,
        "label_short": "CT: extreme bear 4H (fade long)",
        "combo_type":  "countertrend",
        "criteria": {
            "body_min":                0.90, "body_max":   1.01,
            "vol_min":                 4.00, "vol_max":    999.0,
            "adx_min":                 0.0,  "adx_max":    999.0,
            "regime_mode":             "N",
            "signal_direction_required": "short",
        },
        "tf_eligible": ["4h"],
        "rollup": {"n": 778, "wr": 0.555, "mean_r": 0.128, "sharpe": 0.98, "pf": 1.29},
        "primary": {
            "tf": "4h", "direction": "long",
            "entry_retrace": -0.10, "sl_method": "wick_anchor", "tp_R": 2.0,
            "sizing": "HALF",
            "n": 778, "wr": 0.555, "mean_r": 0.128, "pf": 1.29,
        },
        "recent_check": {"verdict": "STRONGER"},
    },
    {
        "name":        "CT5",
        "tier":        15,
        "label_short": "CT: strong bull 4H exhaustion (fade short)",
        "combo_type":  "countertrend",
        "criteria": {
            "body_min":                0.80, "body_max":   1.01,
            "vol_min":                 4.00, "vol_max":    7.00,
            "adx_min":                 0.0,  "adx_max":    999.0,
            "regime_mode":             "N",
            "signal_direction_required": "long",
        },
        "tf_eligible": ["4h"],
        "rollup": {"n": 1_621, "wr": 0.557, "mean_r": 0.134, "sharpe": 1.04, "pf": 1.33},
        "primary": {
            "tf": "4h", "direction": "short",
            "entry_retrace": -0.10, "sl_method": "wick_anchor", "tp_R": 2.0,
            "sizing": "HALF",
            "n": 1_621, "wr": 0.557, "mean_r": 0.134, "pf": 1.33,
        },
        "recent_check": {"verdict": "STRONGER"},
    },
    {
        "name":        "CT6",
        "tier":        16,
        "label_short": "CT: very strong bull 4H (fade short)",
        "combo_type":  "countertrend",
        "criteria": {
            "body_min":                0.85, "body_max":   1.01,
            "vol_min":                 5.00, "vol_max":    10.00,
            "adx_min":                 0.0,  "adx_max":    999.0,
            "regime_mode":             "N",
            "signal_direction_required": "long",
        },
        "tf_eligible": ["4h"],
        "rollup": {"n": 987, "wr": 0.564, "mean_r": 0.144, "sharpe": 1.12, "pf": 1.39},
        "primary": {
            "tf": "4h", "direction": "short",
            "entry_retrace": -0.10, "sl_method": "wick_anchor", "tp_R": 2.0,
            "sizing": "HALF",
            "n": 987, "wr": 0.564, "mean_r": 0.144, "pf": 1.39,
        },
        "recent_check": {"verdict": "MUCH STRONGER"},
    },
    {
        "name":        "CT7",
        "tier":        17,
        "label_short": "CT: extreme bull 4H (fade short)",
        "combo_type":  "countertrend",
        "criteria": {
            "body_min":                0.90, "body_max":   1.01,
            "vol_min":                 4.00, "vol_max":    999.0,
            "adx_min":                 0.0,  "adx_max":    999.0,
            "regime_mode":             "N",
            "signal_direction_required": "long",
        },
        "tf_eligible": ["4h"],
        "rollup": {"n": 691, "wr": 0.551, "mean_r": 0.124, "sharpe": 0.96, "pf": 1.28},
        "primary": {
            "tf": "4h", "direction": "short",
            "entry_retrace": -0.10, "sl_method": "wick_anchor", "tp_R": 2.0,
            "sizing": "HALF",
            "n": 691, "wr": 0.551, "mean_r": 0.124, "pf": 1.28,
        },
        "recent_check": {"verdict": "STRONGER"},
    },
]

COMBOS_BY_NAME: dict = {c["name"]: c for c in COMBOS}


def render_combo_panel_html(matches: list, sig: dict) -> str:
    """
    Render an HTML panel summarising the combo(s) that matched this signal.
    Returns an HTML string suitable for st.markdown(unsafe_allow_html=True).
    """
    if not matches:
        return ""
    lines = []
    for m in matches:
        name   = m.get("name", "?")
        tier   = m.get("tier", "?")
        lvl    = m.get("_matched_level", "STRICT")
        sf     = m.get("_size_factor",  1.0)
        pf_hc  = m.get("_pf_haircut",  1.0)
        ro     = m.get("rollup", {})
        pp     = m.get("primary", {})
        pf_raw = ro.get("pf", 0.0)
        pf_adj = pf_raw * pf_hc
        is_ct  = m.get("combo_type") == "countertrend"
        if is_ct:
            plan_str = (
                f"FADE → {pp.get('tf','?').upper()} {pp.get('direction','?')}, "
                f"retrace {pp.get('entry_retrace', 0):+.2f}, "
                f"{pp.get('sl_method','?')}, TP{pp.get('tp_R', 2.0)}R"
            )
        else:
            plan_str = (
                f"{pp.get('tf','?').upper()} {pp.get('direction','?')}, "
                f"entry {pp.get('entry_zone','0%')}, TP{pp.get('tp_R', 2.0)}R"
            )
        lvl_color = {"STRICT": "#3fb950", "RELAXED": "#e3b341", "LOOSE": "#f85149"}.get(lvl, "#8892b0")
        size_str = f"{sf*100:.0f}% sizing" if sf < 1.0 else "Full sizing"
        lines.append(
            f'<div style="border:1px solid #30363d;border-radius:6px;padding:8px 12px;'
            f'margin-top:6px;background:#161b22;">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
            f'<span style="background:#1f3d2e;color:#3fb950;font-weight:700;'
            f'padding:2px 6px;border-radius:4px;font-size:11px;">Tier {tier}</span>'
            f'<span style="font-weight:700;color:#ccd6f6;">{name}</span>'
            f'<span style="background:{lvl_color}22;color:{lvl_color};'
            f'padding:2px 6px;border-radius:4px;font-size:10px;">{lvl} · {size_str}</span>'
            f'</div>'
            f'<div style="font-size:11px;color:#8892b0;">'
            f'Rollup PF: <b style="color:#ccd6f6;">{pf_raw:.2f}</b>'
            f'{(" → adj " + f"{pf_adj:.2f}") if lvl != "STRICT" else ""}'
            f' · WR: {ro.get("wr", 0)*100:.1f}%'
            f' · Mean R: {ro.get("mean_r", 0):+.3f}'
            f' · n={ro.get("n", 0):,}'
            f'<br>Plan: <b style="color:#58a6ff;">{plan_str}</b>'
            f'</div>'
            f'</div>'
        )
    return "\n".join(lines)


# ============================================================================
# UNIFIED TIER DEFINITIONS — added Phase 4 (May 2026)
# ============================================================================
# These three filters consolidate the 17 individual combos into wider bands
# that are easier to reason about and produce more daily setups. Audit PF
# values come from the unified-tier audit run (see audit_results_*.json).
#
# The 17 individual COMBOS above remain in this file as REFERENCE — the
# scanner uses them only to annotate which specific combo a unified-tier
# signal is "similar to" (the inner combo whose strict bands the signal
# falls inside).
#
# IMPORTANT: hard caps from the level system still apply. Body 0.60-0.70
# trend dead zone, ADX > 50 cap, CT body 0.78 floor are all enforced
# regardless of which tier the user ticks.
# ============================================================================

UNIFIED_TIERS = {
    "TIER_1": {
        "name":           "TIER 1",
        "label":          "TREND-FOLLOWING (TOP CONVICTION)",
        "combo_type":     "trend_following",
        "criteria": {
            "body_min":   0.70, "body_max":  0.80,
            "vol_min":    1.50, "vol_max":   2.50,
            "adx_min":    30.0, "adx_max":   50.0,
            "regime_mode": "N",                       # no regime filter at unified level
            "directions": ["long", "short"],
        },
        "tf_eligible":     ["1h", "4h", "1d"],
        # PF / WR / mean R / n from the unified-tier audit run
        # USER SUPPLIES THESE — placeholder values below
        "rollup": {
            "n": 0, "wr": 0.0, "mean_r": 0.0, "sharpe": 0.0, "pf": 0.0,
        },
        # The 17-combo names whose criteria fall inside this tier's range
        # — used for the "similar to" annotation in scanner cards.
        "constituent_combos": ["C6A-N", "C6A-A", "C5B-A", "C5B-N", "C1A-A"],
        # Default trade plan when a unified-tier match has no inner combo overlap
        "primary": {
            "tf":         "4h",
            "direction":  "long",                     # placeholder, set per-signal
            "entry_zone": "0%",
            "tp_R":       2.0,
            "sizing":     "FULL",
            "n": 0, "wr": 0.0, "mean_r": 0.0, "pf": 0.0,
        },
    },
    "TIER_2": {
        "name":           "TIER 2",
        "label":          "TREND-FOLLOWING (MID CONVICTION)",
        "combo_type":     "trend_following",
        "criteria": {
            "body_min":   0.50, "body_max":  0.60,
            "vol_min":    2.00, "vol_max":   2.50,
            "adx_min":    30.0, "adx_max":   50.0,
            "regime_mode": "N",
            "directions": ["long", "short"],
        },
        "tf_eligible":     ["1h", "4h", "1d"],
        "rollup": {
            "n": 0, "wr": 0.0, "mean_r": 0.0, "sharpe": 0.0, "pf": 0.0,
        },
        "constituent_combos": ["C2A-A", "C2B-A", "C2B-N", "C1A-N", "C2A-N"],
        "primary": {
            "tf":         "4h",
            "direction":  "long",
            "entry_zone": "0%",
            "tp_R":       2.0,
            "sizing":     "HALF",
            "n": 0, "wr": 0.0, "mean_r": 0.0, "pf": 0.0,
        },
    },
    "TIER_3": {
        "name":           "TIER 3",
        "label":          "COUNTERTREND / FADE",
        "combo_type":     "countertrend",
        "criteria": {
            "body_min":   0.80, "body_max":  1.01,
            "vol_min":    4.00, "vol_max":   999.0,
            "adx_min":    0.0,  "adx_max":   999.0,    # no ADX filter
            "regime_mode": "N",
            # For CT, scanner direction is the candle direction; trade is opposite.
            "directions": ["long", "short"],
            "signal_direction_required": None,        # both candle dirs eligible
            "trade_direction":           None,
        },
        "tf_eligible":     ["4h"],                    # primary TF for fade setups
        "rollup": {
            "n": 0, "wr": 0.0, "mean_r": 0.0, "sharpe": 0.0, "pf": 0.0,
        },
        "constituent_combos": ["CT1", "CT2", "CT3", "CT4", "CT5", "CT6", "CT7"],
        "primary": {
            "tf":            "4h",
            "direction":     "short",                  # opposite of candle, set per-signal
            "entry_retrace": -0.10,
            "sl_method":     "wick_anchor",
            "tp_R":          2.0,
            "sizing":        "HALF",
            "n": 0, "wr": 0.0, "mean_r": 0.0, "pf": 0.0,
        },
    },
}


def get_unified_tier_for_signal(sig: dict) -> Optional[dict]:
    """
    Return the unified TIER dict whose criteria match this signal, or None.
    Tries TIER_1 first, then TIER_2, then TIER_3.

    body_pct in `sig` may be in fraction (0-1) or percent (0-100) — auto-normalize.
    """
    body = abs(float(sig.get("body_pct", 0)))
    if body > 1.5:
        body = body / 100.0
    vol = float(sig.get("vol_mult", 0))
    adx = float(sig.get("adx", 0))

    for tier_key, tier in UNIFIED_TIERS.items():
        crit = tier["criteria"]
        if not (crit["body_min"] <= body < crit["body_max"]):  continue
        if not (crit["vol_min"]  <= vol  < crit["vol_max"]):   continue
        if not (crit["adx_min"]  <= adx  < crit["adx_max"]):   continue
        return tier
    return None


def find_similar_combo(sig: dict, tier: dict) -> Optional[str]:
    """
    Given a signal that matched a unified tier, return the name of the most-
    similar individual combo from `tier["constituent_combos"]` (whose strict
    criteria the signal falls inside). Returns None if no constituent matches.

    Used for the "Similar to: C6A-A" annotation in scanner cards.
    """
    body = abs(float(sig.get("body_pct", 0)))
    if body > 1.5:
        body = body / 100.0
    vol = float(sig.get("vol_mult", 0))
    adx = float(sig.get("adx", 0))
    tf  = (sig.get("timeframe") or "").lower()
    direction = sig.get("direction", "")

    for combo_name in tier["constituent_combos"]:
        c = COMBOS_BY_NAME.get(combo_name)
        if c is None:
            continue
        if tf not in c["tf_eligible"]:
            continue
        crit = c["criteria"]
        if not (crit["body_min"] <= body < crit["body_max"]):  continue
        if not (crit["vol_min"]  <= vol  < crit["vol_max"]):   continue
        if not (crit["adx_min"]  <= adx  < crit["adx_max"]):   continue
        # Direction check (trend uses directions list; CT uses signal_direction_required)
        if c.get("combo_type") == "countertrend":
            if direction != crit.get("signal_direction_required", ""):
                continue
        else:
            if direction not in crit["directions"]:
                continue
        return combo_name
    return None
