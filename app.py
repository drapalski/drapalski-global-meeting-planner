import streamlit as st
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo, available_timezones
import pandas as pd
import plotly.graph_objects as go
import uuid
import json
import importlib.resources as resources
import math

from pathlib import Path

from meeting_scoring import (
    aggregate_meeting_score,
    score_local_detailed,
    scoring_methodology_summary,
)

APP_DIR = Path(__file__).parent
LOGO_PATH = APP_DIR / "assets" / "drapalski_logo.png"

st.set_page_config(
    page_title="Global Meeting Planner | Drapalski Consulting",
    page_icon="🌐",
    layout="wide",
)

# ---------- Drapalski Consulting branding ----------

st.markdown(
    """
    <style>
        :root {
            --dc-charcoal: #111111;
            --dc-slate: #5f5f64;
            --dc-light: #fff8fc;
            --dc-border: #e7dce4;
            --dc-pink: #cd549e;
            --dc-hot-pink: #ff66c4;
            --dc-green: #4f9b63;
            --dc-orange: #e59a45;
        }

        html, body, [class*="css"] {
            font-family: Aptos, "Segoe UI", Arial, sans-serif;
        }

        .stApp {
            background: #fffdfd;
        }

        .block-container {
            max-width: none !important;
            width: 100% !important;
            padding-top: 1.15rem !important;
            padding-bottom: 0.65rem !important;
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
        }

        /* Keep the full-screen Streamlit app from stretching too wide.
           Embedded/narrower views remain fluid. */
        @media (min-width: 1450px) {
            .block-container {
                max-width: 1500px !important;
                margin-left: auto !important;
                margin-right: auto !important;
                padding-left: 1.10rem !important;
                padding-right: 1.10rem !important;
            }
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0.50rem;
        }

        div[data-testid="stHorizontalBlock"] {
            gap: 0.38rem;
        }

        .stMarkdown p {
            margin-bottom: 0.20rem;
        }

        .dc-brand {
            border-bottom: 1px solid var(--dc-border);
            padding: 0.05rem 0 0.60rem 0;
            margin-bottom: 0.45rem;
        }

        .dc-title {
            font-size: clamp(1.70rem, 2.6vw, 2.35rem);
            line-height: 1.02;
            font-weight: 750;
            color: var(--dc-charcoal);
            margin: 0;
        }

        .dc-subtitle {
            margin-top: 0.30rem;
            color: var(--dc-slate);
            font-size: 0.90rem;
            max-width: 1050px;
            line-height: 1.40;
        }

        h1, h2, h3, h4 {
            color: var(--dc-charcoal) !important;
        }

        h2, h3 {
            font-family: Georgia, "Times New Roman", serif;
            letter-spacing: -0.01em;
        }

        h2 {
            margin-top: 0.25rem !important;
            margin-bottom: 0.15rem !important;
        }

        h3, h4 {
            margin-top: 0.20rem !important;
            margin-bottom: 0.10rem !important;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 7px;
            border: 1px solid #2e3034;
            font-weight: 600;
            box-shadow: none;
            min-height: 2.15rem;
        }

        .stButton > button[kind="primary"] {
            background: var(--dc-pink);
            border-color: var(--dc-pink);
            color: white;
        }

        .stButton > button[kind="primary"]:hover {
            background: var(--dc-hot-pink);
            border-color: var(--dc-hot-pink);
            color: #202226;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: var(--dc-pink);
            color: var(--dc-charcoal);
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            border-radius: 7px !important;
            border-color: var(--dc-border) !important;
            min-height: 2.20rem !important;
        }

        /* Keep participant controls readable in embedded / narrower layouts. */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTimeInput"] input,
        div[data-testid="stSelectbox"] input {
            font-size: 0.86rem !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding-left: 0.10rem !important;
            padding-right: 0.10rem !important;
        }

        @media (max-width: 980px) {
            .block-container {
                padding-left: 0.30rem !important;
                padding-right: 0.30rem !important;
            }

            section[data-testid="stSidebar"],
            section[data-testid="stSidebar"] > div {
                width: 220px !important;
                min-width: 220px !important;
            }

            .dc-subtitle {
                font-size: 0.84rem;
            }
        }

        div[data-testid="stMetric"] {
            background: var(--dc-light);
            border: 1px solid var(--dc-border);
            border-radius: 8px;
            padding: 0.35rem 0.60rem;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #fffafd 0%, #f8f2f6 100%);
            border-right: 1px solid var(--dc-border);
            width: 238px !important;
            min-width: 238px !important;
        }

        section[data-testid="stSidebar"] > div {
            width: 238px !important;
            min-width: 238px !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
            padding-top: 0.45rem !important;
        }

        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stCaptionContainer {
            font-size: 0.78rem !important;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--dc-border);
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 10px !important;
            border-color: var(--dc-border) !important;
            background: #ffffff;
        }

        /* Slightly tighter card interiors, especially in the participant editor. */
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding-top: 0.26rem !important;
            padding-bottom: 0.26rem !important;
            padding-left: 0.36rem !important;
            padding-right: 0.36rem !important;
        }

        div[data-testid="stTimeInput"] {
            max-width: 7.2rem !important;
        }

        .joining-help {
            font-size: 0.70rem;
            line-height: 1.35;
            color: #74777c;
            padding: 0.42rem 0.70rem 0.34rem 0.70rem;
            margin: 0.05rem 0 0.12rem 0;
        }

        section[data-testid="stSidebar"] hr {
            border-color: #eadde6;
        }

        .dc-brand {
            position: relative;
        }

        .dc-brand::after {
            content: "";
            display: block;
            width: 74px;
            height: 3px;
            background: linear-gradient(90deg, var(--dc-pink), var(--dc-hot-pink));
            margin-top: 0.65rem;
            border-radius: 2px;
        }

        [data-testid="stDecoration"] {
            display: none;
        }

        .dc-footer {
            margin-top: 0.65rem;
            padding-top: 0.55rem;
            border-top: 1px solid var(--dc-border);
            color: var(--dc-slate);
            font-size: 0.72rem;
            line-height: 1.40;
        }

        .dc-footer strong {
            color: var(--dc-charcoal);
            letter-spacing: 0.08em;
        }

        .participant-header {
            background:#34363a;
            color:#f7f7f7;
            border-radius:6px;
            padding:0.40rem 0.45rem;
            font-size:0.82rem;
            font-weight:700;
            text-align:center;
            line-height:1.15;
            margin-bottom:0.70rem;
            white-space:nowrap;
        }

        @media (max-width: 768px) {
            .participant-header {
                margin-bottom:0.45rem !important;
                padding-top:0.52rem !important;
                padding-bottom:0.52rem !important;
            }
        }

        .participant-meta {
            color:#74777c;
            font-size:0.70rem;
            line-height:1.42;
            padding-top:0.05rem;
            padding-bottom:0.14rem;
        }

        .participant-meta strong {
            color:#55585d;
            font-weight:600;
        }

        /* Participant remove buttons: tiny corner X */
        div[class*="st-key-remove_"] {
            display:flex !important;
            justify-content:flex-end !important;
            align-items:flex-start !important;
        }

        div[class*="st-key-remove_"] button {
            background:#ff66c4 !important;
            border:1px solid #ff66c4 !important;
            color:#111111 !important;
            font-size:8px !important;
            font-weight:700 !important;
            width:16px !important;
            min-width:16px !important;
            max-width:16px !important;
            min-height:16px !important;
            height:16px !important;
            padding:0 !important;
            margin:0 !important;
            border-radius:4px !important;
            line-height:1 !important;
            box-shadow:none !important;
        }

        div[class*="st-key-remove_"] button:hover {
            background:#8f949a !important;
            border-color:#8f949a !important;
            color:#ffffff !important;
        }

        section[data-testid="stSidebar"] [data-testid="stExpander"] {
            margin-top:0.55rem !important;
            margin-bottom:0.70rem !important;
        }

        /* Compact horizontal search-horizon radio buttons. */
        section[data-testid="stSidebar"] div[role="radiogroup"] {
            display:flex !important;
            flex-direction:row !important;
            align-items:flex-start !important;
            justify-content:flex-start !important;
            gap:0.45rem !important;
            flex-wrap:nowrap !important;
            margin-top:0.10rem !important;
            margin-bottom:0.10rem !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            margin:0 !important;
            padding:0 !important;
            align-items:flex-start !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] p {
            font-size:0.72rem !important;
            line-height:1.05 !important;
            white-space:nowrap !important;
        }

        /* Compact saved-setup controls in the sidebar. */
        section[data-testid="stSidebar"] div[class*="st-key-load_preset_button"] button,
        section[data-testid="stSidebar"] div[class*="st-key-download_preset_button"] button,
        section[data-testid="stSidebar"] div[class*="st-key-preset_upload"] button,
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
            font-size:8px !important;
            line-height:1 !important;
            min-height:1.45rem !important;
            height:1.45rem !important;
            width:auto !important;
            min-width:0 !important;
            padding:0.08rem 0.30rem !important;
            border-radius:5px !important;
        }

        section[data-testid="stSidebar"] div[class*="st-key-load_preset_button"],
        section[data-testid="stSidebar"] div[class*="st-key-download_preset_button"] {
            margin-top:0 !important;
            margin-bottom:0.08rem !important;
            padding-top:0 !important;
            align-self:flex-start !important;
        }

        section[data-testid="stSidebar"] div[class*="st-key-load_preset_button"] > div,
        section[data-testid="stSidebar"] div[class*="st-key-download_preset_button"] > div {
            display:flex !important;
            align-items:flex-start !important;
            margin-top:0 !important;
            padding-top:0 !important;
        }

        a {
            color: var(--dc-pink) !important;
        }
    </style>

    <div class="dc-brand">
        <div class="dc-title">Global Meeting Planner</div>
        <div class="dc-subtitle">
            Plan international meetings across time zones, working hours, and daylight-saving changes.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Helpers ----------

FAVORITE_ZONES = [
    "UTC",
    "Europe/Berlin",
    "America/Los_Angeles",
    "Asia/Taipei",
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "Europe/London",
    "Europe/Paris",
    "Asia/Tokyo",
    "Asia/Singapore",
    "Australia/Sydney",
]

ALL_ZONES = sorted(available_timezones())


def _read_tzdata_table(filename: str) -> str:
    """Read a table shipped with the tzdata package."""
    try:
        path = resources.files("tzdata").joinpath("zoneinfo", filename)
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def build_country_timezone_data():
    """
    Build country/area names and country -> IANA time-zone choices from tzdata.

    iso3166.tab supplies ISO alpha-2 country/area names.
    zone.tab supplies the IANA time zones used in each country/area.
    """
    country_names = {}
    country_zones = {}

    iso_text = _read_tzdata_table("iso3166.tab")
    for raw in iso_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("	", 1)
        if len(parts) == 2:
            code, name = parts
            country_names[code] = name

    zone_text = _read_tzdata_table("zone.tab")
    for raw in zone_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("	")
        if len(parts) >= 3:
            code, _coords, zone_name = parts[:3]
            if zone_name in ALL_ZONES:
                country_zones.setdefault(code, []).append(zone_name)

    country_names = {
        code: name
        for code, name in country_names.items()
        if code in country_zones and country_zones[code]
    }

    for code in country_zones:
        country_zones[code] = sorted(
            set(country_zones[code]),
            key=lambda z: (z not in FAVORITE_ZONES, z),
        )

    return country_names, country_zones


COUNTRY_NAMES, COUNTRY_ZONES = build_country_timezone_data()
COUNTRY_CODES = sorted(COUNTRY_NAMES, key=lambda c: COUNTRY_NAMES[c].lower())
COUNTRY_CODE_BY_NAME = {name: code for code, name in COUNTRY_NAMES.items()}

ISO_ALPHA3 = {'AD': 'AND', 'AE': 'ARE', 'AF': 'AFG', 'AG': 'ATG', 'AI': 'AIA', 'AL': 'ALB', 'AM': 'ARM', 'AO': 'AGO', 'AQ': 'ATA', 'AR': 'ARG', 'AS': 'ASM', 'AT': 'AUT', 'AU': 'AUS', 'AW': 'ABW', 'AX': 'ALA', 'AZ': 'AZE', 'BA': 'BIH', 'BB': 'BRB', 'BD': 'BGD', 'BE': 'BEL', 'BF': 'BFA', 'BG': 'BGR', 'BH': 'BHR', 'BI': 'BDI', 'BJ': 'BEN', 'BL': 'BLM', 'BM': 'BMU', 'BN': 'BRN', 'BO': 'BOL', 'BQ': 'BES', 'BR': 'BRA', 'BS': 'BHS', 'BT': 'BTN', 'BV': 'BVT', 'BW': 'BWA', 'BY': 'BLR', 'BZ': 'BLZ', 'CA': 'CAN', 'CC': 'CCK', 'CD': 'COD', 'CF': 'CAF', 'CG': 'COG', 'CH': 'CHE', 'CI': 'CIV', 'CK': 'COK', 'CL': 'CHL', 'CM': 'CMR', 'CN': 'CHN', 'CO': 'COL', 'CR': 'CRI', 'CU': 'CUB', 'CV': 'CPV', 'CW': 'CUW', 'CX': 'CXR', 'CY': 'CYP', 'CZ': 'CZE', 'DE': 'DEU', 'DJ': 'DJI', 'DK': 'DNK', 'DM': 'DMA', 'DO': 'DOM', 'DZ': 'DZA', 'EC': 'ECU', 'EE': 'EST', 'EG': 'EGY', 'EH': 'ESH', 'ER': 'ERI', 'ES': 'ESP', 'ET': 'ETH', 'FI': 'FIN', 'FJ': 'FJI', 'FK': 'FLK', 'FM': 'FSM', 'FO': 'FRO', 'FR': 'FRA', 'GA': 'GAB', 'GB': 'GBR', 'GD': 'GRD', 'GE': 'GEO', 'GF': 'GUF', 'GG': 'GGY', 'GH': 'GHA', 'GI': 'GIB', 'GL': 'GRL', 'GM': 'GMB', 'GN': 'GIN', 'GP': 'GLP', 'GQ': 'GNQ', 'GR': 'GRC', 'GS': 'SGS', 'GT': 'GTM', 'GU': 'GUM', 'GW': 'GNB', 'GY': 'GUY', 'HK': 'HKG', 'HM': 'HMD', 'HN': 'HND', 'HR': 'HRV', 'HT': 'HTI', 'HU': 'HUN', 'ID': 'IDN', 'IE': 'IRL', 'IL': 'ISR', 'IM': 'IMN', 'IN': 'IND', 'IO': 'IOT', 'IQ': 'IRQ', 'IR': 'IRN', 'IS': 'ISL', 'IT': 'ITA', 'JE': 'JEY', 'JM': 'JAM', 'JO': 'JOR', 'JP': 'JPN', 'KE': 'KEN', 'KG': 'KGZ', 'KH': 'KHM', 'KI': 'KIR', 'KM': 'COM', 'KN': 'KNA', 'KP': 'PRK', 'KR': 'KOR', 'KW': 'KWT', 'KY': 'CYM', 'KZ': 'KAZ', 'LA': 'LAO', 'LB': 'LBN', 'LC': 'LCA', 'LI': 'LIE', 'LK': 'LKA', 'LR': 'LBR', 'LS': 'LSO', 'LT': 'LTU', 'LU': 'LUX', 'LV': 'LVA', 'LY': 'LBY', 'MA': 'MAR', 'MC': 'MCO', 'MD': 'MDA', 'ME': 'MNE', 'MF': 'MAF', 'MG': 'MDG', 'MH': 'MHL', 'MK': 'MKD', 'ML': 'MLI', 'MM': 'MMR', 'MN': 'MNG', 'MO': 'MAC', 'MP': 'MNP', 'MQ': 'MTQ', 'MR': 'MRT', 'MS': 'MSR', 'MT': 'MLT', 'MU': 'MUS', 'MV': 'MDV', 'MW': 'MWI', 'MX': 'MEX', 'MY': 'MYS', 'MZ': 'MOZ', 'NA': 'NAM', 'NC': 'NCL', 'NE': 'NER', 'NF': 'NFK', 'NG': 'NGA', 'NI': 'NIC', 'NL': 'NLD', 'NO': 'NOR', 'NP': 'NPL', 'NR': 'NRU', 'NU': 'NIU', 'NZ': 'NZL', 'OM': 'OMN', 'PA': 'PAN', 'PE': 'PER', 'PF': 'PYF', 'PG': 'PNG', 'PH': 'PHL', 'PK': 'PAK', 'PL': 'POL', 'PM': 'SPM', 'PN': 'PCN', 'PR': 'PRI', 'PS': 'PSE', 'PT': 'PRT', 'PW': 'PLW', 'PY': 'PRY', 'QA': 'QAT', 'RE': 'REU', 'RO': 'ROU', 'RS': 'SRB', 'RU': 'RUS', 'RW': 'RWA', 'SA': 'SAU', 'SB': 'SLB', 'SC': 'SYC', 'SD': 'SDN', 'SE': 'SWE', 'SG': 'SGP', 'SH': 'SHN', 'SI': 'SVN', 'SJ': 'SJM', 'SK': 'SVK', 'SL': 'SLE', 'SM': 'SMR', 'SN': 'SEN', 'SO': 'SOM', 'SR': 'SUR', 'SS': 'SSD', 'ST': 'STP', 'SV': 'SLV', 'SX': 'SXM', 'SY': 'SYR', 'SZ': 'SWZ', 'TC': 'TCA', 'TD': 'TCD', 'TF': 'ATF', 'TG': 'TGO', 'TH': 'THA', 'TJ': 'TJK', 'TK': 'TKL', 'TL': 'TLS', 'TM': 'TKM', 'TN': 'TUN', 'TO': 'TON', 'TR': 'TUR', 'TT': 'TTO', 'TV': 'TUV', 'TW': 'TWN', 'TZ': 'TZA', 'UA': 'UKR', 'UG': 'UGA', 'UM': 'UMI', 'US': 'USA', 'UY': 'URY', 'UZ': 'UZB', 'VA': 'VAT', 'VC': 'VCT', 'VE': 'VEN', 'VG': 'VGB', 'VI': 'VIR', 'VN': 'VNM', 'VU': 'VUT', 'WF': 'WLF', 'WS': 'WSM', 'YE': 'YEM', 'YT': 'MYT', 'ZA': 'ZAF', 'ZM': 'ZMB', 'ZW': 'ZWE'}


def country_display_name(code: str) -> str:
    """Friendly country/area label with ISO alpha-3 code."""
    name = COUNTRY_NAMES.get(code, code)
    iso3 = ISO_ALPHA3.get(code, "")
    return f"{name} ({iso3})" if iso3 else name


# U.S. state/territory helper: keeps the U.S. experience simple by narrowing
# the time-zone choices to the zones relevant for the selected state.
US_STATE_ZONES = {
    "Alabama": ["America/Chicago"],
    "Alaska": ["America/Anchorage", "America/Adak"],
    "Arizona": ["America/Phoenix"],
    "Arkansas": ["America/Chicago"],
    "California": ["America/Los_Angeles"],
    "Colorado": ["America/Denver"],
    "Connecticut": ["America/New_York"],
    "Delaware": ["America/New_York"],
    "District of Columbia": ["America/New_York"],
    "Florida": ["America/New_York", "America/Chicago"],
    "Georgia": ["America/New_York"],
    "Hawaii": ["Pacific/Honolulu"],
    "Idaho": ["America/Boise", "America/Los_Angeles"],
    "Illinois": ["America/Chicago"],
    "Indiana": ["America/Indiana/Indianapolis", "America/Chicago"],
    "Iowa": ["America/Chicago"],
    "Kansas": ["America/Chicago", "America/Denver"],
    "Kentucky": ["America/New_York", "America/Chicago"],
    "Louisiana": ["America/Chicago"],
    "Maine": ["America/New_York"],
    "Maryland": ["America/New_York"],
    "Massachusetts": ["America/New_York"],
    "Michigan": ["America/Detroit", "America/Chicago"],
    "Minnesota": ["America/Chicago"],
    "Mississippi": ["America/Chicago"],
    "Missouri": ["America/Chicago"],
    "Montana": ["America/Denver"],
    "Nebraska": ["America/Chicago", "America/Denver"],
    "Nevada": ["America/Los_Angeles"],
    "New Hampshire": ["America/New_York"],
    "New Jersey": ["America/New_York"],
    "New Mexico": ["America/Denver"],
    "New York": ["America/New_York"],
    "North Carolina": ["America/New_York"],
    "North Dakota": ["America/Chicago", "America/Denver"],
    "Ohio": ["America/New_York"],
    "Oklahoma": ["America/Chicago"],
    "Oregon": ["America/Los_Angeles", "America/Boise"],
    "Pennsylvania": ["America/New_York"],
    "Rhode Island": ["America/New_York"],
    "South Carolina": ["America/New_York"],
    "South Dakota": ["America/Chicago", "America/Denver"],
    "Tennessee": ["America/New_York", "America/Chicago"],
    "Texas": ["America/Chicago", "America/Denver"],
    "Utah": ["America/Denver"],
    "Vermont": ["America/New_York"],
    "Virginia": ["America/New_York"],
    "Washington": ["America/Los_Angeles"],
    "West Virginia": ["America/New_York"],
    "Wisconsin": ["America/Chicago"],
    "Wyoming": ["America/Denver"],
}
US_STATES = list(US_STATE_ZONES.keys())


def infer_us_state(person: dict) -> str:
    """Use a saved state or infer one from legacy location text."""
    saved = str(person.get("state", "")).strip()
    if saved in US_STATE_ZONES:
        return saved

    legacy = str(person.get("location", "")).strip()
    for state in US_STATES:
        if legacy.lower() == state.lower():
            return state

    # Preserve the current sample participant behavior.
    if person.get("name", "").strip().lower() == "sam":
        return "Oregon"

    return "California"


# UN M49 geographic classification (embedded from the uploaded UNSD Methodology workbook).
# This is informational only; IANA/tzdata remains the source for time-zone calculations.
UN_M49_GEO = {'AD': {'country': 'Andorra', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'AE': {'country': 'United Arab Emirates', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'AF': {'country': 'Afghanistan', 'intermediate': None, 'region': 'Asia', 'subregion': 'Southern Asia'},
 'AG': {'country': 'Antigua and Barbuda',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'AI': {'country': 'Anguilla',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'AL': {'country': 'Albania', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'AM': {'country': 'Armenia', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'AO': {'country': 'Angola', 'intermediate': 'Middle Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'AQ': {'country': 'Antarctica', 'intermediate': None, 'region': None, 'subregion': None},
 'AR': {'country': 'Argentina',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'AS': {'country': 'American Samoa', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Polynesia'},
 'AT': {'country': 'Austria', 'intermediate': None, 'region': 'Europe', 'subregion': 'Western Europe'},
 'AU': {'country': 'Australia', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Australia and New Zealand'},
 'AW': {'country': 'Aruba',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'AX': {'country': 'Åland Islands', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'AZ': {'country': 'Azerbaijan', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'BA': {'country': 'Bosnia and Herzegovina', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'BB': {'country': 'Barbados',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'BD': {'country': 'Bangladesh', 'intermediate': None, 'region': 'Asia', 'subregion': 'Southern Asia'},
 'BE': {'country': 'Belgium', 'intermediate': None, 'region': 'Europe', 'subregion': 'Western Europe'},
 'BF': {'country': 'Burkina Faso',
        'intermediate': 'Western Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'BG': {'country': 'Bulgaria', 'intermediate': None, 'region': 'Europe', 'subregion': 'Eastern Europe'},
 'BH': {'country': 'Bahrain', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'BI': {'country': 'Burundi', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'BJ': {'country': 'Benin', 'intermediate': 'Western Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'BL': {'country': 'Saint Barthélemy',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'BM': {'country': 'Bermuda', 'intermediate': None, 'region': 'Americas', 'subregion': 'Northern America'},
 'BN': {'country': 'Brunei Darussalam', 'intermediate': None, 'region': 'Asia', 'subregion': 'South-eastern Asia'},
 'BO': {'country': 'Bolivia (Plurinational State of)',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'BQ': {'country': 'Bonaire, Sint Eustatius and Saba',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'BR': {'country': 'Brazil',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'BS': {'country': 'Bahamas',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'BT': {'country': 'Bhutan', 'intermediate': None, 'region': 'Asia', 'subregion': 'Southern Asia'},
 'BV': {'country': 'Bouvet Island',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'BW': {'country': 'Botswana',
        'intermediate': 'Southern Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'BY': {'country': 'Belarus', 'intermediate': None, 'region': 'Europe', 'subregion': 'Eastern Europe'},
 'BZ': {'country': 'Belize',
        'intermediate': 'Central America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'CA': {'country': 'Canada', 'intermediate': None, 'region': 'Americas', 'subregion': 'Northern America'},
 'CC': {'country': 'Cocos (Keeling) Islands',
        'intermediate': None,
        'region': 'Oceania',
        'subregion': 'Australia and New Zealand'},
 'CD': {'country': 'Democratic Republic of the Congo',
        'intermediate': 'Middle Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'CF': {'country': 'Central African Republic',
        'intermediate': 'Middle Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'CG': {'country': 'Congo', 'intermediate': 'Middle Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'CH': {'country': 'Switzerland', 'intermediate': None, 'region': 'Europe', 'subregion': 'Western Europe'},
 'CI': {'country': 'Côte d’Ivoire',
        'intermediate': 'Western Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'CK': {'country': 'Cook Islands', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Polynesia'},
 'CL': {'country': 'Chile',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'CM': {'country': 'Cameroon', 'intermediate': 'Middle Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'CN': {'country': 'China', 'intermediate': None, 'region': 'Asia', 'subregion': 'Eastern Asia'},
 'CO': {'country': 'Colombia',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'CR': {'country': 'Costa Rica',
        'intermediate': 'Central America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'CU': {'country': 'Cuba',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'CV': {'country': 'Cabo Verde',
        'intermediate': 'Western Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'CW': {'country': 'Curaçao',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'CX': {'country': 'Christmas Island',
        'intermediate': None,
        'region': 'Oceania',
        'subregion': 'Australia and New Zealand'},
 'CY': {'country': 'Cyprus', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'CZ': {'country': 'Czechia', 'intermediate': None, 'region': 'Europe', 'subregion': 'Eastern Europe'},
 'DE': {'country': 'Germany', 'intermediate': None, 'region': 'Europe', 'subregion': 'Western Europe'},
 'DJ': {'country': 'Djibouti', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'DK': {'country': 'Denmark', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'DM': {'country': 'Dominica',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'DO': {'country': 'Dominican Republic',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'DZ': {'country': 'Algeria', 'intermediate': None, 'region': 'Africa', 'subregion': 'Northern Africa'},
 'EC': {'country': 'Ecuador',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'EE': {'country': 'Estonia', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'EG': {'country': 'Egypt', 'intermediate': None, 'region': 'Africa', 'subregion': 'Northern Africa'},
 'EH': {'country': 'Western Sahara', 'intermediate': None, 'region': 'Africa', 'subregion': 'Northern Africa'},
 'ER': {'country': 'Eritrea', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'ES': {'country': 'Spain', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'ET': {'country': 'Ethiopia', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'FI': {'country': 'Finland', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'FJ': {'country': 'Fiji', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Melanesia'},
 'FK': {'country': 'Falkland Islands (Malvinas)',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'FM': {'country': 'Micronesia (Federated States of)',
        'intermediate': None,
        'region': 'Oceania',
        'subregion': 'Micronesia'},
 'FO': {'country': 'Faroe Islands', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'FR': {'country': 'France', 'intermediate': None, 'region': 'Europe', 'subregion': 'Western Europe'},
 'GA': {'country': 'Gabon', 'intermediate': 'Middle Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'GB': {'country': 'United Kingdom of Great Britain and Northern Ireland',
        'intermediate': None,
        'region': 'Europe',
        'subregion': 'Northern Europe'},
 'GD': {'country': 'Grenada',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'GE': {'country': 'Georgia', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'GF': {'country': 'French Guiana',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'GG': {'country': 'Guernsey', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'GH': {'country': 'Ghana', 'intermediate': 'Western Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'GI': {'country': 'Gibraltar', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'GL': {'country': 'Greenland', 'intermediate': None, 'region': 'Americas', 'subregion': 'Northern America'},
 'GM': {'country': 'Gambia', 'intermediate': 'Western Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'GN': {'country': 'Guinea', 'intermediate': 'Western Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'GP': {'country': 'Guadeloupe',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'GQ': {'country': 'Equatorial Guinea',
        'intermediate': 'Middle Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'GR': {'country': 'Greece', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'GS': {'country': 'South Georgia and the South Sandwich Islands',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'GT': {'country': 'Guatemala',
        'intermediate': 'Central America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'GU': {'country': 'Guam', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Micronesia'},
 'GW': {'country': 'Guinea-Bissau',
        'intermediate': 'Western Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'GY': {'country': 'Guyana',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'HK': {'country': 'China, Hong Kong Special Administrative Region',
        'intermediate': None,
        'region': 'Asia',
        'subregion': 'Eastern Asia'},
 'HM': {'country': 'Heard Island and McDonald Islands',
        'intermediate': None,
        'region': 'Oceania',
        'subregion': 'Australia and New Zealand'},
 'HN': {'country': 'Honduras',
        'intermediate': 'Central America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'HR': {'country': 'Croatia', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'HT': {'country': 'Haiti',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'HU': {'country': 'Hungary', 'intermediate': None, 'region': 'Europe', 'subregion': 'Eastern Europe'},
 'ID': {'country': 'Indonesia', 'intermediate': None, 'region': 'Asia', 'subregion': 'South-eastern Asia'},
 'IE': {'country': 'Ireland', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'IL': {'country': 'Israel', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'IM': {'country': 'Isle of Man', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'IN': {'country': 'India', 'intermediate': None, 'region': 'Asia', 'subregion': 'Southern Asia'},
 'IO': {'country': 'British Indian Ocean Territory',
        'intermediate': 'Eastern Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'IQ': {'country': 'Iraq', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'IR': {'country': 'Iran (Islamic Republic of)', 'intermediate': None, 'region': 'Asia', 'subregion': 'Southern Asia'},
 'IS': {'country': 'Iceland', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'IT': {'country': 'Italy', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'JE': {'country': 'Jersey', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'JM': {'country': 'Jamaica',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'JO': {'country': 'Jordan', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'JP': {'country': 'Japan', 'intermediate': None, 'region': 'Asia', 'subregion': 'Eastern Asia'},
 'KE': {'country': 'Kenya', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'KG': {'country': 'Kyrgyzstan', 'intermediate': None, 'region': 'Asia', 'subregion': 'Central Asia'},
 'KH': {'country': 'Cambodia', 'intermediate': None, 'region': 'Asia', 'subregion': 'South-eastern Asia'},
 'KI': {'country': 'Kiribati', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Micronesia'},
 'KM': {'country': 'Comoros', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'KN': {'country': 'Saint Kitts and Nevis',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'KP': {'country': "Democratic People's Republic of Korea",
        'intermediate': None,
        'region': 'Asia',
        'subregion': 'Eastern Asia'},
 'KR': {'country': 'Republic of Korea', 'intermediate': None, 'region': 'Asia', 'subregion': 'Eastern Asia'},
 'KW': {'country': 'Kuwait', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'KY': {'country': 'Cayman Islands',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'KZ': {'country': 'Kazakhstan', 'intermediate': None, 'region': 'Asia', 'subregion': 'Central Asia'},
 'LA': {'country': "Lao People's Democratic Republic",
        'intermediate': None,
        'region': 'Asia',
        'subregion': 'South-eastern Asia'},
 'LB': {'country': 'Lebanon', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'LC': {'country': 'Saint Lucia',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'LI': {'country': 'Liechtenstein', 'intermediate': None, 'region': 'Europe', 'subregion': 'Western Europe'},
 'LK': {'country': 'Sri Lanka', 'intermediate': None, 'region': 'Asia', 'subregion': 'Southern Asia'},
 'LR': {'country': 'Liberia', 'intermediate': 'Western Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'LS': {'country': 'Lesotho', 'intermediate': 'Southern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'LT': {'country': 'Lithuania', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'LU': {'country': 'Luxembourg', 'intermediate': None, 'region': 'Europe', 'subregion': 'Western Europe'},
 'LV': {'country': 'Latvia', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'LY': {'country': 'Libya', 'intermediate': None, 'region': 'Africa', 'subregion': 'Northern Africa'},
 'MA': {'country': 'Morocco', 'intermediate': None, 'region': 'Africa', 'subregion': 'Northern Africa'},
 'MC': {'country': 'Monaco', 'intermediate': None, 'region': 'Europe', 'subregion': 'Western Europe'},
 'MD': {'country': 'Republic of Moldova', 'intermediate': None, 'region': 'Europe', 'subregion': 'Eastern Europe'},
 'ME': {'country': 'Montenegro', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'MF': {'country': 'Saint Martin (French Part)',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'MG': {'country': 'Madagascar',
        'intermediate': 'Eastern Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'MH': {'country': 'Marshall Islands', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Micronesia'},
 'MK': {'country': 'North Macedonia', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'ML': {'country': 'Mali', 'intermediate': 'Western Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'MM': {'country': 'Myanmar', 'intermediate': None, 'region': 'Asia', 'subregion': 'South-eastern Asia'},
 'MN': {'country': 'Mongolia', 'intermediate': None, 'region': 'Asia', 'subregion': 'Eastern Asia'},
 'MO': {'country': 'China, Macao Special Administrative Region',
        'intermediate': None,
        'region': 'Asia',
        'subregion': 'Eastern Asia'},
 'MP': {'country': 'Northern Mariana Islands', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Micronesia'},
 'MQ': {'country': 'Martinique',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'MR': {'country': 'Mauritania',
        'intermediate': 'Western Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'MS': {'country': 'Montserrat',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'MT': {'country': 'Malta', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'MU': {'country': 'Mauritius',
        'intermediate': 'Eastern Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'MV': {'country': 'Maldives', 'intermediate': None, 'region': 'Asia', 'subregion': 'Southern Asia'},
 'MW': {'country': 'Malawi', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'MX': {'country': 'Mexico',
        'intermediate': 'Central America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'MY': {'country': 'Malaysia', 'intermediate': None, 'region': 'Asia', 'subregion': 'South-eastern Asia'},
 'MZ': {'country': 'Mozambique',
        'intermediate': 'Eastern Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'NA': {'country': 'Namibia', 'intermediate': 'Southern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'NC': {'country': 'New Caledonia', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Melanesia'},
 'NE': {'country': 'Niger', 'intermediate': 'Western Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'NF': {'country': 'Norfolk Island',
        'intermediate': None,
        'region': 'Oceania',
        'subregion': 'Australia and New Zealand'},
 'NG': {'country': 'Nigeria', 'intermediate': 'Western Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'NI': {'country': 'Nicaragua',
        'intermediate': 'Central America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'NL': {'country': 'Netherlands (Kingdom of the)',
        'intermediate': None,
        'region': 'Europe',
        'subregion': 'Western Europe'},
 'NO': {'country': 'Norway', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'NP': {'country': 'Nepal', 'intermediate': None, 'region': 'Asia', 'subregion': 'Southern Asia'},
 'NR': {'country': 'Naoero', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Micronesia'},
 'NU': {'country': 'Niue', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Polynesia'},
 'NZ': {'country': 'New Zealand', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Australia and New Zealand'},
 'OM': {'country': 'Oman', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'PA': {'country': 'Panama',
        'intermediate': 'Central America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'PE': {'country': 'Peru',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'PF': {'country': 'French Polynesia', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Polynesia'},
 'PG': {'country': 'Papua New Guinea', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Melanesia'},
 'PH': {'country': 'Philippines', 'intermediate': None, 'region': 'Asia', 'subregion': 'South-eastern Asia'},
 'PK': {'country': 'Pakistan', 'intermediate': None, 'region': 'Asia', 'subregion': 'Southern Asia'},
 'PL': {'country': 'Poland', 'intermediate': None, 'region': 'Europe', 'subregion': 'Eastern Europe'},
 'PM': {'country': 'Saint Pierre and Miquelon',
        'intermediate': None,
        'region': 'Americas',
        'subregion': 'Northern America'},
 'PN': {'country': 'Pitcairn', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Polynesia'},
 'PR': {'country': 'Puerto Rico',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'PS': {'country': 'State of Palestine', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'PT': {'country': 'Portugal', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'PW': {'country': 'Palau', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Micronesia'},
 'PY': {'country': 'Paraguay',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'QA': {'country': 'Qatar', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'RE': {'country': 'Réunion', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'RO': {'country': 'Romania', 'intermediate': None, 'region': 'Europe', 'subregion': 'Eastern Europe'},
 'RS': {'country': 'Serbia', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'RU': {'country': 'Russian Federation', 'intermediate': None, 'region': 'Europe', 'subregion': 'Eastern Europe'},
 'RW': {'country': 'Rwanda', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'SA': {'country': 'Saudi Arabia', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'SB': {'country': 'Solomon Islands', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Melanesia'},
 'SC': {'country': 'Seychelles',
        'intermediate': 'Eastern Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'SD': {'country': 'Sudan', 'intermediate': None, 'region': 'Africa', 'subregion': 'Northern Africa'},
 'SE': {'country': 'Sweden', 'intermediate': None, 'region': 'Europe', 'subregion': 'Northern Europe'},
 'SG': {'country': 'Singapore', 'intermediate': None, 'region': 'Asia', 'subregion': 'South-eastern Asia'},
 'SH': {'country': 'Saint Helena',
        'intermediate': 'Western Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'SI': {'country': 'Slovenia', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'SJ': {'country': 'Svalbard and Jan Mayen Islands',
        'intermediate': None,
        'region': 'Europe',
        'subregion': 'Northern Europe'},
 'SK': {'country': 'Slovakia', 'intermediate': None, 'region': 'Europe', 'subregion': 'Eastern Europe'},
 'SL': {'country': 'Sierra Leone',
        'intermediate': 'Western Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'SM': {'country': 'San Marino', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'SN': {'country': 'Senegal', 'intermediate': 'Western Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'SO': {'country': 'Somalia', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'SR': {'country': 'Suriname',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'SS': {'country': 'South Sudan',
        'intermediate': 'Eastern Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'ST': {'country': 'Sao Tome and Principe',
        'intermediate': 'Middle Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'SV': {'country': 'El Salvador',
        'intermediate': 'Central America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'SX': {'country': 'Sint Maarten (Dutch part)',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'SY': {'country': 'Syrian Arab Republic', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'SZ': {'country': 'Eswatini',
        'intermediate': 'Southern Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'TC': {'country': 'Turks and Caicos Islands',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'TD': {'country': 'Chad', 'intermediate': 'Middle Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'TF': {'country': 'French Southern Territories',
        'intermediate': 'Eastern Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'TG': {'country': 'Togo', 'intermediate': 'Western Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'TH': {'country': 'Thailand', 'intermediate': None, 'region': 'Asia', 'subregion': 'South-eastern Asia'},
 'TJ': {'country': 'Tajikistan', 'intermediate': None, 'region': 'Asia', 'subregion': 'Central Asia'},
 'TK': {'country': 'Tokelau', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Polynesia'},
 'TL': {'country': 'Timor-Leste', 'intermediate': None, 'region': 'Asia', 'subregion': 'South-eastern Asia'},
 'TM': {'country': 'Turkmenistan', 'intermediate': None, 'region': 'Asia', 'subregion': 'Central Asia'},
 'TN': {'country': 'Tunisia', 'intermediate': None, 'region': 'Africa', 'subregion': 'Northern Africa'},
 'TO': {'country': 'Tonga', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Polynesia'},
 'TR': {'country': 'Türkiye', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'TT': {'country': 'Trinidad and Tobago',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'TV': {'country': 'Tuvalu', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Polynesia'},
 'TZ': {'country': 'United Republic of Tanzania',
        'intermediate': 'Eastern Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'UA': {'country': 'Ukraine', 'intermediate': None, 'region': 'Europe', 'subregion': 'Eastern Europe'},
 'UG': {'country': 'Uganda', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'UM': {'country': 'United States Minor Outlying Islands',
        'intermediate': None,
        'region': 'Oceania',
        'subregion': 'Micronesia'},
 'US': {'country': 'United States of America',
        'intermediate': None,
        'region': 'Americas',
        'subregion': 'Northern America'},
 'UY': {'country': 'Uruguay',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'UZ': {'country': 'Uzbekistan', 'intermediate': None, 'region': 'Asia', 'subregion': 'Central Asia'},
 'VA': {'country': 'Holy See', 'intermediate': None, 'region': 'Europe', 'subregion': 'Southern Europe'},
 'VC': {'country': 'Saint Vincent and the Grenadines',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'VE': {'country': 'Venezuela (Bolivarian Republic of)',
        'intermediate': 'South America',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'VG': {'country': 'British Virgin Islands',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'VI': {'country': 'United States Virgin Islands',
        'intermediate': 'Caribbean',
        'region': 'Americas',
        'subregion': 'Latin America and the Caribbean'},
 'VN': {'country': 'Viet Nam', 'intermediate': None, 'region': 'Asia', 'subregion': 'South-eastern Asia'},
 'VU': {'country': 'Vanuatu', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Melanesia'},
 'WF': {'country': 'Wallis and Futuna Islands', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Polynesia'},
 'WS': {'country': 'Samoa', 'intermediate': None, 'region': 'Oceania', 'subregion': 'Polynesia'},
 'YE': {'country': 'Yemen', 'intermediate': None, 'region': 'Asia', 'subregion': 'Western Asia'},
 'YT': {'country': 'Mayotte', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'ZA': {'country': 'South Africa',
        'intermediate': 'Southern Africa',
        'region': 'Africa',
        'subregion': 'Sub-Saharan Africa'},
 'ZM': {'country': 'Zambia', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'},
 'ZW': {'country': 'Zimbabwe', 'intermediate': 'Eastern Africa', 'region': 'Africa', 'subregion': 'Sub-Saharan Africa'}}


def un_region_label(country_code: str) -> str:
    """Return a compact UN M49 region/sub-region label for display."""
    # The supplied UN M49 workbook does not contain a separate Taiwan row.
    # Show useful geographic context without pretending that the source does.
    if country_code == "TW":
        return "Asia · Eastern Asia · not separately listed in the supplied UN M49 source"

    info = UN_M49_GEO.get(country_code, {})
    parts = [info.get("region"), info.get("subregion"), info.get("intermediate")]
    parts = [p for p in parts if p]
    return " · ".join(parts) if parts else "UN M49 classification unavailable"


def country_code_for_timezone(tz_name: str):
    """Return the first ISO country/area code using this IANA zone."""
    for code, zones in COUNTRY_ZONES.items():
        if tz_name in zones:
            return code
    return None


def infer_country_code(person: dict):
    """Resolve a participant's country/area from saved country, location, or time zone."""
    saved = str(person.get("country_code", "")).upper()
    if saved in COUNTRY_NAMES:
        return saved

    location = (person.get("location") or "").strip().lower()
    for code, name in COUNTRY_NAMES.items():
        if location == name.lower():
            return code

    aliases = {
        "germany": "DE",
        "deutschland": "DE",
        "oregon": "US",
        "united states": "US",
        "united states of america": "US",
        "usa": "US",
        "us": "US",
        "taipei": "TW",
        "taiwan": "TW",
        "united kingdom": "GB",
        "uk": "GB",
    }
    if location in aliases and aliases[location] in COUNTRY_NAMES:
        return aliases[location]

    return country_code_for_timezone(person.get("tz_name", "")) or (
        "DE" if "DE" in COUNTRY_NAMES else COUNTRY_CODES[0]
    )


def friendly_zone_name(tz_name: str) -> str:
    """Turn technical IANA identifiers into friendlier visible labels."""
    common = {
        "UTC": "UTC",
        "Europe/Berlin": "Central European Time (Berlin)",
        "Europe/London": "UK Time (London)",
        "Europe/Paris": "Central European Time (Paris)",
        "America/New_York": "US Eastern Time (New York)",
        "America/Chicago": "US Central Time (Chicago)",
        "America/Denver": "US Mountain Time (Denver)",
        "America/Los_Angeles": "US Pacific Time (Los Angeles)",
        "America/Boise": "US Mountain Time (Boise)",
        "America/Phoenix": "Arizona Time (Phoenix)",
        "America/Anchorage": "Alaska Time (Anchorage)",
        "America/Adak": "Hawaii-Aleutian Time (Adak)",
        "America/Detroit": "US Eastern Time (Detroit)",
        "America/Indiana/Indianapolis": "US Eastern Time (Indianapolis)",
        "Pacific/Honolulu": "Hawaii Time (Honolulu)",
        "Asia/Taipei": "Taipei Time",
        "Asia/Tokyo": "Japan Time (Tokyo)",
        "Asia/Singapore": "Singapore Time",
        "Australia/Sydney": "Sydney Time",
    }
    if tz_name in common:
        return common[tz_name]

    tail = tz_name.split("/")[-1].replace("_", " ")
    area = tz_name.split("/")[0].replace("_", " ")
    return f"{tail} ({area})"


def new_id():
    return uuid.uuid4().hex[:10]


def utc_offset_label(tz_name: str, ref_date: date) -> str:
    """Return the actual UTC offset for this zone on the selected date."""
    tz = ZoneInfo(tz_name)
    # Noon avoids edge cases around midnight DST transitions.
    dt = datetime.combine(ref_date, time(12, 0), tzinfo=tz)
    offset = dt.utcoffset()
    if offset is None:
        return "UTC?"
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    hh, mm = divmod(total_minutes, 60)
    if mm == 0:
        return f"UTC{sign}{hh}"
    return f"UTC{sign}{hh:02d}:{mm:02d}"


def zone_display(tz_name: str, ref_date: date) -> str:
    return f"{friendly_zone_name(tz_name)} · {utc_offset_label(tz_name, ref_date)}"


def minutes_of_day(t: time) -> int:
    return t.hour * 60 + t.minute



def solar_position_approx(utc_dt: datetime):
    """
    Approximate solar declination and subsolar longitude for a UTC datetime.

    Uses the NOAA fractional-year / equation-of-time approximation.
    Accuracy is more than sufficient for a visual day/night overlay.
    Returns:
        declination_degrees,
        subsolar_longitude_degrees
    """
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=ZoneInfo("UTC"))
    else:
        utc_dt = utc_dt.astimezone(ZoneInfo("UTC"))

    day_of_year = utc_dt.timetuple().tm_yday
    fractional_hour = (
        utc_dt.hour
        + utc_dt.minute / 60
        + utc_dt.second / 3600
    )

    gamma = (
        2 * math.pi / 365
        * (day_of_year - 1 + (fractional_hour - 12) / 24)
    )

    equation_of_time = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )

    declination = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.00148 * math.sin(3 * gamma)
    )

    utc_minutes = fractional_hour * 60
    subsolar_lon = (720 - utc_minutes - equation_of_time) / 4

    while subsolar_lon > 180:
        subsolar_lon -= 360
    while subsolar_lon < -180:
        subsolar_lon += 360

    return math.degrees(declination), subsolar_lon


def add_day_night_overlay(fig, utc_dt: datetime):
    """
    Shade the night hemisphere on the world map for the proposed meeting instant.

    The unshaded area is daylight. The overlay is visual guidance rather than
    an astronomical navigation product.
    """
    declination_deg, subsolar_lon = solar_position_approx(utc_dt)
    declination = math.radians(declination_deg)

    longitudes = [x for x in range(-180, 181, 2)]
    terminator_lats = []

    sin_decl = math.sin(declination)
    # Around the equinox, use a tiny signed value so the terminator becomes
    # the expected near-vertical day/night boundary rather than dividing by 0.
    if abs(sin_decl) < 1e-6:
        sin_decl = 1e-6 if declination >= 0 else -1e-6

    cos_decl = math.cos(declination)

    for lon in longitudes:
        hour_angle = math.radians(lon - subsolar_lon)
        ratio = -cos_decl * math.cos(hour_angle) / sin_decl
        lat = math.degrees(math.atan(ratio))
        terminator_lats.append(lat)

    # Northern-summer declination => night is south of the terminator.
    # Southern-summer declination => night is north of it.
    if declination_deg >= 0:
        night_lons = longitudes + [180, -180]
        night_lats = terminator_lats + [-90, -90]
    else:
        night_lons = longitudes + [180, -180]
        night_lats = terminator_lats + [90, 90]

    fig.add_trace(
        go.Scattergeo(
            lon=night_lons,
            lat=night_lats,
            mode="lines",
            line=dict(width=0),
            fill="toself",
            fillcolor="rgba(36, 41, 48, 0.18)",
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Small sun marker at the subsolar point.
    fig.add_trace(
        go.Scattergeo(
            lon=[subsolar_lon],
            lat=[declination_deg],
            mode="markers",
            marker=dict(
                size=8,
                color="#E8B47A",
                line=dict(color="#ffffff", width=0.8),
            ),
            hovertemplate=(
                "<b>Approximate subsolar point</b><br>"
                "Sun is highest here at this instant<extra></extra>"
            ),
            showlegend=False,
        )
    )


# ---------- Visualization helpers ----------

PARTICIPANT_COLORS = [
    "#cd549e",
    "#ff66c4",
    "#34363a",
    "#8f949a",
    "#a7397d",
    "#d8a2c3",
    "#656a70",
    "#f0b6d9",
]

STATUS_COLORS = {
    "Available": "#A8C9AE",
    "Outside availability": "#F3D6E7",
    "Sleep hours": "#4A4A4A",
}

LOCATION_COORDS = {
    "germany": (51.1657, 10.4515),
    "berlin": (52.5200, 13.4050),
    "oregon": (44.0000, -120.5000),
    "portland": (45.5152, -122.6784),
    "taipei": (25.0330, 121.5654),
    "taiwan": (23.6978, 120.9605),
    "new york": (40.7128, -74.0060),
    "texas": (31.0000, -99.0000),
    "london": (51.5074, -0.1278),
    "paris": (48.8566, 2.3522),
    "tokyo": (35.6762, 139.6503),
    "singapore": (1.3521, 103.8198),
    "sydney": (-33.8688, 151.2093),
    "los angeles": (34.0522, -118.2437),
    "seattle": (47.6062, -122.3321),
    "chicago": (41.8781, -87.6298),
    "denver": (39.7392, -104.9903),
}

TIMEZONE_COORDS = {
    "Europe/Berlin": (52.5200, 13.4050),
    "America/Los_Angeles": (45.5152, -122.6784),
    "Asia/Taipei": (25.0330, 121.5654),
    "America/New_York": (40.7128, -74.0060),
    "America/Chicago": (41.8781, -87.6298),
    "America/Denver": (39.7392, -104.9903),
    "Europe/London": (51.5074, -0.1278),
    "Europe/Paris": (48.8566, 2.3522),
    "Asia/Tokyo": (35.6762, 139.6503),
    "Asia/Singapore": (1.3521, 103.8198),
    "Australia/Sydney": (-33.8688, 151.2093),
    "UTC": (0.0, 0.0),
}


def participant_color(index: int) -> str:
    return PARTICIPANT_COLORS[index % len(PARTICIPANT_COLORS)]


def _time_in_window(local_t: time, start_t: time, end_t: time) -> bool:
    """Return True when local_t falls inside the selected availability window."""
    current = minutes_of_day(local_t)
    start = minutes_of_day(start_t)
    end = minutes_of_day(end_t)

    if start == end:
        return True
    if start < end:
        return start <= current < end
    # Supports an overnight availability window, e.g. 22:00–06:00.
    return current >= start or current < end


def local_status(person: dict, local_dt: datetime):
    """
    Map-status convention.

    Green means the participant is inside the availability window they selected.
    Outside that window, 00:00–06:00 is shown as sleep time and all other hours
    are shown as outside availability.
    """
    if _time_in_window(local_dt.time(), person["earliest"], person["latest"]):
        return "Available", STATUS_COLORS["Available"]

    local_hour = local_dt.hour + local_dt.minute / 60
    if 0 <= local_hour < 6:
        return "Sleep hours", STATUS_COLORS["Sleep hours"]

    return "Outside availability", STATUS_COLORS["Outside availability"]


def local_clock_segments_utc(person: dict, ref_date: date):
    """
    Build a 24-hour UTC status band for one participant.

    The participant's selected availability overrides the generic day context.
    Outside that window, 00:00–06:00 local is sleep and remaining hours are
    outside availability.
    """
    tz = ZoneInfo(person["tz_name"])
    utc_anchor = datetime.combine(ref_date, time(0, 0), tzinfo=ZoneInfo("UTC"))

    # Build 15-minute local segments so user-entered quarter-hour availability
    # boundaries are represented accurately and DST is handled by ZoneInfo.
    output = []
    step = timedelta(minutes=15)
    start_local = datetime.combine(ref_date, time(0, 0), tzinfo=tz)

    raw = []
    for i in range(96):
        local_dt = start_local + i * step
        label, _ = local_status(person, local_dt)
        utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
        start_h = ((utc_dt - utc_anchor).total_seconds() / 3600) % 24
        raw.append((label, start_h, 0.25))

    # Merge adjacent UTC segments with the same label where possible.
    for label, start_h, width_h in raw:
        if output:
            prev_label, prev_start, prev_width = output[-1]
            expected = (prev_start + prev_width) % 24
            if prev_label == label and abs(expected - start_h) < 1e-9 and prev_start + prev_width <= 24:
                output[-1] = (prev_label, prev_start, prev_width + width_h)
                continue
        output.append((label, start_h, width_h))

    return output


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    value = hex_color.lstrip("#")
    r = int(value[0:2], 16)
    g = int(value[2:4], 16)
    b = int(value[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def utc_offset_hours(tz_name: str, ref_date: date) -> float:
    tz = ZoneInfo(tz_name)
    dt = datetime.combine(ref_date, time(12, 0), tzinfo=tz)
    offset = dt.utcoffset() or timedelta(0)
    return offset.total_seconds() / 3600


def approximate_map_coords(person: dict, ref_date: date):
    location_key = (person.get("location") or "").strip().lower()

    if location_key in LOCATION_COORDS:
        return LOCATION_COORDS[location_key], False

    for key, coords in LOCATION_COORDS.items():
        if key in location_key or location_key in key:
            return coords, False

    tz_name = person.get("tz_name", "UTC")
    if tz_name in TIMEZONE_COORDS:
        return TIMEZONE_COORDS[tz_name], True

    # Fallback: place the marker on the central meridian implied by the UTC offset.
    # This is only a scheduling visualization, not a geographic timezone boundary.
    lon = utc_offset_hours(tz_name, ref_date) * 15
    while lon > 180:
        lon -= 360
    while lon < -180:
        lon += 360
    return (0.0, lon), True


def add_timezone_band(fig, center_lon: float, color: str):
    """Add an approximate 15-degree-wide visual UTC-offset band."""
    start = center_lon - 7.5
    end = center_lon + 7.5

    def add_piece(a, b):
        fig.add_trace(
            go.Scattergeo(
                lon=[a, b, b, a, a],
                lat=[-58, -58, 78, 78, -58],
                mode="lines",
                line=dict(width=0),
                fill="toself",
                fillcolor=hex_to_rgba(color, 0.12),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    if start < -180:
        add_piece(start + 360, 180)
        add_piece(-180, end)
    elif end > 180:
        add_piece(start, 180)
        add_piece(-180, end - 360)
    else:
        add_piece(start, end)


def preferred_window_utc_segments(person: dict, ref_date: date):
    """Return preferred local hours as one or two segments on a 0–24 UTC axis."""
    tz = ZoneInfo(person["tz_name"])
    local_start = datetime.combine(ref_date, person["earliest"], tzinfo=tz)
    local_end = datetime.combine(ref_date, person["latest"], tzinfo=tz)

    start_utc = local_start.astimezone(ZoneInfo("UTC"))
    end_utc = local_end.astimezone(ZoneInfo("UTC"))

    start_hour = start_utc.hour + start_utc.minute / 60
    duration_hours = (end_utc - start_utc).total_seconds() / 3600
    end_hour = start_hour + duration_hours

    if end_hour <= 24:
        return [(start_hour, duration_hours)]

    return [
        (start_hour, 24 - start_hour),
        (0, end_hour - 24),
    ]

# ---------- Saved setups / session memory ----------

DEFAULT_MEETING_DATE = date.today()
DEFAULT_DURATION_MINUTES = 60
DEFAULT_START_INTERVAL_MINUTES = 30

DURATION_OPTIONS = [30, 45, 60, 90]
START_INTERVAL_OPTIONS = [15, 30, 60]


def default_people():
    """Return a fresh copy of the default participant list."""
    return [
        {
            "id": new_id(),
            "name": "Germany team",
            "location": "Germany",
            "country_code": "DE",
            "tz_name": "Europe/Berlin",
            "earliest": time(8, 0),
            "latest": time(17, 0),
        },
        {
            "id": new_id(),
            "name": "U.S. team",
            "location": "United States",
            "country_code": "US",
            "state": "Oregon",
            "tz_name": "America/Los_Angeles",
            "earliest": time(8, 0),
            "latest": time(17, 0),
        },
        {
            "id": new_id(),
            "name": "Taipei team",
            "location": "Taiwan",
            "country_code": "TW",
            "tz_name": "Asia/Taipei",
            "earliest": time(8, 0),
            "latest": time(17, 0),
        },
    ]


def parse_preset_time(value) -> time:
    """Parse HH:MM from a preset into datetime.time."""
    if isinstance(value, time):
        return value
    return datetime.strptime(str(value), "%H:%M").time()


def build_preset_payload(meeting_date, duration, interval, people):
    """Build a portable JSON-safe preset from the current app state."""
    return {
        "app": "Drapalski Global Meeting Planner",
        "preset_version": 1,
        "meeting_date": meeting_date.isoformat(),
        "meeting_duration_minutes": int(duration),
        "start_time_interval_minutes": int(interval),
        "participants": [
            {
                "name": p["name"],
                "location": p["location"],
                "country_code": p.get("country_code", ""),
                "state": p.get("state", ""),
                "time_zone": p["tz_name"],
                "earliest": p["earliest"].strftime("%H:%M"),
                "latest": p["latest"].strftime("%H:%M"),
            }
            for p in people
        ],
    }


def load_preset_payload(payload):
    """Validate a JSON preset and convert it into app state."""
    if not isinstance(payload, dict):
        raise ValueError("Saved setup must contain a JSON object.")

    meeting_date_value = date.fromisoformat(
        str(payload.get("meeting_date", DEFAULT_MEETING_DATE.isoformat()))
    )
    duration_value = int(
        payload.get("meeting_duration_minutes", DEFAULT_DURATION_MINUTES)
    )
    interval_value = int(
        payload.get("start_time_interval_minutes", DEFAULT_START_INTERVAL_MINUTES)
    )

    if duration_value not in DURATION_OPTIONS:
        raise ValueError(
            "Meeting duration must be one of: "
            + ", ".join(map(str, DURATION_OPTIONS))
            + " minutes."
        )
    if interval_value not in START_INTERVAL_OPTIONS:
        raise ValueError(
            "Start-time interval must be one of: "
            + ", ".join(map(str, START_INTERVAL_OPTIONS))
            + " minutes."
        )

    participants = payload.get("participants")
    if not isinstance(participants, list) or not participants:
        raise ValueError("Saved setup must contain at least one person.")
    if len(participants) > 20:
        raise ValueError("Saved setup contains too many people. Maximum: 20.")

    loaded_people = []
    for idx, item in enumerate(participants, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Participant {idx} is invalid.")

        tz_name = str(item.get("time_zone", "UTC")).strip()
        ZoneInfo(tz_name)  # validates IANA zone name

        earliest = parse_preset_time(item.get("earliest", "09:00"))
        latest = parse_preset_time(item.get("latest", "17:00"))
        if minutes_of_day(latest) <= minutes_of_day(earliest):
            raise ValueError(
                f"Participant {idx}: latest time must be later than earliest time."
            )

        loaded_people.append(
            {
                "id": new_id(),
                "name": str(item.get("name", f"Participant {idx}")).strip()
                or f"Participant {idx}",
                "location": str(item.get("location", "")).strip(),
                "country_code": str(item.get("country_code", "")).upper(),
                "state": str(item.get("state", "")).strip(),
                "tz_name": tz_name,
                "earliest": earliest,
                "latest": latest,
            }
        )

    return meeting_date_value, duration_value, interval_value, loaded_people


def reset_defaults():
    """
    Start over while keeping the first participant.

    This removes every party member except the current top entry and resets
    meeting-level controls. The remaining participant's current country,
    time zone, and working-hour overrides are preserved.
    """
    current_people = st.session_state.get("people_v2", [])
    if current_people:
        st.session_state.people_v2 = [current_people[0]]
    else:
        st.session_state.people_v2 = [default_people()[0]]

    st.session_state.meeting_date = DEFAULT_MEETING_DATE
    st.session_state.duration_minutes = DEFAULT_DURATION_MINUTES
    st.session_state.start_interval_minutes = DEFAULT_START_INTERVAL_MINUTES
    st.session_state.search_horizon_hours = 120


# ---------- Session state ----------

if "people_v2" not in st.session_state:
    st.session_state.people_v2 = default_people()

if "meeting_date" not in st.session_state:
    st.session_state.meeting_date = DEFAULT_MEETING_DATE

if "duration_minutes" not in st.session_state:
    st.session_state.duration_minutes = DEFAULT_DURATION_MINUTES

if "start_interval_minutes" not in st.session_state:
    st.session_state.start_interval_minutes = DEFAULT_START_INTERVAL_MINUTES

if "search_horizon_hours" not in st.session_state:
    st.session_state.search_horizon_hours = 120


# ---------- Meeting settings ----------

# The planner automatically searches forward from the visitor's current date.
# No meeting date input is required for the normal workflow.
try:
    browser_timezone = st.context.timezone
except Exception:
    browser_timezone = None

if not browser_timezone or browser_timezone not in ALL_ZONES:
    browser_timezone = "UTC"

meeting_date = datetime.now(ZoneInfo(browser_timezone)).date()

with st.sidebar:
    st.markdown(
        """
        <div style="font-size:1.12rem;font-weight:700;color:#202226;margin:0.15rem 0 0.2rem 0;">
            Meeting setup
        </div>
        <div style="font-size:0.82rem;line-height:1.38;color:#5e646d;margin-bottom:0.45rem;">
            Choose the meeting length, search horizon, and who is joining. Time-zone changes are handled automatically.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            height:3px;
            width:100%;
            background:#ff66c4;
            border-radius:3px;
            margin:0.65rem 0 0.70rem 0;
        "></div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Upload & download / save")
    st.caption("Reuse the same people, time zones, and working hours later.")
    preset_file = st.file_uploader(
        "Import saved setup",
        type=["json"],
        key="preset_upload",
        help="Load a previously downloaded Global Meeting Planner JSON preset.",
    )

    setup_open_col, setup_save_col = st.columns(2)

    with setup_open_col:
        open_saved_setup = st.button(
            "Open setup",
            use_container_width=True,
            key="load_preset_button",
        )

    # Populated later after the participant editor has the current values.
    with setup_save_col:
        preset_download_slot = st.empty()

    if open_saved_setup:
        if preset_file is None:
            st.warning("Choose a saved setup file first.")
        elif preset_file.size > 100_000:
            st.error("Preset file is too large.")
        else:
            try:
                payload = json.loads(preset_file.getvalue().decode("utf-8"))
                loaded_date, loaded_duration, loaded_interval, loaded_people = (
                    load_preset_payload(payload)
                )
                st.session_state.people_v2 = loaded_people
                # The saved date is intentionally ignored in the simplified workflow.
                # Searches always begin from the visitor's current local date/time.
                st.session_state.duration_minutes = loaded_duration
                st.session_state.start_interval_minutes = loaded_interval
                st.rerun()
            except Exception as exc:
                st.error(f"Could not open saved setup: {exc}")

    st.divider()
    st.header("Meeting length")

    duration = st.selectbox(
        "Meeting length",
        options=DURATION_OPTIONS,
        key="duration_minutes",
        format_func=lambda x: {30: "30 minutes", 45: "45 minutes", 60: "1 hour", 90: "1.5 hours"}.get(x, f"{x} minutes"),
        help="Choose how long the meeting should be.",
    )

    search_horizon_hours = st.radio(
        "Find the best time within",
        options=[24, 48, 120],
        key="search_horizon_hours",
        horizontal=True,
        format_func=lambda hours: {
            24: "24 h",
            48: "48 h",
            120: "120 h · 5 days",
        }[hours],
        help="Choose how far ahead the planner should search for the highest-priority meeting times.",
    )

    st.caption(
        f"No date selection needed. The planner searches the next {search_horizon_hours} hours from now "
        "and ranks the highest-priority options."
    )

    with st.expander("Advanced settings", expanded=False):
        interval = st.selectbox(
            "Time increments",
            options=START_INTERVAL_OPTIONS,
            key="start_interval_minutes",
            format_func=lambda x: f"Every {x} minutes",
            help=(
                "How closely the planner checks possible start times. "
                "30 minutes is a good default for most meetings."
            ),
        )

    st.caption(
        "Your current selections stay available while the app is open. "
        "Use a saved setup if you want to reuse the same people and hours later."
    )

    st.markdown(
    """
    <div style="
        background-color:#fdebf7;
        border:1px solid #cd549e;
        border-left:5px solid #ff66c4;
        border-radius:8px;
        padding:12px 14px;
        color:#202226;
        font-size:0.82rem;
        line-height:1.45;
        margin-top:8px;
        margin-bottom:8px;
    ">
        <strong>Privacy:</strong> scheduling details are not written to an application database.
        A setup is saved only when you choose to download it.
    </div>
    """,
    unsafe_allow_html=True,
)

    st.divider()

    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=118)
        st.markdown("<div style='height:0.20rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="font-size:0.70rem;font-weight:700;letter-spacing:0.13em;
                    text-transform:uppercase;color:#202226;margin-top:0.15rem;">
            Drapalski Consulting LLC
        </div>
        <div style="font-size:0.78rem;line-height:1.45;color:#6b6f75;margin-top:0.2rem;">
            Practical tools for international finance, operations and decision-making.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- Participant editor ----------


joining_title_col, joining_help_col = st.columns([1.0, 2.8], gap="small")

with joining_title_col:
    st.subheader("Who’s joining?")

with joining_help_col:
    st.markdown(
        """
        <div class="joining-help">
            Add the people or teams joining the meeting and choose their country or area.
            For U.S. participants, choose the state too. Working hours default to 08:00–17:00
            local time. Use the override fields only when a participant is available outside
            those hours; the selected window directly drives the ranking and green availability.
        </div>
        """,
        unsafe_allow_html=True,
    )

people = st.session_state.people_v2

# One shared header row keeps the participant cards compact and avoids
# repeating the same field labels for every person.
h1, h2, h3, h4, h5 = st.columns([1.00, 1.15, 1.80, 0.72, 0.72])
for col, label in zip(
    [h1, h2, h3, h4, h5],
    ["Name", "Country / area + state", "Time zone", "Override from", "Override until"],
):
    with col:
        st.markdown(
            f'<div class="participant-header">{label}</div>',
            unsafe_allow_html=True,
        )

for index, person in enumerate(list(people)):
    pid = person["id"]

    with st.container(border=True):
        country_code = person.get("country_code", "")
        base_country_label = country_display_name(country_code)
        location_label = base_country_label
        if country_code == "US" and person.get("state"):
            location_label = f"{person['state']}, {base_country_label}"

        participant_name = person["name"] or f"Person {index + 1}"
        participant_meta = (
            f"{location_label} · "
            f"{friendly_zone_name(person['tz_name'])} · "
            f"{utc_offset_label(person['tz_name'], meeting_date)} on {meeting_date.strftime('%d %b %Y')}"
        )
        participant_region = f"UN M49 geography: {un_region_label(country_code)}"

        top_name, top_meta, top_remove = st.columns([1.55, 7.25, 0.18])

        with top_name:
            st.markdown(f"**{participant_name}**")

        with top_meta:
            st.markdown(
                f"""
                <div class="participant-meta">
                    {participant_meta}<br>
                    {participant_region}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with top_remove:
            if st.button(
                "×",
                key=f"remove_{pid}",
                use_container_width=False,
                help="Remove party",
            ):
                st.session_state.people_v2 = [p for p in people if p["id"] != pid]
                st.rerun()

        # Keep metadata visually separate from the editable controls.
        st.markdown("<div style='height:0.38rem;'></div>", unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns([1.00, 1.15, 1.80, 0.72, 0.72])

        with c1:
            person["name"] = st.text_input(
                "Name",
                value=person["name"],
                key=f"name_{pid}",
                label_visibility="collapsed",
            )

        with c2:
            current_country = infer_country_code(person)
            selected_country = st.selectbox(
                "Country / area",
                options=COUNTRY_CODES,
                index=COUNTRY_CODES.index(current_country),
                format_func=lambda code: country_display_name(code),
                key=f"country_{pid}",
                help="Choose the participant's country or area.",
                label_visibility="collapsed",
            )
            person["country_code"] = selected_country
            person["location"] = COUNTRY_NAMES[selected_country]

            if selected_country == "US":
                current_state = infer_us_state(person)
                person["state"] = st.selectbox(
                    "State",
                    options=US_STATES,
                    index=US_STATES.index(current_state),
                    key=f"state_{pid}_{selected_country}",
                    help="The state narrows the U.S. time-zone choices.",
                    label_visibility="collapsed",
                )
            else:
                person["state"] = ""

        with c3:
            if selected_country == "US":
                zone_options = [
                    z for z in US_STATE_ZONES.get(person["state"], ["America/New_York"])
                    if z in ALL_ZONES
                ]
            else:
                zone_options = COUNTRY_ZONES.get(selected_country, [])

            current_zone = person.get("tz_name", "")
            if current_zone not in zone_options:
                current_zone = zone_options[0] if zone_options else "UTC"

            if len(zone_options) == 1:
                person["tz_name"] = zone_options[0]
                st.text_input(
                    "Time zone",
                    value=zone_display(person["tz_name"], meeting_date),
                    key=f"tz_display_{pid}_{selected_country}_{person.get('state', '')}",
                    disabled=True,
                    help="Selected automatically from the country/state.",
                    label_visibility="collapsed",
                )
            else:
                person["tz_name"] = st.selectbox(
                    "Time zone",
                    options=zone_options,
                    index=zone_options.index(current_zone),
                    format_func=lambda z: zone_display(z, meeting_date),
                    key=f"tz_{pid}_{selected_country}_{person.get('state', '')}",
                    help="Only the time zones relevant to this country/state are shown.",
                    label_visibility="collapsed",
                )

        with c4:
            person["earliest"] = st.time_input(
                "Available from",
                value=person["earliest"],
                step=900,
                key=f"earliest_{pid}",
                help="Override this participant's default 08:00 working-hours start only when needed.",
                label_visibility="collapsed",
            )

        with c5:
            person["latest"] = st.time_input(
                "Available until",
                value=person["latest"],
                step=900,
                key=f"latest_{pid}",
                help="Override this participant's default 17:00 working-hours end only when needed.",
                label_visibility="collapsed",
            )


add_col, reset_col, spacer = st.columns([1.3, 1.3, 5])

with add_col:
    if st.button("＋ Add person", type="primary", use_container_width=True):
        st.session_state.people_v2.append(
            {
                "id": new_id(),
                "name": "New person",
                "location": COUNTRY_NAMES.get("DE", "Germany"),
                "country_code": "DE" if "DE" in COUNTRY_NAMES else COUNTRY_CODES[0],
                "state": "",
                "tz_name": "Europe/Berlin" if "Europe/Berlin" in ALL_ZONES else "UTC",
                "earliest": time(8, 0),
                "latest": time(17, 0),
            }
        )
        st.rerun()

with reset_col:
    st.button(
        "Start over",
        use_container_width=True,
        on_click=reset_defaults,
    )

people = st.session_state.people_v2

preset_payload = build_preset_payload(
    meeting_date=meeting_date,
    duration=duration,
    interval=interval,
    people=people,
)
preset_json = json.dumps(preset_payload, indent=2, ensure_ascii=False)

with preset_download_slot:
    st.download_button(
        "Save setup",
        data=preset_json,
        file_name=f"meeting_setup_{meeting_date.isoformat()}.json",
        mime="application/json",
        use_container_width=True,
        key="download_preset_button",
        help="Save the current people, hours, and meeting settings so you can reuse them later.",
    )

if not people:
    st.warning("Add at least one participant to calculate meeting times.")
    st.stop()

# Validate windows.
bad_windows = [
    p["name"] or "Unnamed participant"
    for p in people
    if minutes_of_day(p["latest"]) <= minutes_of_day(p["earliest"])
]
if bad_windows:
    st.error(
        "For this version, Latest must be later than Earliest on the same local day. "
        "Please fix: " + ", ".join(bad_windows)
    )
    st.stop()


# ---------- Offset summary ----------

offset_rows = []
for p in people:
    tz = ZoneInfo(p["tz_name"])
    sample = datetime.combine(meeting_date, time(12, 0), tzinfo=tz)
    offset_rows.append(
        {
            "Name": p["name"],
            "Country / area": country_display_name(p.get("country_code", "")),
            "State": p.get("state", "") if p.get("country_code") == "US" else "",
            "UN M49 geography": un_region_label(p.get("country_code", "")),
            "Time zone": p["tz_name"],
            "UTC offset on date": utc_offset_label(p["tz_name"], meeting_date),
            "Preferred hours": f"{p['earliest'].strftime('%H:%M')}–{p['latest'].strftime('%H:%M')}",
            "Zone abbreviation": sample.tzname(),
        }
    )

with st.expander("Time-zone details", expanded=False):
    st.dataframe(pd.DataFrame(offset_rows), use_container_width=True, hide_index=True)

# ---------- Global scheduling visualization ----------

st.subheader("World time view")

# Browser time zone was resolved above for the automatic search date.
reference_zone_options = []
for zone_name in [browser_timezone, *FAVORITE_ZONES, *ALL_ZONES]:
    if zone_name in ALL_ZONES and zone_name not in reference_zone_options:
        reference_zone_options.append(zone_name)

if (
    "map_reference_tz" not in st.session_state
    or st.session_state.map_reference_tz not in reference_zone_options
):
    st.session_state.map_reference_tz = browser_timezone

reference_col, control_col = st.columns([1.85, 1.15])

with reference_col:
    reference_tz = st.selectbox(
        "Reference time zone",
        options=reference_zone_options,
        key="map_reference_tz",
        format_func=lambda z: (
            f"{friendly_zone_name(z)} · {utc_offset_label(z, meeting_date)}"
            + (" · your browser" if z == browser_timezone else "")
        ),
        help=(
            "Defaults to the time zone reported by your browser/computer. "
            "You can override it here if needed."
        ),
    )

with control_col:
    map_hour = st.slider(
        "Proposed meeting time",
        min_value=0,
        max_value=23,
        value=12,
        step=1,
        format="%d:00",
        help="Choose the proposed meeting time in the reference time zone shown on the left. "
             "The app converts that instant to every participant’s local time.",
    )

reference_local = datetime.combine(
    meeting_date,
    time(map_hour, 0),
    tzinfo=ZoneInfo(reference_tz),
)
map_reference_utc = reference_local.astimezone(ZoneInfo("UTC"))


world_fig = go.Figure()

# Shade the night hemisphere for the proposed meeting instant.
add_day_night_overlay(world_fig, map_reference_utc)

for p in people:
    local_dt = map_reference_utc.astimezone(ZoneInfo(p["tz_name"]))
    status_label, status_color = local_status(p, local_dt)

    (lat, lon), approximate = approximate_map_coords(p, meeting_date)
    approx_text = " · approximate point" if approximate else ""

    world_fig.add_trace(
        go.Scattergeo(
            lat=[lat],
            lon=[lon],
            mode="markers+text",
            text=[p["name"]],
            textposition="top center",
            marker=dict(
                size=11,
                color=status_color,
                line=dict(color="#FFFFFF", width=1.4),
            ),
            showlegend=False,
            hovertemplate=(
                f"<b>{p['name']}</b><br>"
                f"{p['location']}<br>"
                f"Local time: {local_dt.strftime('%H:%M')}<br>"
                f"{status_label}<br>"
                f"{p['tz_name']} · {utc_offset_label(p['tz_name'], meeting_date)}"
                f"{approx_text}<extra></extra>"
            ),
        )
    )

world_fig.update_geos(
    projection_type="equal earth",
    showland=True,
    landcolor="#ececee",
    showocean=True,
    oceancolor="#fbfbfb",
    showcountries=True,
    countrycolor="#d4d4d7",
    coastlinecolor="#bfc1c5",
    coastlinewidth=0.65,
    showframe=False,
    bgcolor="rgba(0,0,0,0)",
)

world_fig.update_layout(
    height=330,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
)

st.plotly_chart(
    world_fig,
    use_container_width=True,
    config={"displayModeBar": False, "responsive": True},
)

reference_offset = utc_offset_label(reference_tz, meeting_date)

st.markdown(
    f"""
    <div style="
        font-size:0.78rem;
        line-height:1.55;
        color:#62656b;
        margin-top:-0.20rem;
        margin-bottom:0.45rem;
        padding:0.35rem 0.10rem 0.40rem 0.10rem;
        border-bottom:1px solid #eadde6;
    ">
        <strong>Proposed meeting:</strong>
        {reference_local.strftime('%H:%M')} in {friendly_zone_name(reference_tz)}
        ({reference_offset})
        · {map_reference_utc.strftime('%H:%M')} UTC
        <br>
        <span style="color:#A8C9AE;font-weight:700;">●</span> inside selected availability
        &nbsp;&nbsp;
        <span style="color:#F3D6E7;font-weight:700;">●</span> awake but outside availability
        &nbsp;&nbsp;
        <span style="color:#4A4A4A;font-weight:700;">●</span> 00:00–06:00 local sleep hours
        &nbsp;&nbsp;
        <span style="color:#555b63;font-weight:700;">◐</span> shaded map area = night
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("#### Availability across the day")

band_fig = go.Figure()

utc_anchor = datetime.combine(
    meeting_date,
    time(0, 0),
    tzinfo=ZoneInfo("UTC"),
)

# Numeric y positions give us enough control to place local-time labels and
# local-midnight day separators around each participant's availability bar.
for row_idx, p in enumerate(people):
    # Subtle alternating-day background on the row.
    tz = ZoneInfo(p["tz_name"])
    local_at_utc_start = utc_anchor.astimezone(tz)
    next_local_date = local_at_utc_start.date() + timedelta(days=1)
    next_midnight_local = datetime.combine(
        next_local_date,
        time(0, 0),
        tzinfo=tz,
    )
    next_midnight_utc = next_midnight_local.astimezone(ZoneInfo("UTC"))
    midnight_x = (next_midnight_utc - utc_anchor).total_seconds() / 3600

    if 0 < midnight_x < 24:
        # A light blended tint marks the portion belonging to the next local day.
        band_fig.add_shape(
            type="rect",
            x0=midnight_x,
            x1=24,
            y0=row_idx - 0.33,
            y1=row_idx + 0.33,
            xref="x",
            yref="y",
            fillcolor="rgba(205,84,158,0.035)",
            line=dict(width=0),
            layer="below",
        )
        band_fig.add_shape(
            type="line",
            x0=midnight_x,
            x1=midnight_x,
            y0=row_idx - 0.43,
            y1=row_idx + 0.43,
            xref="x",
            yref="y",
            line=dict(color="#8f949a", width=1, dash="dot"),
            layer="above",
        )
        band_fig.add_annotation(
            x=midnight_x + 0.08,
            y=row_idx - 0.48,
            text=next_local_date.strftime("%a"),
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(size=8, color="#6b6f75"),
        )

    # Availability / awake / sleep shading.
    for label, start_hour, width_hours in local_clock_segments_utc(p, meeting_date):
        band_fig.add_trace(
            go.Bar(
                y=[row_idx],
                x=[width_hours],
                base=[start_hour],
                width=0.46,
                orientation="h",
                marker=dict(
                    color=STATUS_COLORS[label],
                    line=dict(color="rgba(255,255,255,0.55)", width=0.5),
                ),
                name=label,
                showlegend=False,
                hovertemplate=(
                    f"<b>{p['name']}</b><br>"
                    f"{label}<br>"
                    f"{friendly_zone_name(p['tz_name'])} · "
                    f"{utc_offset_label(p['tz_name'], meeting_date)}"
                    "<extra></extra>"
                ),
            )
        )

    # Local clock labels every two UTC hours, placed just above each row.
    for utc_hour in range(0, 24, 2):
        local_dt = (utc_anchor + timedelta(hours=utc_hour)).astimezone(tz)
        band_fig.add_annotation(
            x=utc_hour,
            y=row_idx - 0.31,
            text=local_dt.strftime("%H:%M"),
            showarrow=False,
            xanchor="center",
            yanchor="middle",
            font=dict(size=8, color="#697f9f"),
        )

# Proposed meeting selection: display the full duration, not just a start line.
selected_utc_hour = (
    map_reference_utc.hour
    + map_reference_utc.minute / 60
    + map_reference_utc.second / 3600
)
meeting_width_hours = duration / 60
meeting_end_hour = selected_utc_hour + meeting_width_hours

def _add_meeting_window(x0, x1, annotation=False):
    kwargs = dict(
        x0=x0,
        x1=x1,
        fillcolor="rgba(17,17,17,0.055)",
        line=dict(color="#111111", width=2),
        layer="above",
    )
    if annotation:
        kwargs["annotation_text"] = (
            f"{reference_local.strftime('%H:%M')} "
            f"{reference_offset} · {duration} min"
        )
        kwargs["annotation_position"] = "top"
        kwargs["annotation_font"] = dict(size=9, color="#111111")
    band_fig.add_vrect(**kwargs)

if meeting_end_hour <= 24:
    _add_meeting_window(selected_utc_hour, meeting_end_hour, annotation=True)
else:
    _add_meeting_window(selected_utc_hour, 24, annotation=True)
    _add_meeting_window(0, meeting_end_hour - 24, annotation=False)

band_height = max(220, 92 + len(people) * 68)

band_fig.update_layout(
    barmode="overlay",
    height=band_height,
    margin=dict(l=5, r=5, t=24, b=28),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#fbfbfb",
    bargap=0.36,
    xaxis=dict(
        range=[0, 24],
        tickmode="array",
        tickvals=list(range(0, 25, 2)),
        ticktext=[f"{h:02d}" for h in range(0, 25, 2)],
        title="UTC reference",
        title_font=dict(size=9),
        tickfont=dict(size=8, color="#8a8f96"),
        gridcolor="#e8e7e8",
        gridwidth=1,
        zeroline=False,
        side="bottom",
    ),
    yaxis=dict(
        title="",
        tickmode="array",
        tickvals=list(range(len(people))),
        ticktext=[p["name"] for p in people],
        tickfont=dict(size=10),
        range=[len(people) - 0.35, -0.70],
        gridcolor="rgba(0,0,0,0)",
        zeroline=False,
    ),
    showlegend=False,
)

st.plotly_chart(
    band_fig,
    use_container_width=True,
    config={"displayModeBar": False, "responsive": True},
)

st.caption(
    "Local clock times are shown above each participant row in two-hour increments. "
    "The outlined panel is the proposed meeting window and its width reflects the selected meeting length. "
    "A dotted separator marks that participant’s local midnight and labels the next local day."
)



# ---------- Candidate calculation ----------

# Start at the next configured interval from the current moment.
now_utc = datetime.now(ZoneInfo("UTC")).replace(second=0, microsecond=0)
minute_remainder = now_utc.minute % interval
if minute_remainder:
    now_utc += timedelta(minutes=interval - minute_remainder)

anchor_utc = now_utc
candidate_rows = []

# Search the user-selected horizon automatically and rank the best options.
SEARCH_HORIZON_HOURS = int(search_horizon_hours)
steps = int((SEARCH_HORIZON_HOURS * 60) / interval)

for step in range(steps):
    start_utc = anchor_utc + timedelta(minutes=step * interval)
    end_utc = start_utc + timedelta(minutes=duration)

    row = {"UTC": start_utc}
    scores = []
    preferred_count = 0
    worst_score = 100

    for p in people:
        tz = ZoneInfo(p["tz_name"])
        local_start = start_utc.astimezone(tz)
        local_end = end_utc.astimezone(tz)

        score_detail = score_local_detailed(
            local_start,
            local_end,
            p["earliest"],
            p["latest"],
            country_code=p.get("country_code"),
            subdivision=p.get("state"),
        )
        score = score_detail.total_score
        status = score_detail.status

        scores.append(score)
        worst_score = min(worst_score, score)

        if status == "Preferred":
            preferred_count += 1

        row[p["id"]] = local_start
        row[p["id"] + "_status"] = status
        row[p["id"] + "_score"] = score
        row[p["id"] + "_score_detail"] = score_detail.as_dict()

    meeting_score = aggregate_meeting_score(scores)

    row["Average score"] = meeting_score.average_participant_score
    row["Worst-person score"] = meeting_score.worst_participant_score
    row["Fairness score"] = meeting_score.fairness_score
    row["Preferred count"] = preferred_count
    row["Overall score"] = meeting_score.overall_score

    candidate_rows.append(row)

results = pd.DataFrame(candidate_rows).sort_values(
    ["Overall score", "Preferred count", "Average score", "UTC"],
    ascending=[False, False, False, True],
).reset_index(drop=True)


# ---------- Best times ----------

st.subheader("Best meeting times")
st.caption(scoring_methodology_summary())

top_n = st.slider("How many options to show", 3, 10, 4)

for rank, (_, row) in enumerate(results.head(top_n).iterrows(), start=1):
    with st.container(border=True):
        heading, metric = st.columns([4, 1])

        with heading:
            st.markdown(f"#### #{rank} — Score {row['Overall score']:.0f}/100")

        with metric:
            st.metric("Preferred", f"{int(row['Preferred count'])}/{len(people)}")

        cols = st.columns(len(people))

        for col, p in zip(cols, people):
            local = row[p["id"]]
            status = row[p["id"] + "_status"]

            with col:
                st.markdown(f"**{p['name']}**")
                st.write(local.strftime("%a %d %b %Y"))
                st.write(local.strftime("%H:%M"))
                st.caption(
                    f"{p['location']} · {local.tzname()} · "
                    f"{utc_offset_label(p['tz_name'], local.date())} · {status}"
                )


# ---------- Email-ready proposal ----------

with st.expander("Email-ready proposal · top 3", expanded=False):

    def proposal_short_label(person):
        """Short readable label for email proposals."""
        country_code = person.get("country_code", "")
        tz_name = person.get("tz_name", "")

        if country_code == "US":
            if tz_name == "America/Los_Angeles":
                return "US West"
            if tz_name in ("America/Denver", "America/Boise"):
                return "US Mountain"
            if tz_name == "America/Chicago":
                return "US Central"
            if tz_name in ("America/New_York", "America/Detroit", "America/Indiana/Indianapolis"):
                return "US East"
            return "US"

        if country_code == "DE":
            return "Germany"

        if country_code == "TW" or tz_name == "Asia/Taipei":
            return "Taipei"

        country_name = COUNTRY_NAMES.get(country_code, "").strip()
        if country_name:
            return country_name

        fallback = person.get("name", "Participant").strip()
        if fallback.lower().endswith(" team"):
            fallback = fallback[:-5]
        return fallback

    proposal_lines = [
        "Hi all,",
        "",
        (
            "Looking at everyone's calendars, here are three options for the next "
            + ("24 hours" if search_horizon_hours == 24
               else "48 hours" if search_horizon_hours == 48
               else "5 days")
            + ":"
        ),
    ]

    for proposal_rank, (_, proposal_row) in enumerate(results.head(3).iterrows(), start=1):
        proposal_utc = proposal_row["UTC"]
        if hasattr(proposal_utc, "to_pydatetime"):
            proposal_utc = proposal_utc.to_pydatetime()

        user_local = proposal_utc.astimezone(ZoneInfo(browser_timezone))
        reference_date = user_local.date()
        option_parts = []

        for p in people:
            participant_local = proposal_row[p["id"]]
            if hasattr(participant_local, "to_pydatetime"):
                participant_local = participant_local.to_pydatetime()

            label = proposal_short_label(p)
            offset_text = utc_offset_label(
                p["tz_name"],
                participant_local.date(),
            )

            day_delta = (participant_local.date() - reference_date).days
            if day_delta == -1:
                day_note = ", previous day"
            elif day_delta == 1:
                day_note = ", next day"
            elif day_delta < -1:
                day_note = f", {abs(day_delta)} days earlier"
            elif day_delta > 1:
                day_note = f", {day_delta} days later"
            else:
                day_note = ""

            option_parts.append(
                f"{label} {participant_local.strftime('%a %d %b %H:%M')} "
                f"({offset_text}{day_note})"
            )

        proposal_lines.append(
            f"{proposal_rank}. {user_local.strftime('%a %d %b')} — "
            + " / ".join(option_parts)
        )

    proposal_lines.extend(
        [
            "",
            "Please let me know which works best and I'll send the invite.",
            "",
            "Best regards,",
        ]
    )

    email_proposal_text = "\n".join(proposal_lines)

    st.caption(
        "Use the copy icon in the top-right corner of the text box to copy this directly into an email."
    )
    st.code(email_proposal_text, language="text", wrap_lines=True)


# ---------- UTC timeline ----------

with st.expander("Full 24-hour comparison", expanded=False):
    timeline_rows = []
    for hour in range(24):
        utc_dt = anchor_utc + timedelta(hours=hour)
        timeline_row = {"UTC": utc_dt.strftime("%a %H:%M")}

        for p in people:
            local = utc_dt.astimezone(ZoneInfo(p["tz_name"]))
            timeline_score = score_local_detailed(
                local,
                local + timedelta(minutes=duration),
                p["earliest"],
                p["latest"],
                country_code=p.get("country_code"),
                subdivision=p.get("state"),
            )
            status = timeline_score.status
            timeline_row[p["name"]] = (
                f"{local.strftime('%a %H:%M')} · "
                f"{utc_offset_label(p['tz_name'], local.date())} · {status}"
            )

        timeline_rows.append(timeline_row)

    st.dataframe(
        pd.DataFrame(timeline_rows),
        use_container_width=True,
        hide_index=True,
    )


st.markdown(
    """
    <div class="dc-footer">
        <strong>DRAPALSKI CONSULTING LLC</strong><br>
        Global Meeting Planner · Designed for professional use with clients and business partners.<br>
        Time-zone calculations use the IANA tz database and automatically account for DST.<br>
        Scheduling inputs are not intentionally persisted to a server-side database by this application.<br>
        Built by Drapalski Consulting LLC · Comments / feedback:
        <a href="https://www.drapal.ski" target="_blank" style="text-decoration:none;">www.drapal.ski</a>
    </div>
    """,
    unsafe_allow_html=True,
)
