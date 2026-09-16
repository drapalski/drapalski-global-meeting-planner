# Global Meeting Planner

**A Drapalski Consulting tool for coordinating international teams across time zones, working hours, local availability, public holidays, and scheduling norms.**

Global Meeting Planner helps international teams identify practical meeting times without repeatedly converting time zones by hand. It combines participant-selected availability, date-specific UTC offsets, daylight-saving rules, local-time visualization, public-holiday calendars, and a transparent composite meeting score in one browser-based workflow.

![Global Meeting Planner preview](assets/preview.png)

## What it does

- Compares local working hours across countries and time zones
- Applies date-specific daylight-saving changes automatically using IANA time-zone data
- Uses the visitor's browser time zone as the default meeting reference
- Narrows U.S. time-zone choices by state
- Lets each participant define their own local availability window
- Visualizes each participant's local time across a shared UTC timeline
- Shows local-day transitions and proposed meeting windows
- Checks supported country and subdivision public-holiday calendars
- Applies documented local workweek / scheduling-norm profiles where configured
- Ranks candidate meeting times using a deterministic composite score
- Saves and reloads portable meeting setups as JSON files
- Shows ISO alpha-3 country codes and UN M49 geographic context

## Why we built it

International work creates small coordination frictions that compound across teams. A meeting involving Europe, North America, and Asia should not require repeated manual UTC calculations, spreadsheet checks, or guesswork about who is being asked to join at an inconvenient local time.

This tool turns those calculations into a visual planning workflow while keeping the scoring methodology separate, reviewable, and adjustable.

## Live application

**Open the Global Meeting Planner:**  
https://drapalski-meeting-planner.streamlit.app/

## Meeting scoring model

Meeting recommendations are generated using a deterministic composite scheduling model maintained separately in [`meeting_scoring.py`](meeting_scoring.py).

The current participant-level score evaluates:

| Component | Weight |
| --- | ---: |
| Participant-selected availability | 30% |
| Business-hours fit | 20% |
| Human convenience | 20% |
| Local workweek / scheduling norms | 15% |
| Public-holiday calendar | 15% |

The model also applies explicit caps for materially inconvenient conditions, including meetings that fall outside a participant's selected availability, overlap sleep hours, fall in configured non-working periods, or occur on a detected public holiday.

The meeting-level score currently combines:

```text
65% × average participant score
+ 35% × lowest participant score
```

The scoring engine returns a detailed breakdown for each participant so that individual components, penalties, caps, holiday checks, and local-norm assumptions can be reviewed independently.

### Local norms

Local-norm profiles are jurisdiction-level scheduling references, not assumptions about an individual's religion, culture, or personal preferences.

Profiles are kept in `meeting_scoring.py` with fields for:

- working weekdays
- reference business hours
- lunch windows
- confidence
- source
- scope
- last-reviewed date

Participant-selected availability remains the strongest direct user input.

### Public holidays

Public-holiday checks use the Python [`holidays`](https://pypi.org/project/holidays/) package for supported countries and subdivisions. Holiday data is evaluated in each participant's local date.

Manual overrides can also be added in `meeting_scoring.py` for corrections or organization-specific closures.

## Architecture

The application and scoring methodology are intentionally separated:

```text
app.py
    Streamlit interface
    participant inputs
    time-zone calculations
    maps and timeline visualization
    ranked meeting-time display
        |
        | imports
        v
meeting_scoring.py
    composite scoring policy
    participant score components
    local-norm profiles
    holiday calendar logic
    penalties and hard caps
    meeting-level aggregation
```

This keeps the user interface easier to maintain while allowing the scoring model to evolve independently as new scheduling research, country-specific information, and practical experience are collected.

## About Drapalski Consulting

**Drapalski Consulting LLC** provides structured financial leadership, governance, analytics, and cross-border advisory support to businesses operating in complex environments.

Website: [www.drapal.ski](https://www.drapal.ski)

## Technology

Built with:

- Python
- Streamlit
- Plotly
- pandas
- IANA time-zone data via `tzdata`
- `holidays` for supported public-holiday calendars

## Privacy

Scheduling information is not intentionally written by the application to its own persistent database. Current selections live in the active Streamlit session. A reusable setup is persisted only when the user chooses to download a JSON setup file.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Repository structure

```text
.
├── .github/
│   └── workflows/
│       └── python-check.yml
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── drapalski_logo.png
│   └── preview.png
├── .gitignore
├── app.py
├── meeting_scoring.py
├── LICENSE.md
├── README.md
├── requirements.txt
└── sample_preset.json
```

## Methodology development

The scoring model is intentionally versioned and reviewable. Future refinements may include:

- additional sourced country / jurisdiction scheduling profiles
- recurring-meeting burden rotation
- organization-specific working calendars
- meeting-type weighting
- client / host priority
- historical acceptance patterns
- calendar-density penalties
- additional public-holiday and subdivision handling
- a future fairness component that rewards more balanced inconvenience across participants

New rules should be added only when they can be expressed as a transparent component, penalty, cap, or hard constraint with a clear rationale and, where relevant, a documented source.

## Use and rights

Copyright © 2026 Drapalski Consulting LLC. All rights reserved. See `LICENSE.md`.
