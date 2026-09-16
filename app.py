import streamlit as st
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo, available_timezones
import pandas as pd
import plotly.graph_objects as go
import uuid
import json
import importlib.resources as resources

from pathlib import Path

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
            padding-top: 0.45rem !important;
            padding-bottom: 0.65rem !important;
            padding-left: 0.45rem !important;
            padding-right: 0.45rem !important;
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
                width: 205px !important;
                min-width: 205px !important;
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
            width: 218px !important;
            min-width: 218px !important;
        }

        section[data-testid="stSidebar"] > div {
            width: 218px !important;
            min-width: 218px !important;
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


def score_local(local_start: datetime, local_end: datetime, earliest: time, latest: time):
    """Score a proposed local meeting against a person's preferred window."""
    s = minutes_of_day(local_start.time())
    e = minutes_of_day(local_end.time())
    pref_start = minutes_of_day(earliest)
    pref_end = minutes_of_day(latest)

    # Simple same-day preferred-window model.
    fully_inside = (
        local_start.date() == local_end.date()
        and pref_start <= s
        and e <= pref_end
    )

    if fully_inside:
        center = (pref_start + pref_end) / 2
        meeting_center = (s + e) / 2
        half = max((pref_end - pref_start) / 2, 60)
        comfort = 100 - 20 * abs(meeting_center - center) / half
        return max(80, min(100, comfort)), "Preferred"

    # Distance to the preferred window using meeting start/end.
    if e < pref_start:
        delta = pref_start - e
    elif s > pref_end:
        delta = s - pref_end
    else:
        # Partly overlaps the preferred window.
        return 70, "Possible"

    if delta <= 60:
        return 60, "Possible"
    if delta <= 120:
        return 40, "Difficult"
    if delta <= 240:
        return 20, "Very difficult"
    return 0, "Unreasonable"


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
    "Business hours": "#A8C9AE",
    "Shoulder hours": "#8F3548",
    "Sleep hours": "#E8B47A",
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


def local_status(local_dt: datetime):
    """Map-status convention: green 09–17, orange 00–06, pink otherwise."""
    local_hour = local_dt.hour + local_dt.minute / 60
    if 9 <= local_hour < 17:
        return "Business hours", STATUS_COLORS["Business hours"]
    if 0 <= local_hour < 6:
        return "Sleep hours", STATUS_COLORS["Sleep hours"]
    return "Shoulder hours", STATUS_COLORS["Shoulder hours"]


def local_clock_segments_utc(person: dict, ref_date: date):
    """Map a person's local business/sleep/other windows onto one UTC day."""
    tz = ZoneInfo(person["tz_name"])
    utc_anchor = datetime.combine(ref_date, time(0, 0), tzinfo=ZoneInfo("UTC"))

    local_windows = [
        ("Sleep hours", time(0, 0), time(6, 0), 0),
        ("Shoulder hours", time(6, 0), time(9, 0), 0),
        ("Business hours", time(9, 0), time(17, 0), 0),
        ("Shoulder hours", time(17, 0), time(0, 0), 1),
    ]

    output = []
    for label, start_t, end_t, end_day_offset in local_windows:
        local_start = datetime.combine(ref_date, start_t, tzinfo=tz)
        local_end = datetime.combine(
            ref_date + timedelta(days=end_day_offset),
            end_t,
            tzinfo=tz,
        )

        utc_start = local_start.astimezone(ZoneInfo("UTC"))
        utc_end = local_end.astimezone(ZoneInfo("UTC"))
        duration_h = (utc_end - utc_start).total_seconds() / 3600
        start_h = ((utc_start - utc_anchor).total_seconds() / 3600) % 24
        finish_h = start_h + duration_h

        if finish_h <= 24:
            output.append((label, start_h, duration_h))
        else:
            output.append((label, start_h, 24 - start_h))
            output.append((label, 0, finish_h - 24))

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
            "earliest": time(7, 0),
            "latest": time(23, 0),
        },
        {
            "id": new_id(),
            "name": "U.S. team",
            "location": "United States",
            "country_code": "US",
            "state": "Oregon",
            "tz_name": "America/Los_Angeles",
            "earliest": time(9, 0),
            "latest": time(17, 0),
        },
        {
            "id": new_id(),
            "name": "Taipei team",
            "location": "Taiwan",
            "country_code": "TW",
            "tz_name": "Asia/Taipei",
            "earliest": time(8, 0),
            "latest": time(18, 0),
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
    """Reset meeting settings and participants."""
    st.session_state.people_v2 = default_people()
    st.session_state.meeting_date = DEFAULT_MEETING_DATE
    st.session_state.duration_minutes = DEFAULT_DURATION_MINUTES
    st.session_state.start_interval_minutes = DEFAULT_START_INTERVAL_MINUTES


# ---------- Session state ----------

if "people_v2" not in st.session_state:
    st.session_state.people_v2 = default_people()

if "meeting_date" not in st.session_state:
    st.session_state.meeting_date = DEFAULT_MEETING_DATE

if "duration_minutes" not in st.session_state:
    st.session_state.duration_minutes = DEFAULT_DURATION_MINUTES

if "start_interval_minutes" not in st.session_state:
    st.session_state.start_interval_minutes = DEFAULT_START_INTERVAL_MINUTES


# ---------- Meeting settings ----------

with st.sidebar:
    st.markdown(
        """
        <div style="font-size:1.12rem;font-weight:700;color:#202226;margin:0.15rem 0 0.2rem 0;">
            Meeting setup
        </div>
        <div style="font-size:0.82rem;line-height:1.38;color:#5e646d;margin-bottom:0.45rem;">
            Set the date, meeting length, and who is joining. Time-zone changes are handled automatically.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Saved meeting setups")
    st.caption("Reuse the same people, time zones, and working hours later.")
    preset_file = st.file_uploader(
        "Import saved setup",
        type=["json"],
        key="preset_upload",
        help="Load a previously downloaded Global Meeting Planner JSON preset.",
    )

    if st.button(
        "Open saved setup",
        use_container_width=True,
        key="load_preset_button",
    ):
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
                st.session_state.meeting_date = loaded_date
                st.session_state.duration_minutes = loaded_duration
                st.session_state.start_interval_minutes = loaded_interval
                st.rerun()
            except Exception as exc:
                st.error(f"Could not open saved setup: {exc}")

    # Populated later after the participant editor has the current values.
    preset_download_slot = st.empty()

    st.divider()
    st.header("Meeting details")

    meeting_date = st.date_input(
        "Meeting date",
        key="meeting_date",
        help="UTC offsets are calculated for this exact date.",
    )

    duration = st.selectbox(
        "Meeting length",
        options=DURATION_OPTIONS,
        key="duration_minutes",
        format_func=lambda x: {30: "30 minutes", 45: "45 minutes", 60: "1 hour", 90: "1.5 hours"}.get(x, f"{x} minutes"),
        help="Choose how long the meeting should be.",
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


st.subheader("Who’s joining?")
st.write(
    "Add the people or teams joining the meeting and choose their country or area. "
    "For U.S. participants, choose the state too. The correct time-zone choices update automatically."
)

people = st.session_state.people_v2

for index, person in enumerate(list(people)):
    pid = person["id"]

    with st.container(border=True):
        top_left, top_right = st.columns([9, 1])

        with top_left:
            st.markdown(f"**{person['name'] or f'Person {index + 1}'}**")

        with top_right:
            if st.button("Remove", key=f"remove_{pid}", use_container_width=True):
                st.session_state.people_v2 = [p for p in people if p["id"] != pid]
                st.rerun()

        c1, c2, c3, c4, c5 = st.columns([1.05, 1.20, 1.85, 0.90, 0.90])

        with c1:
            person["name"] = st.text_input(
                "Name",
                value=person["name"],
                key=f"name_{pid}",
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
                )
            else:
                person["tz_name"] = st.selectbox(
                    "Time zone",
                    options=zone_options,
                    index=zone_options.index(current_zone),
                    format_func=lambda z: zone_display(z, meeting_date),
                    key=f"tz_{pid}_{selected_country}_{person.get('state', '')}",
                    help="Only the time zones relevant to this country/state are shown.",
                )

        with c4:
            person["earliest"] = st.time_input(
                "Available from",
                value=person["earliest"],
                step=900,
                key=f"earliest_{pid}",
            )

        with c5:
            person["latest"] = st.time_input(
                "Available until",
                value=person["latest"],
                step=900,
                key=f"latest_{pid}",
            )

        country_code = person.get("country_code", "")
        base_country_label = country_display_name(country_code)
        location_label = base_country_label
        if country_code == "US" and person.get("state"):
            location_label = f"{person['state']}, {base_country_label}"

        st.caption(
            f"{location_label} · "
            f"{friendly_zone_name(person['tz_name'])} · "
            f"{utc_offset_label(person['tz_name'], meeting_date)} on {meeting_date.strftime('%d %b %Y')}"
        )
        st.caption(
            f"UN M49 geography: {un_region_label(country_code)}"
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
                "earliest": time(9, 0),
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
        "Save this setup",
        data=preset_json,
        file_name=f"meeting_setup_{meeting_date.isoformat()}.json",
        mime="application/json",
        use_container_width=True,
        help="Save the current people, hours, date, and meeting settings so you can reuse them later.",
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

# Use the visitor's browser/computer time zone as the default reference.
# Streamlit exposes this directly through st.context.timezone.
try:
    browser_timezone = st.context.timezone
except Exception:
    browser_timezone = None

if not browser_timezone or browser_timezone not in ALL_ZONES:
    browser_timezone = "UTC"

reference_zone_options = []
for zone_name in [browser_timezone, *FAVORITE_ZONES, *ALL_ZONES]:
    if zone_name in ALL_ZONES and zone_name not in reference_zone_options:
        reference_zone_options.append(zone_name)

if (
    "map_reference_tz" not in st.session_state
    or st.session_state.map_reference_tz not in reference_zone_options
):
    st.session_state.map_reference_tz = browser_timezone

control_col, reference_col = st.columns([1.15, 1.85])

with control_col:
    map_hour = st.slider(
        "Explore a local hour",
        min_value=0,
        max_value=23,
        value=12,
        step=1,
        format="%d:00",
        help="Choose an hour in the reference time zone. The app converts it to UTC automatically.",
    )

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

reference_local = datetime.combine(
    meeting_date,
    time(map_hour, 0),
    tzinfo=ZoneInfo(reference_tz),
)
map_reference_utc = reference_local.astimezone(ZoneInfo("UTC"))

st.markdown(
    f"""
    <div style="font-size:0.78rem;line-height:1.45;color:#62656b;margin-top:-0.20rem;margin-bottom:0.15rem;">
        <strong>Reference:</strong>
        {friendly_zone_name(reference_tz)} · {reference_local.strftime('%H:%M')} local ·
        {map_reference_utc.strftime('%H:%M')} UTC
        {" · detected from your browser" if reference_tz == browser_timezone else " · manually selected"}
        &nbsp;&nbsp;&nbsp;
        <span style="color:#4f9b63;font-weight:700;">● Green</span> 09–17 local &nbsp;&nbsp;
        <span style="color:#cd549e;font-weight:700;">● Pink</span> 06–09 / 17–24 &nbsp;&nbsp;
        <span style="color:#e59a45;font-weight:700;">● Orange</span> 00–06
    </div>
    """,
    unsafe_allow_html=True,
)

world_fig = go.Figure()

for p in people:
    local_dt = map_reference_utc.astimezone(ZoneInfo(p["tz_name"]))
    status_label, status_color = local_status(local_dt)

    center_lon = utc_offset_hours(p["tz_name"], meeting_date) * 15
    while center_lon > 180:
        center_lon -= 360
    while center_lon < -180:
        center_lon += 360

    add_timezone_band(world_fig, center_lon, status_color)

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

for status_label, display_name in [
    ("Business hours", "Business · 09–17"),
    ("Shoulder hours", "Other awake · 06–09 / 17–24"),
    ("Sleep hours", "Sleep · 00–06"),
]:
    world_fig.add_trace(
        go.Scattergeo(
            lat=[None],
            lon=[None],
            mode="markers",
            marker=dict(size=9, color=STATUS_COLORS[status_label]),
            name=display_name,
            hoverinfo="skip",
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
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.01,
        xanchor="left",
        x=0,
        font=dict(size=10, color="#4f5358"),
    ),
)

st.plotly_chart(
    world_fig,
    use_container_width=True,
    config={"displayModeBar": False, "responsive": True},
)

st.markdown("#### Local-day status bands · UTC")

band_fig = go.Figure()
legend_seen = set()

for p in people:
    for label, start_hour, width_hours in local_clock_segments_utc(p, meeting_date):
        show_legend = label not in legend_seen
        legend_seen.add(label)

        band_fig.add_trace(
            go.Bar(
                y=[p["name"]],
                x=[width_hours],
                base=[start_hour],
                orientation="h",
                marker=dict(
                    color=STATUS_COLORS[label],
                    line=dict(color="#FFFFFF", width=0.5),
                ),
                name=label,
                legendgroup=label,
                showlegend=show_legend,
                hovertemplate=(
                    f"<b>{p['name']}</b><br>"
                    f"{label}<br>"
                    f"{p['tz_name']} · {utc_offset_label(p['tz_name'], meeting_date)}"
                    "<extra></extra>"
                ),
            )
        )

band_fig.update_layout(
    barmode="overlay",
    height=max(180, 70 + len(people) * 36),
    margin=dict(l=5, r=5, t=0, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#fbfbfb",
    xaxis=dict(
        range=[0, 24],
        tickmode="array",
        tickvals=list(range(0, 25, 3)),
        ticktext=[f"{h:02d}" for h in range(0, 25, 3)],
        title="UTC",
        title_font=dict(size=10),
        tickfont=dict(size=9),
        gridcolor="#e5e4e5",
        zeroline=False,
    ),
    yaxis=dict(
        title="",
        categoryorder="array",
        categoryarray=[p["name"] for p in people[::-1]],
        gridcolor="rgba(0,0,0,0)",
        tickfont=dict(size=10),
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.01,
        xanchor="left",
        x=0,
        font=dict(size=9, color="#4f5358"),
    ),
)

st.plotly_chart(
    band_fig,
    use_container_width=True,
    config={"displayModeBar": False, "responsive": True},
)

st.caption(
    "The selected hour is interpreted in the reference time zone above, then converted through UTC "
    "to each participant’s local time. Equal Earth projection. Green = 09:00–17:00 local; "
    "orange = 00:00–06:00 local; pink = remaining hours. "
    "Map bands are scheduling guides, not legal timezone borders."
)


# ---------- Candidate calculation ----------

anchor_utc = datetime.combine(meeting_date, time(0, 0), tzinfo=ZoneInfo("UTC"))
candidate_rows = []

# Search 48 hours so the planner can surface cross-date compromises.
steps = int((48 * 60) / interval)

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

        score, status = score_local(
            local_start,
            local_end,
            p["earliest"],
            p["latest"],
        )

        scores.append(score)
        worst_score = min(worst_score, score)

        if status == "Preferred":
            preferred_count += 1

        row[p["id"]] = local_start
        row[p["id"] + "_status"] = status
        row[p["id"] + "_score"] = score

    average_score = sum(scores) / len(scores)
    overall_score = 0.65 * average_score + 0.35 * worst_score

    row["Average score"] = round(average_score, 1)
    row["Worst-person score"] = worst_score
    row["Preferred count"] = preferred_count
    row["Overall score"] = round(overall_score, 1)

    candidate_rows.append(row)

results = pd.DataFrame(candidate_rows).sort_values(
    ["Overall score", "Preferred count", "Average score"],
    ascending=[False, False, False],
).reset_index(drop=True)


# ---------- Best times ----------

st.subheader("Best meeting times")
st.caption("The planner ranks options by how comfortably they fit everyone’s selected local availability.")

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


# ---------- UTC timeline ----------

with st.expander("Full 24-hour comparison", expanded=False):
    timeline_rows = []
    for hour in range(24):
        utc_dt = anchor_utc + timedelta(hours=hour)
        timeline_row = {"UTC": utc_dt.strftime("%a %H:%M")}

        for p in people:
            local = utc_dt.astimezone(ZoneInfo(p["tz_name"]))
            _, status = score_local(
                local,
                local + timedelta(minutes=duration),
                p["earliest"],
                p["latest"],
            )
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
