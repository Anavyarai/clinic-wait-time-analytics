"""Stage 3 analytical investigation for fully simulated clinic data only."""
from __future__ import annotations
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / ".python_packages"
if LOCAL.exists(): sys.path.insert(0, str(LOCAL))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

METRICS = ROOT / "data" / "cleaned" / "metrics"
IMAGES = ROOT / "images"
SERVICE_TARGETS = {"Primary Care": 15, "Follow-up": 12, "Vaccination": 10, "Chronic Care": 25, "Minor Procedure": 30}

def savefig(name: str) -> None:
    plt.tight_layout(); plt.savefig(IMAGES / name, dpi=160, bbox_inches="tight"); plt.close()

def write_notebook() -> None:
    """Write the reproducible notebook front end for this investigation."""
    def markdown(source): return {"cell_type":"markdown","metadata":{},"source":[source]}
    def code(source): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":[source]}
    cells = [
        markdown("# Clinic Wait-Time Analytics: Stage 3 Investigation\n\n## Simulated data only\nThis notebook analyzes only the validated synthetic data in this project. It contains no real clinic, patient, or staff data. Scenario outcomes are **model estimates**, not proven causal effects."),
        code("from pathlib import Path\nimport runpy\nimport pandas as pd\nfrom IPython.display import Image, display\nROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\nrunpy.run_path(ROOT / 'stage3_analysis.py', run_name='__main__')\nMETRICS = ROOT / 'data' / 'cleaned' / 'metrics'\nIMAGES = ROOT / 'images'\ndef table(name): return pd.read_csv(METRICS / name)"),
        markdown("## Highest-priority operational problems\n1. Central City late-morning and late-afternoon congestion.\n2. West End opening and mid-morning coverage constraint.\n3. Minor Procedure and Chronic Care templates underestimate service time.\n4. Model-estimated walkout risk rises materially at 30–44 minutes of waiting.\n5. Early and Monday slots concentrate no-shows."),
        markdown("## 1. Overloaded hours, weekdays, and locations\nThe heatmap identifies repeated high-wait cells, led by Central City and selected West End hours. These are wave-specific problems rather than all-day demand.\n\n**Decision:** shift flexible Central City coverage from the 13:00 low-demand period to 15:00–16:00; protect West End opening coverage before increasing headcount."),
        code("display(Image(filename=str(IMAGES / 'stage3_wait_heatmap_simulated.png')))\ntable('location_weekday_hour_load_simulated.csv').query('demand_coverage_mismatch == True').head(12)"),
        markdown("## 2. Understaffing relative to demand\nRequired provider equivalents use completed service-hours divided by an 85% utilization target. Central City has the largest recurring average shortfalls at 10:00 and 15:00; West End has smaller shortfalls near 09:00–10:00.\n\n**Decision:** pilot staggered shifts first, then add contingent capacity only if wait targets remain unmet."),
        code("table('staffing_gap_by_location_hour_simulated.csv').sort_values('peak_provider_gap', ascending=False).head(12)"),
        markdown("## 3. Service types running longer than scheduled\nBooking targets are stated planning assumptions because the source data has no scheduled-duration field. Minor Procedure, Chronic Care, and Primary Care run over target; Vaccination is on target.\n\n**Decision:** add 10 minutes to Minor Procedure bookings and test a five-minute Chronic Care buffer in high-congestion periods."),
        code("display(Image(filename=str(IMAGES / 'stage3_service_duration_variance_simulated.png')))\ntable('service_duration_variance_simulated.csv')"),
        markdown("## 4. Wait range where walkout risk rises\nWalkouts do not have a service-start timestamp, so their realized wait is unknown. The chart is a **model estimate** from the simulation's smooth walkout rule. Risk first rises materially at **30–44 minutes** and increases faster beyond 45 minutes.\n\n**Decision:** trigger queue overflow actions at 30 minutes: cross-cover, proactive patient updates, or voluntary rebooking."),
        code("display(Image(filename=str(IMAGES / 'stage3_walkout_wait_model_estimate.png')))\ntable('walkout_wait_model_estimates_simulated.csv')"),
        markdown("## 5. No-show concentration\nFirst-hour slots have the highest simulated no-show rates, with Monday 08:00 also elevated.\n\n**Decision:** use reminder-plus-confirmation outreach for Monday and pre-09:00 bookings; do not broadly overbook before testing completion and walkout effects."),
        code("display(Image(filename=str(IMAGES / 'stage3_no_show_slots_simulated.png')))\ntable('no_show_by_weekday_slot_simulated.csv').head(12)"),
        markdown("## 6. Staffing-demand mismatch\nHourly appointments per provider and wait spikes do not always coincide because queues carry over. Daily staffing totals therefore conceal the operational mismatch.\n\n**Decision:** govern capacity by clinic-date-hour demand, starting with Central City 15:00–16:00 and West End 08:00."),
        code("capacity=table('hourly_capacity_simulated.csv')\ncapacity.groupby(['clinic_location','hour_of_day'],as_index=False).agg(avg_attended=('attended_appointments','mean'),avg_providers=('providers_scheduled','mean'),avg_appts_per_provider=('appointments_per_provider','mean'),avg_wait=('avg_wait_time_minutes','mean')).sort_values('avg_wait',ascending=False).head(15)"),
        markdown("## Recommendation scenarios — model estimates\nThe scenarios are transparent directional estimates. Reallocation scenarios use observed peak-versus-low-demand wait differences; booking changes use duration variance against stated targets; targeted reminders assume a 15–25% no-show reduction. They are not causal proof."),
        code("table('recommendation_scenarios_model_estimates_simulated.csv')"),
        markdown("## Limitations of inference\n- Data and embedded patterns are simulated, not real-world evidence.\n- Staffing gaps use completed service time and can understate unmet demand from walkouts.\n- The model excludes rooms, specialty matching, breaks, emergencies, insurance, and rescheduling.\n- Walkout-by-wait findings are model estimates because realized waits are undefined for walkouts.\n- Test each intervention with operational guardrails and a pre-defined comparison period.")
    ]
    notebook = {"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.12"}},"nbformat":4,"nbformat_minor":5}
    out = ROOT / "notebooks" / "clinic_wait_time_stage3_analysis.ipynb"; out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(notebook, indent=1), encoding="utf-8")

def main() -> None:
    IMAGES.mkdir(exist_ok=True)
    a = pd.read_csv(METRICS / "appointment_metrics_simulated.csv", parse_dates=["appointment_date", "scheduled_time", "arrival_time", "service_start_time", "service_end_time"])
    cap = pd.read_csv(METRICS / "hourly_capacity_simulated.csv", parse_dates=["appointment_date"])
    a["weekday"] = pd.Categorical(a["appointment_date"].dt.day_name(), ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"], ordered=True)
    a["scheduled_hour"] = a["scheduled_time"].dt.hour
    completed = a[a.completed].copy()

    # 1 and 6: demand, coverage and operational overload at location-weekday-hour grain.
    profile = cap.merge(a[["appointment_id","clinic_location","appointment_date","hour_of_day","weekday"]], on=["clinic_location","appointment_date","hour_of_day"], how="left")
    profile = profile.groupby(["clinic_location","weekday","hour_of_day"], observed=True).agg(
        avg_scheduled_appointments=("scheduled_appointments","mean"), avg_attended_appointments=("attended_appointments","mean"),
        avg_providers_scheduled=("providers_scheduled","mean"), avg_appointments_per_provider=("appointments_per_provider","mean"),
        avg_wait_time_minutes=("avg_wait_time_minutes","mean"), avg_walkouts=("walked_out_appointments","mean"), clinic_days=("appointment_date","nunique")
    ).reset_index()
    profile["demand_coverage_mismatch"] = (profile.avg_appointments_per_provider >= 2.5) | (profile.avg_wait_time_minutes >= 12)
    profile.sort_values(["avg_wait_time_minutes","avg_appointments_per_provider"], ascending=False).to_csv(METRICS / "location_weekday_hour_load_simulated.csv", index=False)

    heat = profile.pivot_table(index=["clinic_location","weekday"], columns="hour_of_day", values="avg_wait_time_minutes", aggfunc="mean").fillna(0)
    plt.figure(figsize=(11,6)); plt.imshow(heat, aspect="auto", cmap="YlOrRd"); plt.colorbar(label="Average wait (minutes)")
    plt.yticks(range(len(heat.index)), [f"{x[0]} — {x[1]}" for x in heat.index]); plt.xticks(range(len(heat.columns)), heat.columns)
    plt.title("Simulated average wait by location, weekday, and arrival hour"); plt.xlabel("Arrival hour"); savefig("stage3_wait_heatmap_simulated.png")

    # 2: staffing gap uses realized service demand and a transparent 85% target utilization.
    completed["service_hours"] = completed.service_duration_minutes / 60
    required = completed.groupby(["clinic_location","appointment_date","hour_of_day"], as_index=False).service_hours.sum().rename(columns={"service_hours":"completed_service_hours"})
    gaps = cap.merge(required, on=["clinic_location","appointment_date","hour_of_day"], how="left").fillna({"completed_service_hours":0})
    gaps["required_provider_equivalents"] = gaps.completed_service_hours / 0.85
    gaps["provider_gap"] = (gaps.required_provider_equivalents - gaps.providers_scheduled).round(2)
    gaps["provider_gap_positive"] = gaps.provider_gap.clip(lower=0)
    staffing = gaps.groupby(["clinic_location","hour_of_day"], as_index=False).agg(
        avg_scheduled_providers=("providers_scheduled","mean"), avg_required_provider_equivalents=("required_provider_equivalents","mean"),
        avg_provider_gap=("provider_gap","mean"), peak_provider_gap=("provider_gap","max"), avg_wait_time_minutes=("avg_wait_time_minutes","mean"),
        avg_attended_appointments=("attended_appointments","mean")
    )
    staffing.sort_values("peak_provider_gap", ascending=False).to_csv(METRICS / "staffing_gap_by_location_hour_simulated.csv", index=False)

    # 3: service duration against explicit scheduling targets (planning assumption, not source fact).
    service = completed.groupby("service_type", as_index=False).agg(completed_appointments=("appointment_id","size"), avg_service_duration_minutes=("service_duration_minutes","mean"), p90_service_duration_minutes=("service_duration_minutes", lambda x:x.quantile(.9)), avg_wait_time_minutes=("wait_time_minutes","mean"))
    service["scheduled_duration_target_minutes"] = service.service_type.map(SERVICE_TARGETS)
    service["duration_variance_minutes"] = (service.avg_service_duration_minutes-service.scheduled_duration_target_minutes).round(2)
    service = service.sort_values("duration_variance_minutes", ascending=False); service.to_csv(METRICS / "service_duration_variance_simulated.csv", index=False)
    plt.figure(figsize=(9,4)); plt.bar(service.service_type, service.duration_variance_minutes, color=["#c2410c" if x>0 else "#0f766e" for x in service.duration_variance_minutes]); plt.axhline(0,color="black",lw=.8); plt.xticks(rotation=25,ha="right"); plt.ylabel("Minutes vs booking target"); plt.title("Simulated service duration variance by service type"); savefig("stage3_service_duration_variance_simulated.png")

    # 4: transparent model estimate. Walkouts have no observed realized wait, so calculate curve explicitly.
    bands = pd.DataFrame({"wait_range":["0–14","15–29","30–44","45–59","60+"], "wait_midpoint_minutes":[7,22,37,52,67]})
    late_effect = 0.025/(1+np.exp(-(completed.late_arrival_minutes.mean()-18)/7))
    bands["estimated_walkout_probability_pct"] = (100*(.006+.39/(1+np.exp(-(bands.wait_midpoint_minutes-42)/15))+late_effect)).round(1)
    bands["increment_vs_prior_band_pp"] = bands.estimated_walkout_probability_pct.diff().fillna(0).round(1)
    bands.to_csv(METRICS / "walkout_wait_model_estimates_simulated.csv", index=False)
    plt.figure(figsize=(7,4)); plt.plot(bands.wait_range,bands.estimated_walkout_probability_pct,marker="o",color="#c2410c"); plt.ylabel("Model-estimated walkout probability (%)"); plt.title("Walkout risk rises materially after ~30 minutes (model estimate)"); savefig("stage3_walkout_wait_model_estimate.png")

    # 5: no-show concentration using scheduled, non-cancelled appointments.
    slots = a[~a.cancelled].groupby(["weekday","scheduled_hour"], observed=True).agg(non_cancelled_appointments=("appointment_id","size"), no_show_appointments=("no_show","sum"), no_show_rate_pct=("no_show","mean")).reset_index()
    slots.no_show_rate_pct = (slots.no_show_rate_pct*100).round(2); slots.sort_values("no_show_rate_pct", ascending=False).to_csv(METRICS / "no_show_by_weekday_slot_simulated.csv", index=False)
    ns = slots.pivot(index="weekday",columns="scheduled_hour",values="no_show_rate_pct").fillna(0)
    plt.figure(figsize=(9,4)); plt.imshow(ns,aspect="auto",cmap="Blues"); plt.colorbar(label="No-show rate (%)"); plt.yticks(range(len(ns.index)),ns.index); plt.xticks(range(len(ns.columns)),ns.columns); plt.title("Simulated no-show concentration by scheduled slot"); plt.xlabel("Scheduled hour"); savefig("stage3_no_show_slots_simulated.png")

    # Scenario model estimates: simple observed peak vs reference-period differences, not causal proofs.
    loc_hour = cap.groupby(["clinic_location","hour_of_day"],as_index=False).agg(avg_wait=("avg_wait_time_minutes","mean"), avg_attended=("attended_appointments","mean"), avg_providers=("providers_scheduled","mean"))
    central_peak = loc_hour[(loc_hour.clinic_location=="Central City") & (loc_hour.hour_of_day.isin([15,16]))].avg_wait.mean()
    central_ref = loc_hour[(loc_hour.clinic_location=="Central City") & (loc_hour.hour_of_day==13)].avg_wait.mean()
    west_peak = loc_hour[(loc_hour.clinic_location=="West End") & (loc_hour.hour_of_day==8)].avg_wait.mean()
    west_ref = loc_hour[(loc_hour.clinic_location=="West End") & (loc_hour.hour_of_day==13)].avg_wait.mean()
    scenarios = pd.DataFrame([
        ["Shift one Central City provider from 13:00 to 15:00–16:00", "Central City weekday afternoon", "Reallocate one existing provider; no net headcount", round(central_peak-central_ref,1), "Observed peak-to-low-demand-period wait difference used as a directional estimate"],
        ["Start West End's second provider at 08:00", "West End opening hour", "Move existing 09:00 start one hour earlier", round(west_peak-west_ref,1), "Observed 08:00-to-low-demand-period wait difference used as a directional estimate"],
        ["Extend Minor Procedure booking target by 10 minutes", "Minor Procedure", "No added staffing; reduce downstream queue pressure", round(float(service.loc[service.service_type=="Minor Procedure","duration_variance_minutes"].iloc[0]),1), "Average overrun minutes versus stated booking target"],
        ["Target reminders for Monday and pre-09:00 appointments", "High-risk no-show slots", "Assume a 15–25% reduction in no-shows in targeted slots", np.nan, "Model estimate: releases capacity; wait effect requires operational trial"],
    ], columns=["recommendation","target","scenario_assumption","estimated_wait_or_duration_improvement_minutes","method_note"])
    scenarios.to_csv(METRICS / "recommendation_scenarios_model_estimates_simulated.csv",index=False)
    write_notebook()
    print("Stage 3 outputs written. Highest location average waits:")
    print(completed.groupby("clinic_location").wait_time_minutes.mean().sort_values(ascending=False).round(1))

if __name__ == "__main__": main()
