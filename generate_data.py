"""Generate and validate a fully simulated clinic wait-time analytics dataset.

All outputs are synthetic and contain no real patient or clinic data.
Run from the repository root: python generate_data.py
"""
from __future__ import annotations

from pathlib import Path
import math
import sys

# Supports a project-local dependency install when the base Python runtime is minimal.
LOCAL_PACKAGES = Path(__file__).resolve().parent / ".python_packages"
if LOCAL_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_PACKAGES))

import numpy as np
import pandas as pd


SEED = 20260913
ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
REPORTS = ROOT / "reports"

LOCATIONS = {
    "Central City": {"base_daily": 55, "providers": 3, "support": 5, "pressure": 1.22},
    "Northside": {"base_daily": 40, "providers": 3, "support": 4, "pressure": 1.05},
    "Lakeside": {"base_daily": 32, "providers": 3, "support": 3, "pressure": 0.91},
    "West End": {"base_daily": 36, "providers": 2, "support": 3, "pressure": 1.13},
}
SERVICES = {
    "Primary Care": {"share": 0.38, "mean": 18, "sd": 5},
    "Follow-up": {"share": 0.27, "mean": 13, "sd": 4},
    "Vaccination": {"share": 0.16, "mean": 9, "sd": 3},
    "Chronic Care": {"share": 0.12, "mean": 28, "sd": 7},
    "Minor Procedure": {"share": 0.07, "mean": 38, "sd": 10},
}


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def build_staff_shifts(dates: pd.DatetimeIndex, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for location, profile in LOCATIONS.items():
        for date in dates:
            if date.weekday() == 6:
                continue
            # Saturday operates a shorter, deliberately leaner shift.
            for p in range(profile["providers"]):
                start_hour = 8 if p < max(1, profile["providers"] - 1) else 9
                end_hour = 17 if date.weekday() < 5 else 13
                # West End's staggered provider start leaves a morning constraint.
                if location == "West End" and p >= 2:
                    start_hour += 1
                rows.append({
                    "staff_id": f"{location[:2].upper()}-PR-{p+1:02d}", "role": "Provider",
                    "shift_start": date + pd.Timedelta(hours=start_hour),
                    "shift_end": date + pd.Timedelta(hours=end_hour), "clinic_location": location,
                })
            for s in range(profile["support"]):
                rows.append({
                    "staff_id": f"{location[:2].upper()}-SU-{s+1:02d}", "role": "Support",
                    "shift_start": date + pd.Timedelta(hours=8),
                    "shift_end": date + pd.Timedelta(hours=(17 if date.weekday() < 5 else 13)),
                    "clinic_location": location,
                })
    return pd.DataFrame(rows).sort_values(["clinic_location", "shift_start", "staff_id"])


def scheduled_minutes(rng: np.random.Generator, location: str, weekday: int) -> int:
    # Discrete demand waves: late morning and after-work peak; Central has strongest wave.
    slots = np.arange(8 * 60, (17 if weekday < 5 else 13) * 60, 10)
    hour = slots / 60
    weights = 0.55 + 1.4 * np.exp(-((hour - 10.5) / 1.25) ** 2) + 1.15 * np.exp(-((hour - 15.5) / 1.3) ** 2)
    if location == "Central City":
        weights += 0.65 * np.exp(-((hour - 16.0) / 0.8) ** 2)
    if location == "West End":
        weights += 0.7 * np.exp(-((hour - 9.0) / 0.7) ** 2)
    return int(rng.choice(slots, p=weights / weights.sum()))


def generate_appointments(dates: pd.DatetimeIndex, shifts: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    records = []
    service_names = list(SERVICES)
    service_probs = [v["share"] for v in SERVICES.values()]
    appointment_number = 0
    for location, profile in LOCATIONS.items():
        for date in dates:
            if date.weekday() == 6:
                continue
            weekday_factor = 1.17 if date.weekday() == 0 else (0.72 if date.weekday() == 5 else 1.0)
            season_factor = 1.08 if date.month in (2, 3) else (0.93 if date.month == 6 else 1.0)
            count = rng.poisson(profile["base_daily"] * weekday_factor * season_factor)
            for _ in range(count):
                appointment_number += 1
                scheduled = date + pd.Timedelta(minutes=scheduled_minutes(rng, location, date.weekday()))
                service = str(rng.choice(service_names, p=service_probs))
                early_slot = scheduled.hour < 9
                no_show_p = 0.042 + (0.050 if early_slot else 0) + (0.027 if date.weekday() == 0 else 0)
                cancelled = rng.random() < (0.035 + (0.012 if date.weekday() == 0 else 0))
                no_show = (not cancelled) and rng.random() < no_show_p
                # Arrivals are centered modestly early; later arrivals are more common during peak traffic.
                late_bias = 3.0 if scheduled.hour in (9, 16) else 0.0
                arrival_offset = float(np.clip(rng.normal(-4 + late_bias, 10), -32, 45))
                arrival = pd.NaT if (cancelled or no_show) else scheduled + pd.Timedelta(minutes=round(arrival_offset))
                records.append({
                    "appointment_id": f"APT-{appointment_number:06d}", "clinic_location": location,
                    "appointment_date": date.date().isoformat(), "service_type": service,
                    "scheduled_time": scheduled, "arrival_time": arrival,
                    "cancelled": cancelled, "no_show": no_show,
                })
    appts = pd.DataFrame(records)
    appts["appointment_date"] = pd.to_datetime(appts["appointment_date"])

    # Queue simulation: actual arrivals compete for on-shift provider capacity.
    output = []
    for (location, date), day in appts.groupby(["clinic_location", "appointment_date"], sort=False):
        provider_shifts = shifts[(shifts.clinic_location == location) & (shifts.shift_start.dt.date == date.date()) & (shifts.role == "Provider")]
        availability = [(row.shift_start, row.staff_id, row.shift_end) for row in provider_shifts.itertuples()]
        active = day[~day.cancelled & ~day.no_show].sort_values("arrival_time")
        for idx, appt in active.iterrows():
            service = SERVICES[appt.service_type]
            duration = max(5, float(rng.normal(service["mean"], service["sd"])))
            # Small overrun multiplier captures room/admin friction under demand pressure.
            duration *= LOCATIONS[location]["pressure"]
            options = [(max(free_at, appt.arrival_time), staff, shift_end, pos)
                       for pos, (free_at, staff, shift_end) in enumerate(availability)]
            candidate_start, staff, shift_end, pos = min(options, key=lambda x: x[0])
            prospective_wait = max(0.0, (candidate_start - appt.arrival_time).total_seconds() / 60)
            late_minutes = max(0.0, (appt.arrival_time - appt.scheduled_time).total_seconds() / 60)
            # Gradual walkout response: low at short waits, rising through prolonged waits;
            # late arrivals experience a small extra likelihood of leaving.
            walkout_p = 0.006 + 0.39 * sigmoid((prospective_wait - 42) / 15) + 0.025 * sigmoid((late_minutes - 18) / 7)
            walked_out = rng.random() < min(walkout_p, 0.72)
            if walked_out:
                output.append((idx, pd.NaT, pd.NaT, None, None, True))
                continue
            end = candidate_start + pd.Timedelta(minutes=round(duration))
            availability[pos] = (end, staff, shift_end)
            output.append((idx, candidate_start, end, staff, "Provider", False))
        for idx, appt in day[day.cancelled | day.no_show].iterrows():
            output.append((idx, pd.NaT, pd.NaT, None, None, False))
    timeline = pd.DataFrame(output, columns=["index", "service_start_time", "service_end_time", "staff_id", "role", "walked_out"]).set_index("index")
    appts = appts.join(timeline)
    appts["completed"] = ~(appts.cancelled | appts.no_show | appts.walked_out)
    appts["satisfaction_score"] = np.nan
    completed = appts.completed
    waits = (appts.loc[completed, "service_start_time"] - appts.loc[completed, "arrival_time"]).dt.total_seconds() / 60
    noise = rng.normal(0, 0.55, completed.sum())
    appts.loc[completed, "satisfaction_score"] = np.clip(np.rint(4.9 - 0.034 * waits + noise), 1, 5)
    appts["complaint_flag"] = False
    appts.loc[completed, "complaint_flag"] = rng.random(completed.sum()) < np.clip(0.025 + waits.to_numpy() / 235, 0.02, 0.55)
    appts["complaint_flag"] = appts["complaint_flag"].astype("boolean")
    return appts.sort_values("appointment_id").reset_index(drop=True)


def validation_report(raw: pd.DataFrame, cleaned: pd.DataFrame, shifts: pd.DataFrame) -> str:
    nulls = raw.isna().sum().to_frame("null_count").to_markdown()
    dtypes = raw.dtypes.astype(str).to_frame("dtype").to_markdown()
    completed = cleaned[cleaned.completed]
    wait = completed.wait_minutes
    duration = completed.service_duration_minutes
    walkout_rate = raw.walked_out.mean() * 100
    arrival_offset = (raw.loc[raw.arrival_time.notna(), "arrival_time"] - raw.loc[raw.arrival_time.notna(), "scheduled_time"]).dt.total_seconds() / 60
    assigned = completed.merge(shifts, on=["staff_id", "clinic_location"], suffixes=("", "_shift"))
    assigned = assigned[(assigned.shift_start.dt.date == assigned.appointment_date.dt.date)]
    in_shift = ((assigned.service_start_time >= assigned.shift_start) & (assigned.service_start_time <= assigned.shift_end)).mean() * 100
    return f"""# Validation Report — Simulated Data

**Scope:** Synthetic clinic operations data generated with seed `{SEED}`. No real clinic, patient, or staff data is represented.

## Output counts

| Dataset | Rows |
|---|---:|
| Raw appointments | {len(raw):,} |
| Cleaned appointments | {len(cleaned):,} |
| Staff shifts | {len(shifts):,} |
| Completed appointments | {int(raw.completed.sum()):,} |

## Null counts — raw appointments

{nulls}

Expected nulls occur for arrivals and service timestamps of cancelled/no-show appointments, and service/staff fields for walkouts. Feedback is collected only after completed visits.

## Data types — raw appointments

{dtypes}

## Time and range sanity checks

- Appointment dates range from **{raw.appointment_date.min().date()}** to **{raw.appointment_date.max().date()}**.
- Scheduled times range from **{raw.scheduled_time.min()}** to **{raw.scheduled_time.max()}**; clinics operate Monday–Saturday only.
- Negative waits among completed visits: **{int((wait < 0).sum())}** (expected 0).
- Service end at/before service start among completed visits: **{int((completed.service_end_time <= completed.service_start_time).sum())}** (expected 0).
- Arrival offsets for attended appointments: median **{arrival_offset.median():.1f} min**, 1st–99th percentile **{arrival_offset.quantile(.01):.1f} to {arrival_offset.quantile(.99):.1f} min**; all are within the configured -32 to +45 minute envelope.
- Staff-shift consistency: **{in_shift:.1f}%** of completed visits start within their assigned provider shift. The remainder are simulated overtime caused by queue carryover; no visit is assigned to a different clinic.

## Plausibility checks

| Measure (completed visits unless noted) | Result |
|---|---:|
| Mean wait | {wait.mean():.1f} min |
| Median / 90th-percentile wait | {wait.median():.1f} / {wait.quantile(.90):.1f} min |
| Mean service duration | {duration.mean():.1f} min |
| Service-duration 1st–99th percentile | {duration.quantile(.01):.1f}–{duration.quantile(.99):.1f} min |
| Walkout rate (all appointments) | {walkout_rate:.1f}% |
| No-show rate (not cancelled) | {(raw.no_show.sum() / (~raw.cancelled).sum() * 100):.1f}% |
| Complaint rate (completed) | {completed.complaint_flag.mean() * 100:.1f}% |

## Known simulation limitations

This is simulated data, not a forecast or a representation of a real clinic. The model uses a provider-queue abstraction and does not model rooms, clinician specialty matching, insurance, emergencies, rescheduling, or individual patient behavior. Staffing is planned at the shift level; unplanned absences and real-time breaks are not simulated. Causal patterns are intentionally encoded for analysis practice and should not be interpreted as measured effects.
"""


def main() -> None:
    for path in (RAW, CLEAN, REPORTS, ROOT / "sql", ROOT / "notebooks", ROOT / "dashboard", ROOT / "images"):
        path.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    dates = pd.date_range("2026-01-01", "2026-06-30", freq="D")
    shifts = build_staff_shifts(dates, rng)
    raw = generate_appointments(dates, shifts, rng)
    cleaned = raw.copy()
    cleaned["wait_minutes"] = (cleaned.service_start_time - cleaned.arrival_time).dt.total_seconds() / 60
    cleaned["service_duration_minutes"] = (cleaned.service_end_time - cleaned.service_start_time).dt.total_seconds() / 60
    cleaned["arrival_offset_minutes"] = (cleaned.arrival_time - cleaned.scheduled_time).dt.total_seconds() / 60
    cleaned["outcome"] = np.select(
        [cleaned.completed, cleaned.walked_out, cleaned.no_show, cleaned.cancelled],
        ["completed", "walked_out", "no_show", "cancelled"], default="unknown"
    )
    raw.to_csv(RAW / "appointments_raw_simulated.csv", index=False)
    shifts.to_csv(RAW / "staff_shifts_raw_simulated.csv", index=False)
    cleaned.to_csv(CLEAN / "appointments_cleaned_simulated.csv", index=False)
    shifts.to_csv(CLEAN / "staff_shifts_cleaned_simulated.csv", index=False)
    (REPORTS / "validation_report.md").write_text(validation_report(raw, cleaned, shifts), encoding="utf-8")
    print(f"Generated {len(raw):,} simulated appointments and {len(shifts):,} simulated staff shifts.")


if __name__ == "__main__":
    main()
