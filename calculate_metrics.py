"""Stage 2 metric layer for the clinic wait-time analytics portfolio project.

Reads only the validated, fully simulated Stage 1 datasets and writes tidy KPI
tables for later dashboard work. Run: python calculate_metrics.py
"""
from __future__ import annotations

from pathlib import Path
import sys

LOCAL_PACKAGES = Path(__file__).resolve().parent / ".python_packages"
if LOCAL_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_PACKAGES))

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "cleaned"
OUTPUT = INPUT / "metrics"


def rates_and_waits(frame: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """Produce a consistent, dashboard-ready KPI grain for any grouping."""
    rows = []
    grouper = group_cols[0] if len(group_cols) == 1 else group_cols
    for keys, group in frame.groupby(grouper, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        scheduled = len(group)
        non_cancelled = group[~group["cancelled"]]
        attended = group[~group["cancelled"] & ~group["no_show"]]
        completed = group[group["completed"]]
        attended_with_arrival = attended["late_arrival_minutes"].dropna()
        completed_wait = completed["wait_time_minutes"].dropna()
        completed_duration = completed["service_duration_minutes"].dropna()
        row = dict(zip(group_cols, keys))
        row.update({
            "scheduled_appointments": scheduled,
            "attended_appointments": len(attended),
            "completed_appointments": len(completed),
            "cancelled_appointments": int(group["cancelled"].sum()),
            "no_show_appointments": int(group["no_show"].sum()),
            "walked_out_appointments": int(group["walked_out"].sum()),
            "completion_rate_pct": round(len(completed) / scheduled * 100, 2) if scheduled else np.nan,
            "cancellation_rate_pct": round(group["cancelled"].mean() * 100, 2) if scheduled else np.nan,
            "no_show_rate_pct": round(group["no_show"].sum() / len(non_cancelled) * 100, 2) if len(non_cancelled) else np.nan,
            "walkout_rate_pct": round(group["walked_out"].sum() / len(attended) * 100, 2) if len(attended) else np.nan,
            "avg_wait_time_minutes": round(completed_wait.mean(), 2),
            "median_wait_time_minutes": round(completed_wait.median(), 2),
            "p90_wait_time_minutes": round(completed_wait.quantile(0.90), 2),
            "pct_waiting_over_15_minutes": round((completed_wait > 15).mean() * 100, 2),
            "pct_waiting_over_30_minutes": round((completed_wait > 30).mean() * 100, 2),
            "avg_late_arrival_minutes": round(attended_with_arrival.mean(), 2),
            "pct_arriving_late": round((attended_with_arrival > 0).mean() * 100, 2),
            "avg_service_duration_minutes": round(completed_duration.mean(), 2),
            "avg_satisfaction_score": round(completed["satisfaction_score"].mean(), 2),
            "complaint_rate_pct": round(completed["complaint_flag"].astype(float).mean() * 100, 2),
        })
        rows.append(row)
    return pd.DataFrame(rows)


def build_coverage(shifts: pd.DataFrame) -> pd.DataFrame:
    """Hourly scheduled provider coverage, by clinic and calendar date."""
    providers = shifts[shifts["role"] == "Provider"].copy()
    records = []
    for shift in providers.itertuples(index=False):
        hours = pd.date_range(shift.shift_start.floor("h"), shift.shift_end.ceil("h"), freq="h", inclusive="left")
        for hour in hours:
            records.append({"clinic_location": shift.clinic_location, "appointment_date": hour.normalize(), "hour_of_day": hour.hour, "providers_scheduled": 1})
    return pd.DataFrame(records).groupby(["clinic_location", "appointment_date", "hour_of_day"], as_index=False)["providers_scheduled"].sum()


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    appts = pd.read_csv(
        INPUT / "appointments_cleaned_simulated.csv",
        parse_dates=["appointment_date", "scheduled_time", "arrival_time", "service_start_time", "service_end_time"],
    )
    shifts = pd.read_csv(INPUT / "staff_shifts_cleaned_simulated.csv", parse_dates=["shift_start", "shift_end"])

    # Recalculate core measures from timestamps (rather than trusting a prior derived column).
    appts["wait_time_minutes"] = (appts["service_start_time"] - appts["arrival_time"]).dt.total_seconds() / 60
    appts["service_duration_minutes"] = (appts["service_end_time"] - appts["service_start_time"]).dt.total_seconds() / 60
    appts["late_arrival_minutes"] = (appts["arrival_time"] - appts["scheduled_time"]).dt.total_seconds().div(60).clip(lower=0)
    appts["hour_of_day"] = appts["arrival_time"].fillna(appts["scheduled_time"]).dt.hour
    appts["weekday"] = appts["appointment_date"].dt.day_name()
    appts["weekday_number"] = appts["appointment_date"].dt.weekday

    # Attach the planned staff shift to completed appointments; non-completed rows retain no staff shift.
    shifts["appointment_date"] = shifts["shift_start"].dt.normalize()
    shifts["staff_shift"] = shifts["shift_start"].dt.strftime("%H:%M") + "–" + shifts["shift_end"].dt.strftime("%H:%M")
    appts = appts.merge(
        shifts[["staff_id", "clinic_location", "appointment_date", "staff_shift", "shift_start", "shift_end"]],
        on=["staff_id", "clinic_location", "appointment_date"], how="left", validate="m:1",
    )
    appts["staff_shift"] = appts["staff_shift"].fillna("Not assigned")

    # Appointment-level enriched output is retained for drill-through and auditability.
    appts.to_csv(OUTPUT / "appointment_metrics_simulated.csv", index=False)

    # Standard KPI tables by requested operational cuts.
    overall = rates_and_waits(appts.assign(scope="All clinics"), ["scope"])
    by_location = rates_and_waits(appts, ["clinic_location"])
    by_hour = rates_and_waits(appts, ["hour_of_day"])
    by_weekday = rates_and_waits(appts, ["weekday_number", "weekday"]).sort_values("weekday_number")
    by_service = rates_and_waits(appts, ["service_type"])
    by_staff_shift = rates_and_waits(appts, ["staff_shift"])

    # Join scheduled provider coverage to a demand-hour table for capacity decisions.
    coverage = build_coverage(shifts)
    demand = appts.groupby(["clinic_location", "appointment_date", "hour_of_day"], as_index=False).agg(
        scheduled_appointments=("appointment_id", "size"),
        attended_appointments=("arrival_time", lambda s: int(s.notna().sum())),
        completed_appointments=("completed", "sum"),
        avg_wait_time_minutes=("wait_time_minutes", "mean"),
        walked_out_appointments=("walked_out", "sum"),
    )
    hourly_capacity = demand.merge(coverage, on=["clinic_location", "appointment_date", "hour_of_day"], how="left")
    hourly_capacity["providers_scheduled"] = hourly_capacity["providers_scheduled"].fillna(0).astype(int)
    hourly_capacity["appointments_per_provider"] = np.where(
        hourly_capacity["providers_scheduled"] > 0,
        hourly_capacity["attended_appointments"] / hourly_capacity["providers_scheduled"], np.nan,
    )
    hourly_capacity["avg_wait_time_minutes"] = hourly_capacity["avg_wait_time_minutes"].round(2)
    hourly_capacity["appointments_per_provider"] = hourly_capacity["appointments_per_provider"].round(2)

    overall.to_csv(OUTPUT / "kpi_overall.csv", index=False)
    by_location.to_csv(OUTPUT / "kpi_by_location.csv", index=False)
    by_hour.to_csv(OUTPUT / "kpi_by_hour.csv", index=False)
    by_weekday.to_csv(OUTPUT / "kpi_by_weekday.csv", index=False)
    by_service.to_csv(OUTPUT / "kpi_by_service_type.csv", index=False)
    by_staff_shift.to_csv(OUTPUT / "kpi_by_staff_shift.csv", index=False)
    hourly_capacity.to_csv(OUTPUT / "hourly_capacity_simulated.csv", index=False)

    print(f"Wrote {len(appts):,} appointment-level rows and 8 dashboard-ready metric tables to {OUTPUT}")
    print(overall.to_string(index=False))


if __name__ == "__main__":
    main()
