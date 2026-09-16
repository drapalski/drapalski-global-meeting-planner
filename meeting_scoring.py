"""
meeting_scoring.py
==================

Standalone deterministic scoring engine for the Drapalski Global Meeting Planner.

The Streamlit user interface belongs in app.py.
All scoring assumptions belong here.

DESIGN GOALS
------------
1. Transparent: every score is decomposed into named components.
2. Deterministic: same inputs + same model version = same result.
3. User-led: explicit participant availability is the strongest input.
4. Extensible: local-norm profiles and holiday calendars are separate layers.
5. Sourceable: country-level local-norm overrides carry source and review notes.
6. Conservative: never infer an individual's religion or personal preferences
   from nationality. Country profiles are only workweek/calendar reference norms.

PUBLIC-HOLIDAY DATA
-------------------
When the optional `holidays` package is installed, this module generates
government-designated holidays locally by ISO country code and, where supported,
subdivision. No live API call is required.

Recommended dependency:
    holidays==0.104
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, replace
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from statistics import mean
from typing import Dict, Iterable, List, Optional, Tuple

try:
    import holidays as holidays_lib
    HOLIDAYS_AVAILABLE = True
except ImportError:
    holidays_lib = None
    HOLIDAYS_AVAILABLE = False


SCORING_MODEL_VERSION = "2026.09-v2"
DAY_MINUTES = 24 * 60


# =====================================================================
# 1. MODEL POLICY
# =====================================================================

@dataclass(frozen=True)
class ScoringPolicy:
    """
    Participant-level composite.

    Default weights:
        30% Explicit availability
        20% Business-hours fit
        20% Human convenience
        15% Local norms / customary workweek
        15% Public-holiday calendar

    Severe conflicts also receive explicit caps after weighting.
    """

    business_start: time = time(8, 0)
    business_end: time = time(17, 0)

    coffee_end: time = time(9, 0)
    lunch_start: time = time(11, 30)
    lunch_end: time = time(13, 30)
    preferred_afternoon_end: time = time(16, 0)
    sleep_start: time = time(0, 0)
    sleep_end: time = time(6, 0)

    # Python weekday: Monday=0 ... Sunday=6.
    working_weekdays: Tuple[int, ...] = (0, 1, 2, 3, 4)

    # Workweek-transition low-priority period.
    # Mon-Fri profile => Fri 20:00 through Mon 09:00.
    # Sun-Thu profile => Thu 20:00 through Sun 09:00.
    weekend_transition_start: time = time(20, 0)
    weekend_transition_end: time = time(9, 0)

    weight_availability: float = 0.30
    weight_business_hours: float = 0.20
    weight_human_convenience: float = 0.20
    weight_local_norms: float = 0.15
    weight_holiday_calendar: float = 0.15

    cap_partial_availability: float = 75.0
    cap_outside_availability: float = 55.0
    cap_sleep_overlap: float = 30.0
    cap_local_nonwork_period: float = 45.0
    cap_public_holiday: float = 20.0

    # Meeting-level aggregation remains compatible with the existing app.
    aggregate_average_weight: float = 0.65
    aggregate_worst_weight: float = 0.35

    # Available for future testing but intentionally 0 for now.
    aggregate_fairness_weight: float = 0.00


DEFAULT_POLICY = ScoringPolicy()


# =====================================================================
# 2. LOCAL NORMS / "CULTURAL" REFERENCE PROFILES
# =====================================================================

@dataclass(frozen=True)
class LocalNormsProfile:
    """
    Country/jurisdiction scheduling reference.

    This is intentionally separate from a person's explicit availability.

    confidence:
        1.00 = strong general reference
        <1.0 = narrower or sector-specific evidence; effect is blended toward
               neutral to avoid over-generalizing.
    """

    working_weekdays: Tuple[int, ...]
    business_start: Optional[time] = None
    business_end: Optional[time] = None
    lunch_start: Optional[time] = None
    lunch_end: Optional[time] = None

    confidence: float = 1.0
    note: str = ""
    source_url: str = ""
    source_scope: str = ""
    last_reviewed: str = ""


# Keep these narrow, documented, and reviewable.
LOCAL_NORMS_PROFILES: Dict[str, LocalNormsProfile] = {
    "AE": LocalNormsProfile(
        working_weekdays=(0, 1, 2, 3, 4),  # Mon-Fri
        confidence=1.0,
        note="UAE government/semi-government Monday-Friday reference.",
        source_url="https://u.ae/en/about-the-uae/fact-sheet",
        source_scope="government and semi-government reference",
        last_reviewed="2026-09-16",
    ),
    "SA": LocalNormsProfile(
        working_weekdays=(6, 0, 1, 2, 3),  # Sun-Thu
        business_start=time(7, 30),
        business_end=time(14, 30),
        confidence=0.80,
        note=(
            "Saudi government reference: Sunday-Thursday working days. "
            "Private-sector schedules can differ, so the profile is deliberately "
            "below full confidence."
        ),
        source_url=(
            "https://www.hrsd.gov.sa/sites/default/files/2020-05/"
            "Implementing%20Regulation%20for%20Human%20Resources%20in%20the%20Civil%20Service.pdf"
        ),
        source_scope="government reference",
        last_reviewed="2026-09-16",
    ),
}

# Future sourced profile template:
#
# "XX": LocalNormsProfile(
#     working_weekdays=(...),
#     business_start=time(...),
#     business_end=time(...),
#     lunch_start=time(...),
#     lunch_end=time(...),
#     confidence=0.90,
#     note="What this profile represents and what it does NOT claim.",
#     source_url="...",
#     source_scope="...",
#     last_reviewed="YYYY-MM-DD",
# )


# =====================================================================
# 3. HOLIDAY OVERRIDES / SUBDIVISIONS
# =====================================================================

# Optional manual corrections or organization-specific closures.
MANUAL_HOLIDAY_OVERRIDES: Dict[Tuple[str, date], str] = {}

US_STATE_TO_CODE = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT",
    "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL",
    "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}


# =====================================================================
# 4. AUDITABLE OUTPUT
# =====================================================================

@dataclass
class ParticipantScoreBreakdown:
    total_score: float
    status: str

    availability_score: float
    business_hours_score: float
    human_convenience_score: float
    local_norms_score: float
    holiday_calendar_score: float

    weighted_before_caps: float
    applied_caps: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    country_code: Optional[str] = None
    subdivision: Optional[str] = None
    local_norms_profile_used: str = "generic"
    local_norms_confidence: float = 1.0

    selected_availability_overlap_ratio: float = 0.0
    sleep_overlap_minutes: int = 0
    low_priority_local_period: bool = False

    holiday_detected: bool = False
    holiday_name: Optional[str] = None
    holiday_data_available: bool = False

    model_version: str = SCORING_MODEL_VERSION

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class MeetingScoreBreakdown:
    overall_score: float
    average_participant_score: float
    worst_participant_score: float
    fairness_score: float
    participant_scores: List[float]
    model_version: str = SCORING_MODEL_VERSION

    def as_dict(self) -> dict:
        return asdict(self)


# =====================================================================
# 5. HELPERS
# =====================================================================

def minutes_of_day(t: time) -> int:
    return t.hour * 60 + t.minute


def _duration_minutes(start: datetime, end: datetime) -> int:
    return max(1, int((end - start).total_seconds() // 60))


def _continuous_window(start_t: time, end_t: time) -> Tuple[int, int]:
    start = minutes_of_day(start_t)
    end = minutes_of_day(end_t)
    if end <= start:
        end += DAY_MINUTES
    return start, end


def _continuous_meeting(
    local_start: datetime,
    local_end: datetime,
    window_start: Optional[int] = None,
    window_end: Optional[int] = None,
) -> Tuple[int, int]:
    start = minutes_of_day(local_start.time())
    duration = _duration_minutes(local_start, local_end)
    end = start + duration

    if (
        window_start is not None
        and window_end is not None
        and window_end > DAY_MINUTES
        and start < window_start
    ):
        start += DAY_MINUTES
        end = start + duration

    return start, end


def _overlap_minutes(a0: int, a1: int, b0: int, b1: int) -> int:
    return max(0, min(a1, b1) - max(a0, b0))


def _bounded_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return max(0.0, min(1.0, numerator / denominator))


def _country_profile(
    country_code: Optional[str],
    base: ScoringPolicy,
) -> Tuple[ScoringPolicy, Optional[LocalNormsProfile], str]:
    if not country_code:
        return base, None, "generic"

    code = country_code.upper()
    profile = LOCAL_NORMS_PROFILES.get(code)
    if profile is None:
        return base, None, "generic"

    effective = replace(
        base,
        working_weekdays=profile.working_weekdays,
        business_start=profile.business_start or base.business_start,
        business_end=profile.business_end or base.business_end,
        lunch_start=profile.lunch_start or base.lunch_start,
        lunch_end=profile.lunch_end or base.lunch_end,
    )
    return effective, profile, code


def _subdivision_code(country_code: Optional[str], subdivision: Optional[str]) -> Optional[str]:
    if not country_code or not subdivision:
        return None

    if country_code.upper() == "US":
        return US_STATE_TO_CODE.get(subdivision, subdivision)

    return subdivision


@lru_cache(maxsize=1024)
def _holiday_calendar(
    country_code: str,
    subdivision_code: Optional[str],
    year: int,
):
    if not HOLIDAYS_AVAILABLE:
        return None

    try:
        return holidays_lib.country_holidays(
            country_code,
            subdiv=subdivision_code,
            years=year,
            observed=True,
            language="en_US",
        )
    except Exception:
        try:
            return holidays_lib.country_holidays(
                country_code,
                years=year,
                observed=True,
                language="en_US",
            )
        except Exception:
            return None


# =====================================================================
# 6. COMPONENT 1 — USER-SELECTED AVAILABILITY (30%)
# =====================================================================

def _availability_component(
    local_start: datetime,
    local_end: datetime,
    earliest: time,
    latest: time,
) -> Tuple[float, float, List[str]]:
    pref_start, pref_end = _continuous_window(earliest, latest)
    start, end = _continuous_meeting(local_start, local_end, pref_start, pref_end)
    duration = max(1, end - start)

    overlap = _overlap_minutes(start, end, pref_start, pref_end)
    ratio = _bounded_ratio(overlap, duration)

    if ratio >= 0.999:
        return 100.0, 1.0, [
            "Meeting is fully inside the participant's selected availability."
        ]

    if ratio > 0:
        return 30.0 + 60.0 * ratio, ratio, [
            f"Meeting overlaps {ratio:.0%} of selected availability."
        ]

    return 0.0, 0.0, [
        "Meeting is completely outside selected availability."
    ]


# =====================================================================
# 7. COMPONENT 2 — BUSINESS-HOURS FIT (20%)
# =====================================================================

def _business_hours_component(
    local_start: datetime,
    local_end: datetime,
    policy: ScoringPolicy,
) -> Tuple[float, List[str]]:
    start = minutes_of_day(local_start.time())
    duration = _duration_minutes(local_start, local_end)
    end = start + duration

    business_start = minutes_of_day(policy.business_start)
    business_end = minutes_of_day(policy.business_end)

    overlap = _overlap_minutes(start, end, business_start, business_end)
    ratio = _bounded_ratio(overlap, duration)

    if ratio >= 0.999:
        return 100.0, ["Meeting is fully inside reference business hours."]

    if ratio > 0:
        return 45.0 + 45.0 * ratio, [
            f"Meeting overlaps {ratio:.0%} of reference business hours."
        ]

    midpoint = (start + duration / 2) % DAY_MINUTES

    if midpoint < business_start:
        minutes_early = business_start - midpoint
        return max(20.0, 60.0 - minutes_early / 6), [
            "Meeting is before reference business hours."
        ]

    minutes_late = midpoint - business_end
    return max(20.0, 60.0 - minutes_late / 6), [
        "Meeting is after reference business hours."
    ]


# =====================================================================
# 8. COMPONENT 3 — HUMAN CONVENIENCE (20%)
# =====================================================================

def _human_convenience_component(
    local_start: datetime,
    local_end: datetime,
    policy: ScoringPolicy,
) -> Tuple[float, int, List[str]]:
    """
    Convenience preferences:
      - avoid first work hour when possible,
      - prefer 09:00-11:30 and 13:30-16:00,
      - reduce ranking across lunch,
      - taper toward end of workday,
      - treat 00:00-06:00 as sleep,
      - prefer edges of sleep window over its middle.
    """
    start = minutes_of_day(local_start.time())
    duration = _duration_minutes(local_start, local_end)
    end = start + duration

    business_start = minutes_of_day(policy.business_start)
    coffee_end = minutes_of_day(policy.coffee_end)
    lunch_start = minutes_of_day(policy.lunch_start)
    lunch_end = minutes_of_day(policy.lunch_end)
    afternoon_end = minutes_of_day(policy.preferred_afternoon_end)
    business_end = minutes_of_day(policy.business_end)
    sleep_start = minutes_of_day(policy.sleep_start)
    sleep_end = minutes_of_day(policy.sleep_end)

    sleep_overlap = _overlap_minutes(start, end, sleep_start, sleep_end)

    if sleep_overlap > 0:
        midpoint = (start + duration / 2) % DAY_MINUTES
        edge_distance = min(abs(midpoint - sleep_start), abs(sleep_end - midpoint))
        max_distance = max(1, (sleep_end - sleep_start) / 2)
        edge_preference = 1.0 - _bounded_ratio(edge_distance, max_distance)
        return 5.0 + 30.0 * edge_preference, sleep_overlap, [
            f"Meeting overlaps sleep by {sleep_overlap} minutes; sleep-window edges "
            "score better than the middle of the night."
        ]

    if coffee_end <= start and end <= lunch_start:
        return 100.0, 0, ["Inside preferred morning convenience window."]

    if lunch_end <= start and end <= afternoon_end:
        return 100.0, 0, ["Inside preferred afternoon convenience window."]

    lunch_overlap = _overlap_minutes(start, end, lunch_start, lunch_end)
    if lunch_overlap > 0:
        lunch_ratio = _bounded_ratio(lunch_overlap, duration)
        return 82.0 - 22.0 * lunch_ratio, 0, [
            f"Meeting overlaps lunch by {lunch_overlap} minutes."
        ]

    if business_start <= start < coffee_end:
        progress = _bounded_ratio(
            start - business_start,
            max(1, coffee_end - business_start),
        )
        return 82.0 + 12.0 * progress, 0, [
            "Early workday; later starts score better to allow start-of-day routines."
        ]

    if start >= afternoon_end and end <= business_end:
        late = max(0, end - afternoon_end)
        span = max(1, business_end - afternoon_end)
        return 94.0 - 12.0 * _bounded_ratio(late, span), 0, [
            "Late workday; convenience declines toward end of day."
        ]

    midpoint = (start + duration / 2) % DAY_MINUTES

    if sleep_end <= midpoint < business_start:
        progress = _bounded_ratio(
            midpoint - sleep_end,
            max(1, business_start - sleep_end),
        )
        return 40.0 + 30.0 * progress, 0, [
            "Early morning outside normal business hours."
        ]

    if business_end <= midpoint < DAY_MINUTES:
        hours_after = (midpoint - business_end) / 60
        return max(28.0, 66.0 - 6.0 * hours_after), 0, [
            "Evening outside normal business hours."
        ]

    return 75.0, 0, ["Neutral human-convenience period."]


# =====================================================================
# 9. COMPONENT 4 — LOCAL NORMS / CULTURAL CALENDAR (15%)
# =====================================================================

def _low_priority_local_period(
    local_start: datetime,
    local_end: datetime,
    policy: ScoringPolicy,
) -> bool:
    """
    Derive low-priority weekend transition from the configured workweek.

    Mon-Fri:
        Fri 20:00 -> Mon 09:00

    Sun-Thu:
        Thu 20:00 -> Sun 09:00
    """
    working = tuple(sorted(set(policy.working_weekdays)))
    if not working:
        return False

    first_workday = working[0]
    last_workday = working[-1]

    def low(dt: datetime) -> bool:
        wd = dt.weekday()
        minute = minutes_of_day(dt.time())

        if wd not in working:
            return True

        if wd == last_workday and minute >= minutes_of_day(policy.weekend_transition_start):
            return True

        if wd == first_workday and minute < minutes_of_day(policy.weekend_transition_end):
            return True

        return False

    probe = local_start
    while probe < local_end:
        if low(probe):
            return True
        probe += timedelta(minutes=15)

    if local_end > local_start:
        return low(local_end - timedelta(minutes=1))

    return low(local_start)


def _local_norms_component(
    local_start: datetime,
    local_end: datetime,
    policy: ScoringPolicy,
    profile: Optional[LocalNormsProfile],
) -> Tuple[float, bool, List[str]]:
    low_period = _low_priority_local_period(local_start, local_end, policy)

    raw = 25.0 if low_period else 100.0
    confidence = profile.confidence if profile else 1.0

    # Lower-confidence profiles are blended toward neutral.
    score = 100.0 - confidence * (100.0 - raw)

    if profile:
        profile_note = (
            f"Local-norm profile ({profile.source_scope or 'country reference'}, "
            f"confidence {profile.confidence:.0%}): {profile.note}"
        )
    else:
        profile_note = (
            "Generic Mon-Fri workweek baseline used because no sourced country "
            "override is configured."
        )

    if low_period:
        return score, True, [
            profile_note,
            "Meeting falls in the configured non-working/weekend transition."
        ]

    return score, False, [
        profile_note,
        "Meeting falls in a configured working-day period."
    ]


# =====================================================================
# 10. COMPONENT 5 — PUBLIC HOLIDAYS (15%)
# =====================================================================

def _holiday_component(
    local_start: datetime,
    local_end: datetime,
    country_code: Optional[str],
    subdivision: Optional[str],
) -> Tuple[float, bool, Optional[str], bool, List[str]]:
    if not country_code:
        return 100.0, False, None, False, [
            "No country code supplied; holiday component left neutral."
        ]

    code = country_code.upper()
    dates_to_check = {local_start.date(), local_end.date()}

    for d in dates_to_check:
        manual = MANUAL_HOLIDAY_OVERRIDES.get((code, d))
        if manual:
            return 0.0, True, manual, True, [
                f"Manual holiday override detected: {manual}."
            ]

    if not HOLIDAYS_AVAILABLE:
        return 100.0, False, None, False, [
            "Python 'holidays' package is not installed; holiday component left neutral."
        ]

    subdiv_code = _subdivision_code(code, subdivision)

    for year in {d.year for d in dates_to_check}:
        cal = _holiday_calendar(code, subdiv_code, year)
        if cal is None:
            return 100.0, False, None, False, [
                f"No holiday calendar could be resolved for {code}; component left neutral."
            ]

        for d in dates_to_check:
            if d.year == year and d in cal:
                name = str(cal.get(d))
                return 0.0, True, name, True, [
                    f"Public holiday detected for {code}: {name} ({d.isoformat()})."
                ]

    return 100.0, False, None, True, [
        f"No public holiday detected for {code} on the proposed local date."
    ]


# =====================================================================
# 11. PARTICIPANT COMPOSITE
# =====================================================================

def score_local_detailed(
    local_start: datetime,
    local_end: datetime,
    earliest: time,
    latest: time,
    *,
    country_code: Optional[str] = None,
    subdivision: Optional[str] = None,
    policy: ScoringPolicy = DEFAULT_POLICY,
) -> ParticipantScoreBreakdown:
    effective, profile, profile_key = _country_profile(country_code, policy)

    weight_sum = (
        effective.weight_availability
        + effective.weight_business_hours
        + effective.weight_human_convenience
        + effective.weight_local_norms
        + effective.weight_holiday_calendar
    )
    if abs(weight_sum - 1.0) > 1e-9:
        raise ValueError(
            f"Participant component weights must sum to 1.0, got {weight_sum:.4f}"
        )

    availability, availability_ratio, notes_a = _availability_component(
        local_start, local_end, earliest, latest
    )
    business, notes_b = _business_hours_component(
        local_start, local_end, effective
    )
    human, sleep_overlap, notes_h = _human_convenience_component(
        local_start, local_end, effective
    )
    local_norms, low_local_period, notes_n = _local_norms_component(
        local_start, local_end, effective, profile
    )
    holiday, holiday_hit, holiday_name, holiday_data, notes_c = _holiday_component(
        local_start, local_end, country_code, subdivision
    )

    weighted = (
        availability * effective.weight_availability
        + business * effective.weight_business_hours
        + human * effective.weight_human_convenience
        + local_norms * effective.weight_local_norms
        + holiday * effective.weight_holiday_calendar
    )

    score = weighted
    caps: Dict[str, float] = {}

    if 0 < availability_ratio < 1:
        caps["partial_selected_availability"] = effective.cap_partial_availability
        score = min(score, effective.cap_partial_availability)

    if availability_ratio == 0:
        caps["outside_selected_availability"] = effective.cap_outside_availability
        score = min(score, effective.cap_outside_availability)

    if sleep_overlap > 0:
        caps["sleep_overlap"] = effective.cap_sleep_overlap
        score = min(score, effective.cap_sleep_overlap)

    if low_local_period:
        caps["local_nonwork_period"] = effective.cap_local_nonwork_period
        score = min(score, effective.cap_local_nonwork_period)

    if holiday_hit:
        caps["public_holiday"] = effective.cap_public_holiday
        score = min(score, effective.cap_public_holiday)

    score = round(max(0.0, min(100.0, score)), 1)

    if score >= 85:
        status = "Preferred"
    elif score >= 70:
        status = "Good"
    elif score >= 50:
        status = "Possible"
    elif score >= 30:
        status = "Difficult"
    elif score >= 15:
        status = "Very difficult"
    else:
        status = "Last resort"

    notes = notes_a + notes_b + notes_h + notes_n + notes_c
    if caps:
        notes.append(
            "Applied cap(s): "
            + ", ".join(f"{name} <= {value:g}" for name, value in caps.items())
        )

    return ParticipantScoreBreakdown(
        total_score=score,
        status=status,
        availability_score=round(availability, 1),
        business_hours_score=round(business, 1),
        human_convenience_score=round(human, 1),
        local_norms_score=round(local_norms, 1),
        holiday_calendar_score=round(holiday, 1),
        weighted_before_caps=round(weighted, 1),
        applied_caps=caps,
        notes=notes,
        country_code=country_code,
        subdivision=subdivision,
        local_norms_profile_used=profile_key,
        local_norms_confidence=profile.confidence if profile else 1.0,
        selected_availability_overlap_ratio=round(availability_ratio, 4),
        sleep_overlap_minutes=int(sleep_overlap),
        low_priority_local_period=low_local_period,
        holiday_detected=holiday_hit,
        holiday_name=holiday_name,
        holiday_data_available=holiday_data,
    )


def score_local(
    local_start: datetime,
    local_end: datetime,
    earliest: time,
    latest: time,
    *,
    country_code: Optional[str] = None,
    subdivision: Optional[str] = None,
    policy: ScoringPolicy = DEFAULT_POLICY,
) -> Tuple[float, str]:
    result = score_local_detailed(
        local_start,
        local_end,
        earliest,
        latest,
        country_code=country_code,
        subdivision=subdivision,
        policy=policy,
    )
    return result.total_score, result.status


# =====================================================================
# 12. MEETING-LEVEL COMPOSITE
# =====================================================================

def aggregate_meeting_score(
    participant_scores: Iterable[float],
    *,
    policy: ScoringPolicy = DEFAULT_POLICY,
) -> MeetingScoreBreakdown:
    scores = [float(s) for s in participant_scores]
    if not scores:
        raise ValueError("At least one participant score is required.")

    avg = mean(scores)
    worst = min(scores)
    best = max(scores)

    # Useful future metric: balanced burden across participants.
    fairness = max(0.0, 100.0 - (best - worst))

    total_weight = (
        policy.aggregate_average_weight
        + policy.aggregate_worst_weight
        + policy.aggregate_fairness_weight
    )
    if total_weight <= 0:
        raise ValueError("Meeting aggregation weights must sum to > 0.")

    overall = (
        avg * policy.aggregate_average_weight
        + worst * policy.aggregate_worst_weight
        + fairness * policy.aggregate_fairness_weight
    ) / total_weight

    return MeetingScoreBreakdown(
        overall_score=round(overall, 1),
        average_participant_score=round(avg, 1),
        worst_participant_score=round(worst, 1),
        fairness_score=round(fairness, 1),
        participant_scores=[round(s, 1) for s in scores],
    )


# =====================================================================
# 13. UI / README DESCRIPTION
# =====================================================================

def scoring_methodology_summary() -> str:
    holiday_text = (
        "Public holidays are included from the installed country/subdivision holiday calendar."
        if HOLIDAYS_AVAILABLE
        else "Public-holiday scoring is neutral until the optional holidays package is installed."
    )

    return (
        f"Composite scoring model {SCORING_MODEL_VERSION}: "
        "30% selected availability, 20% business-hours fit, 20% human convenience, "
        "15% local workweek/norms, and 15% public-holiday calendar. "
        "Hard caps apply to meetings outside availability, during sleep, in configured "
        "non-working periods, or on public holidays. "
        "Overall meeting ranking = 65% participant average + 35% lowest participant score. "
        + holiday_text
    )


# =====================================================================
# 14. SELF-REVIEW
# =====================================================================

if __name__ == "__main__":
    start = datetime(2026, 9, 16, 10, 0)
    end = start + timedelta(hours=1)

    example = score_local_detailed(
        start,
        end,
        earliest=time(8, 0),
        latest=time(17, 0),
        country_code="DE",
    )

    print("Scoring model:", SCORING_MODEL_VERSION)
    print("Total:", example.total_score, example.status)
    print("Availability:", example.availability_score)
    print("Business hours:", example.business_hours_score)
    print("Human convenience:", example.human_convenience_score)
    print("Local norms:", example.local_norms_score)
    print("Holiday calendar:", example.holiday_calendar_score)
    print("Before caps:", example.weighted_before_caps)
    print("Caps:", example.applied_caps or "None")
    print("Notes:")
    for note in example.notes:
        print(" -", note)
