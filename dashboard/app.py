"""Clinic Wait-Time Operations Analytics — polished Streamlit dashboard.
All records and findings are simulated for portfolio use.
"""
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if (ROOT / ".python_packages").exists():
    sys.path.insert(0, str(ROOT / ".python_packages"))

st.set_page_config(
    page_title="Clinic Operations Intelligence",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# CUSTOM DASHBOARD UI
# =========================

st.success("🔥 NEW UI VERSION IS RUNNING")

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F4F7FB;
}

/* Remove Streamlit top padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111827;
    border-right: none;
}

section[data-testid="stSidebar"] * {
    color: #E5E7EB !important;
}

/* Main title */
.dashboard-title {
    font-size: 42px;
    font-weight: 800;
    color: #111827;
    letter-spacing: -1.5px;
    margin-bottom: 4px;
}

.dashboard-subtitle {
    font-size: 15px;
    color: #6B7280;
    margin-bottom: 28px;
}

/* Header */
.dashboard-header {
    background: linear-gradient(135deg, #172554, #1E3A8A);
    padding: 30px 34px;
    border-radius: 20px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(30, 58, 138, 0.15);
}

.dashboard-header-title {
    color: white;
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 5px;
}

.dashboard-header-text {
    color: #DBEAFE;
    font-size: 14px;
}

/* KPI cards */
.kpi-card {
    background: white;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
    min-height: 125px;
}

.kpi-label {
    color: #6B7280;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .8px;
}

.kpi-value {
    color: #111827;
    font-size: 30px;
    font-weight: 800;
    margin-top: 8px;
}

.kpi-description {
    color: #9CA3AF;
    font-size: 12px;
    margin-top: 5px;
}

/* Section titles */
.section-title {
    font-size: 22px;
    font-weight: 800;
    color: #111827;
    margin-top: 35px;
    margin-bottom: 4px;
}

.section-description {
    color: #6B7280;
    font-size: 13px;
    margin-bottom: 15px;
}

/* Insight cards */
.insight-card {
    background: white;
    border-radius: 15px;
    padding: 18px;
    border: 1px solid #E5E7EB;
    min-height: 120px;
}

.insight-danger {
    border-left: 5px solid #EF4444;
}

.insight-warning {
    border-left: 5px solid #F59E0B;
}

.insight-success {
    border-left: 5px solid #10B981;
}

.insight-title {
    font-size: 15px;
    font-weight: 700;
    color: #111827;
}

.insight-text {
    font-size: 12px;
    color: #6B7280;
    margin-top: 6px;
    line-height: 1.5;
}

/* Chart containers */
.chart-container {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
}

/* Hide Streamlit menu/footer */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ---------- Design system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --navy:#172033;
    --navy-2:#26344d;
    --ink:#202938;
    --muted:#6b7280;
    --line:#e7ebf0;
    --surface:#ffffff;
    --bg:#f5f7fa;
    --blue:#315efb;
    --blue-soft:#edf2ff;
    --teal:#0f9f92;
    --teal-soft:#eaf8f6;
    --amber:#c78300;
    --amber-soft:#fff7e6;
    --red:#d14343;
    --red-soft:#fff0f0;
}

html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
.stApp { background:var(--bg); color:var(--ink); }
.main .block-container { max-width:1480px; padding:2rem 2.5rem 4rem; }

[data-testid="stHeader"] { background:transparent; }
[data-testid="stSidebar"] {
    background:#fff;
    border-right:1px solid var(--line);
}
[data-testid="stSidebar"] > div:first-child { padding-top:1.5rem; }
[data-testid="stSidebar"] .block-container { padding:1.5rem 1.15rem; }

h1,h2,h3,h4 { font-family:'Manrope', sans-serif; color:var(--navy); }
h1 { font-size:2.25rem !important; letter-spacing:-.04em; margin-bottom:.15rem !important; }
h2 { font-size:1.22rem !important; letter-spacing:-.02em; }
h3 { font-size:1.02rem !important; }

.hero {
    background:linear-gradient(135deg,#172033 0%,#253653 100%);
    border-radius:20px;
    padding:28px 32px;
    color:white;
    margin-bottom:18px;
    box-shadow:0 12px 30px rgba(23,32,51,.12);
}
.hero .eyebrow {
    text-transform:uppercase;
    letter-spacing:.14em;
    font-size:.72rem;
    font-weight:700;
    opacity:.72;
    margin-bottom:8px;
}
.hero h1 { color:white !important; margin:0 !important; }
.hero p { color:#dbe3ef; margin:7px 0 0; font-size:.98rem; }
.hero-right { text-align:right; }
.live {
    display:inline-block;
    background:rgba(255,255,255,.12);
    border:1px solid rgba(255,255,255,.2);
    border-radius:999px;
    padding:7px 12px;
    font-size:.78rem;
    font-weight:700;
}

.notice {
    background:var(--blue-soft);
    border:1px solid #d9e2ff;
    border-left:4px solid var(--blue);
    border-radius:12px;
    padding:11px 14px;
    color:#34446b;
    font-size:.84rem;
    margin-bottom:20px;
}

.section-head {
    display:flex;
    align-items:end;
    justify-content:space-between;
    margin:26px 0 12px;
}
.section-kicker {
    color:var(--blue);
    font-size:.7rem;
    font-weight:800;
    letter-spacing:.13em;
    text-transform:uppercase;
}
.section-title { font-family:'Manrope'; font-weight:800; color:var(--navy); font-size:1.18rem; margin-top:3px; }
.section-desc { color:var(--muted); font-size:.8rem; }

.kpi {
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:16px;
    padding:17px 18px 15px;
    min-height:118px;
    box-shadow:0 4px 16px rgba(31,41,55,.035);
}
.kpi-label { color:#7a8392; font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
.kpi-value { color:var(--navy); font-family:'Manrope'; font-size:1.75rem; font-weight:800; margin:7px 0 4px; letter-spacing:-.035em; }
.kpi-note { color:#8b93a1; font-size:.72rem; }
.kpi-alert .kpi-value { color:var(--red); }
.kpi-good .kpi-value { color:var(--teal); }

.insight {
    background:#fff;
    border:1px solid var(--line);
    border-radius:14px;
    padding:14px 16px;
    height:100%;
}
.insight-tag { font-size:.67rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; margin-bottom:7px; }
.insight-title { font-family:'Manrope'; font-weight:800; color:var(--navy); font-size:.92rem; }
.insight-text { color:#6b7280; font-size:.76rem; line-height:1.45; margin-top:4px; }
.insight-red { border-top:3px solid var(--red); }
.insight-amber { border-top:3px solid #e2a52e; }
.insight-blue { border-top:3px solid var(--blue); }

.panel {
    background:#fff;
    border:1px solid var(--line);
    border-radius:16px;
    padding:18px 18px 10px;
    box-shadow:0 4px 16px rgba(31,41,55,.03);
}
.panel-title { font-family:'Manrope'; font-weight:800; color:var(--navy); font-size:.96rem; }
.panel-sub { color:#8a93a1; font-size:.73rem; margin:3px 0 7px; }

[data-testid="stMetric"] {
    background:#fff;
    border:1px solid var(--line);
    border-radius:16px;
    padding:1rem;
}
[data-testid="stMetricLabel"] { color:#7a8392 !important; }
[data-testid="stMetricValue"] { color:var(--navy) !important; font-family:'Manrope' !important; }

.stButton > button {
    border-radius:10px;
    border:1px solid var(--line);
}
div[data-baseweb="select"] > div {
    border-radius:9px !important;
}
.stExpander {
    border:1px solid var(--line) !important;
    border-radius:12px !important;
    background:#fff !important;
}
[data-testid="stDataFrame"] { border-radius:12px; overflow:hidden; }
footer { visibility:hidden; }

@media (max-width: 900px) {
    .main .block-container { padding:1.2rem; }
    .hero { padding:22px; }
    h1 { font-size:1.75rem !important; }
}
</style>
""", unsafe_allow_html=True)

METRICS = ROOT / "data" / "cleaned" / "metrics"
STAFF = ROOT / "data" / "cleaned" / "staff_shifts_cleaned_simulated.csv"

@st.cache_data
def load():
    needed = [
        "appointment_metrics_simulated.csv",
        "walkout_wait_model_estimates_simulated.csv",
        "recommendation_scenarios_model_estimates_simulated.csv",
    ]
    missing = [x for x in needed if not (METRICS / x).exists()]
    if missing:
        return None, None, None, None, "Missing: " + ", ".join(missing)
    a = pd.read_csv(
        METRICS / needed[0],
        parse_dates=["appointment_date","scheduled_time","arrival_time",
                     "service_start_time","service_end_time"],
    )
    c = pd.read_csv(METRICS / needed[1])
    r = pd.read_csv(METRICS / needed[2])
    s = pd.read_csv(STAFF, parse_dates=["shift_start","shift_end"]) if STAFF.exists() else pd.DataFrame()
    return a, c, r, s, None

a, curve, recs, shifts, err = load()
if err:
    st.error(err)
    st.stop()

a["weekday"] = pd.Categorical(
    a.appointment_date.dt.day_name(),
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
    ordered=True,
)
a["hour"] = a.arrival_time.fillna(a.scheduled_time).dt.hour

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ◉ CLINIC IQ")
    st.caption("Operations intelligence")
    st.divider()
    st.markdown("**FILTERS**")

    locations = st.multiselect(
        "Clinic location",
        sorted(a.clinic_location.unique()),
        default=sorted(a.clinic_location.unique()),
    )
    mind, maxd = a.appointment_date.min().date(), a.appointment_date.max().date()
    dr = st.date_input(
        "Appointment date range",
        value=(mind, maxd),
        min_value=mind,
        max_value=maxd,
    )
    services = st.multiselect(
        "Service type",
        sorted(a.service_type.unique()),
        default=sorted(a.service_type.unique()),
    )
    weekdays = st.multiselect(
        "Day of week",
        list(a.weekday.cat.categories),
        default=list(a.weekday.cat.categories),
    )
    st.divider()
    st.caption("Served = completed. Staffing = planned provider coverage.")
    st.caption("All data is simulated for portfolio demonstration.")

if len(dr) != 2 or not locations or not services or not weekdays:
    st.warning("Select a complete date range and at least one value in each filter.")
    st.stop()

start, end = pd.Timestamp(dr[0]), pd.Timestamp(dr[1])
f = a[
    a.clinic_location.isin(locations)
    & a.appointment_date.between(start, end)
    & a.service_type.isin(services)
    & a.weekday.isin(weekdays)
].copy()

done = f[f.completed]
attended = f[~f.cancelled & ~f.no_show]

provider_hours = 0
if not shifts.empty:
    ss = shifts[
        shifts.clinic_location.isin(locations)
        & shifts.shift_start.dt.normalize().between(start, end)
        & shifts.role.eq("Provider")
    ]
    provider_hours = (ss.shift_end - ss.shift_start).dt.total_seconds().sum() / 3600

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <div class="eyebrow">Operations intelligence platform</div>
  <div style="display:flex;justify-content:space-between;gap:20px;align-items:center;">
    <div>
      <h1>Clinic Wait-Time Analytics</h1>
      <p>Patient flow, staffing capacity & operational risk — in one view.</p>
    </div>
    <div class="hero-right"><span class="live">● LIVE ANALYTICS</span></div>
  </div>
</div>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="notice"><b>SIMULATED DATA</b> — This portfolio dashboard uses synthetic operational data. '
    'No real patients, staff, PII, or clinical records are represented.</div>',
    unsafe_allow_html=True,
)

# ---------- Executive KPI row ----------
st.markdown("""
<div class="section-head">
  <div><div class="section-kicker">01 · Executive overview</div>
  <div class="section-title">Network performance at a glance</div></div>
  <div class="section-desc">Filtered view</div>
</div>
""", unsafe_allow_html=True)

vals = [
    ("Average wait", f"{done.wait_time_minutes.mean():.1f} min", "Completed visits only", ""),
    ("P90 wait", f"{done.wait_time_minutes.quantile(.9):.0f} min", "90th percentile", "kpi-alert" if done.wait_time_minutes.quantile(.9) > 20 else ""),
    ("Wait > 30 min", f"{done.wait_time_minutes.gt(30).mean()*100:.1f}%", "Completed visits", "kpi-alert"),
    ("Walkout rate", f"{f.walked_out.sum()/len(attended)*100:.1f}%", "Of attended patients", "kpi-alert"),
    ("No-show rate", f"{f.no_show.sum()/(~f.cancelled).sum()*100:.1f}%", "Of non-cancelled", ""),
    ("Served / provider hr", f"{len(done)/provider_hours:.2f}" if provider_hours else "N/A", "Planned provider-hours", "kpi-good"),
]
cols = st.columns(6)
for col, (label, value, note, cls) in zip(cols, vals):
    col.markdown(
        f'<div class="kpi {cls}"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>',
        unsafe_allow_html=True,
    )

# ---------- Operational alerts ----------
st.markdown("""
<div class="section-head">
  <div><div class="section-kicker">02 · What needs attention</div>
  <div class="section-title">Operational signals</div></div>
  <div class="section-desc">Prioritize the bottlenecks before broad capacity changes</div>
</div>
""", unsafe_allow_html=True)

loc_wait = done.groupby("clinic_location").wait_time_minutes.mean().sort_values(ascending=False)
top_loc = loc_wait.index[0] if len(loc_wait) else "—"
top_loc_wait = loc_wait.iloc[0] if len(loc_wait) else 0
weekday_no = f[~f.cancelled].groupby("weekday", observed=True).no_show.mean().mul(100).sort_values(ascending=False)
top_day = weekday_no.index[0] if len(weekday_no) else "—"
top_day_rate = weekday_no.iloc[0] if len(weekday_no) else 0

alerts = [
    ("RED", "insight-red", f"{top_loc} is the highest-wait location",
     f"Average wait is {top_loc_wait:.1f} minutes in the current filter. Review peak-hour coverage first."),
    ("AMBER", "insight-amber", f"{top_day} has the strongest no-show signal",
     f"Current filtered no-show rate is {top_day_rate:.1f}%. Prioritize reminders before testing overbooking."),
    ("BLUE", "insight-blue", "Peak-hour coverage is the key lever",
     "Compare patient arrivals with scheduled providers below before considering permanent headcount."),
]
ac = st.columns(3)
for col, (tag, cls, title, text) in zip(ac, alerts):
    col.markdown(
        f'<div class="insight {cls}"><div class="insight-tag">{tag} · SIGNAL</div>'
        f'<div class="insight-title">{title}</div><div class="insight-text">{text}</div></div>',
        unsafe_allow_html=True,
    )

# ---------- Helper ----------
def panel_title(title, subtitle):
    st.markdown(
        f'<div class="panel-title">{title}</div><div class="panel-sub">{subtitle}</div>',
        unsafe_allow_html=True,
    )

plot_layout = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#667085", size=11),
    margin=dict(l=8, r=8, t=8, b=8),
    height=330,
    hoverlabel=dict(bgcolor="#172033", font_color="white"),
)
grid_color = "#eef1f5"

# ---------- Capacity ----------
st.markdown("""
<div class="section-head">
  <div><div class="section-kicker">03 · Capacity</div>
  <div class="section-title">Is staffing aligned with demand?</div></div>
</div>
""", unsafe_allow_html=True)

l, r = st.columns(2)
with l:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    panel_title("Demand vs provider coverage", "Hourly patient arrivals compared with planned providers")
    h = f.groupby("hour", as_index=False).agg(patient_demand=("appointment_id","size"))
    if not shifts.empty:
        t = shifts[
            shifts.clinic_location.isin(locations)
            & shifts.shift_start.dt.normalize().between(start, end)
            & shifts.role.eq("Provider")
        ].copy()
        t["hour"] = t.shift_start.dt.hour
        cov = t.groupby("hour", as_index=False).agg(staffing_coverage=("staff_id","count"))
        cov.staffing_coverage /= max(1, t.shift_start.dt.normalize().nunique())
        h = h.merge(cov, on="hour", how="left").fillna(0)
    else:
        h["staffing_coverage"] = 0
    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(x=h.hour, y=h.patient_demand, name="Patients", marker_color="#315efb"), secondary_y=False)
    fig.add_trace(go.Scatter(x=h.hour, y=h.staffing_coverage, name="Providers", mode="lines+markers",
                             line=dict(color="#0f9f92", width=3)), secondary_y=True)
    fig.update_layout(**plot_layout, legend=dict(orientation="h", y=1.08, x=0))
    fig.update_xaxes(title="Arrival hour", gridcolor=grid_color)
    fig.update_yaxes(title="Patients", gridcolor=grid_color, secondary_y=False)
    fig.update_yaxes(title="Providers", gridcolor=grid_color, secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    panel_title("Wait-time by location", "Average completed-visit wait, ranked highest to lowest")
    x = done.groupby("clinic_location", as_index=False).wait_time_minutes.mean().sort_values("wait_time_minutes")
    fig = px.bar(x, x="wait_time_minutes", y="clinic_location", orientation="h", text_auto=".1f")
    fig.update_traces(marker_color="#315efb", textposition="outside")
    fig.update_layout(**plot_layout, xaxis_title="Average wait (minutes)", yaxis_title="", showlegend=False)
    fig.update_xaxes(gridcolor=grid_color)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Decision lens: prioritize peak-period redesign at the locations with the longest waits.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Wait and service ----------
st.markdown("""
<div class="section-head">
  <div><div class="section-kicker">04 · Patient flow</div>
  <div class="section-title">Where does the queue build?</div></div>
</div>
""", unsafe_allow_html=True)

l, r = st.columns(2)
with l:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    panel_title("Service duration & downstream delay", "Longer services can consume capacity and push later appointments back")
    x = done.groupby("service_type", as_index=False).agg(
        avg_wait=("wait_time_minutes","mean"),
        avg_duration=("service_duration_minutes","mean")
    ).sort_values("avg_wait", ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x.service_type, y=x.avg_wait, name="Wait", marker_color="#315efb"))
    fig.add_trace(go.Bar(x=x.service_type, y=x.avg_duration, name="Service duration", marker_color="#9aa8c2"))
    fig.update_layout(**plot_layout, barmode="group", legend=dict(orientation="h", y=1.08, x=0),
                      yaxis_title="Minutes", xaxis_title="")
    fig.update_yaxes(gridcolor=grid_color)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Decision lens: use longer-service templates to protect capacity during peak sessions.")
    st.markdown('</div>', unsafe_allow_html=True)

with r:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    panel_title("Wait-time heatmap", "Average completed-visit wait by weekday and arrival hour")
    x = done.groupby(["weekday","hour"], observed=True).wait_time_minutes.mean().reset_index()
    x = x.pivot(index="weekday", columns="hour", values="wait_time_minutes").fillna(0)
    fig = px.imshow(x, aspect="auto", color_continuous_scale=["#edf2ff","#315efb"],
                    labels={"x":"Arrival hour","y":"Day","color":"Avg wait"})
    fig.update_layout(**plot_layout, coloraxis_colorbar=dict(title="min"))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Decision lens: schedule flexible coverage around recurring weekday-hour pressure cells.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Patient behavior ----------
st.markdown("""
<div class="section-head">
  <div><div class="section-kicker">05 · Patient behavior</div>
  <div class="section-title">When does patient loss increase?</div></div>
</div>
""", unsafe_allow_html=True)

l, r = st.columns(2)
with l:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    panel_title("Walkout risk curve", "Model-estimated relationship between waiting and walkout probability")
    fig = px.line(curve, x="wait_range", y="estimated_walkout_probability_pct", markers=True)
    fig.update_traces(line=dict(color="#d14343", width=3), marker=dict(size=7))
    fig.update_layout(**plot_layout, xaxis_title="Wait-time band", yaxis_title="Estimated probability (%)")
    fig.update_yaxes(gridcolor=grid_color)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Model estimate only — useful for setting an operational trigger, not proving causality.")
    st.markdown('</div>', unsafe_allow_html=True)

with r:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    panel_title("No-show concentration", "Highest-rate weekday / scheduled-hour combinations")
    x = f[~f.cancelled].groupby(
        ["weekday", f.scheduled_time.dt.hour], observed=True
    ).no_show.mean().mul(100).reset_index(name="no_show_rate")
    x.columns = ["weekday","scheduled_hour","no_show_rate"]
    x = x.sort_values("no_show_rate", ascending=False).head(12)
    fig = px.bar(x, x="scheduled_hour", y="no_show_rate", color="weekday", barmode="group")
    fig.update_layout(**plot_layout, xaxis_title="Scheduled hour", yaxis_title="No-show rate (%)",
                      legend=dict(orientation="h", y=1.08, x=0))
    fig.update_yaxes(gridcolor=grid_color)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Decision lens: target reminder + confirmation outreach at high-risk slots.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Risk table ----------
st.markdown("""
<div class="section-head">
  <div><div class="section-kicker">06 · Action queue</div>
  <div class="section-title">High-risk periods</div></div>
  <div class="section-desc">Sorted by average wait and demand</div>
</div>
""", unsafe_allow_html=True)

x = f.groupby(["clinic_location","weekday","hour"], observed=True).agg(
    demand=("appointment_id","size"),
    average_wait_minutes=("wait_time_minutes","mean"),
    walkouts=("walked_out","sum")
).reset_index()

if not shifts.empty:
    t = shifts[
        shifts.clinic_location.isin(locations)
        & shifts.shift_start.dt.normalize().between(start, end)
        & shifts.role.eq("Provider")
    ].copy()
    t["hour"] = t.shift_start.dt.hour
    p = t.groupby(["clinic_location","hour"], as_index=False).agg(staffing=("staff_id","count"))
    p.staffing /= max(1, t.shift_start.dt.normalize().nunique())
    x = x.merge(p, on=["clinic_location","hour"], how="left").fillna(0)
else:
    x["staffing"] = 0

x["suggested_action"] = x.average_wait_minutes.map(
    lambda z: "Shift peak coverage" if z >= 15
    else ("Monitor queue" if z >= 8 else "Maintain plan")
)
x["average_wait_minutes"] = x["average_wait_minutes"].round(1)
x["staffing"] = x["staffing"].round(1)
x = x.sort_values(["average_wait_minutes","demand"], ascending=False).head(15)

st.dataframe(
    x,
    use_container_width=True,
    hide_index=True,
    column_config={
        "clinic_location":"Clinic",
        "weekday":"Day",
        "hour":st.column_config.NumberColumn("Hour", format="%d:00"),
        "demand":"Demand",
        "average_wait_minutes":"Avg wait (min)",
        "walkouts":"Walkouts",
        "staffing":"Providers",
        "suggested_action":"Suggested response",
    },
)

# ---------- Recommendations ----------
st.markdown("""
<div class="section-head">
  <div><div class="section-kicker">07 · Recommended actions</div>
  <div class="section-title">From insight to intervention</div></div>
</div>
""", unsafe_allow_html=True)

for i, q in enumerate(recs.itertuples(index=False), start=1):
    impact = (
        "Capacity release; test to quantify wait impact"
        if pd.isna(q.estimated_wait_or_duration_improvement_minutes)
        else f"Directional estimate: {abs(q.estimated_wait_or_duration_improvement_minutes):.1f} min"
    )
    with st.expander(f"{i:02d}  ·  {q.target} — {q.recommendation}"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Finding**")
            st.write(q.method_note)
        with c2:
            st.markdown("**Estimated impact**")
            st.write(impact)
        st.markdown("**Operational change**")
        st.write(q.recommendation)
        st.caption("Model estimate, not a proven real-world outcome.")

st.divider()
st.caption("Clinic Wait-Time Operations Analytics · Simulated data · Built for portfolio demonstration")
