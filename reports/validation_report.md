# Validation Report — Simulated Data

**Scope:** Synthetic clinic operations data generated with seed `20260913`. No real clinic, patient, or staff data is represented.

## Output counts

| Dataset | Rows |
|---|---:|
| Raw appointments | 25,211 |
| Cleaned appointments | 25,211 |
| Staff shifts | 4,030 |
| Completed appointments | 21,890 |

## Null counts — raw appointments

|                    |   null_count |
|:-------------------|-------------:|
| appointment_id     |            0 |
| clinic_location    |            0 |
| appointment_date   |            0 |
| service_type       |            0 |
| scheduled_time     |            0 |
| arrival_time       |         2161 |
| cancelled          |            0 |
| no_show            |            0 |
| service_start_time |         3321 |
| service_end_time   |         3321 |
| staff_id           |         3321 |
| role               |         3321 |
| walked_out         |            0 |
| completed          |            0 |
| satisfaction_score |         3321 |
| complaint_flag     |            0 |

Expected nulls occur for arrivals and service timestamps of cancelled/no-show appointments, and service/staff fields for walkouts. Feedback is collected only after completed visits.

## Data types — raw appointments

|                    | dtype          |
|:-------------------|:---------------|
| appointment_id     | str            |
| clinic_location    | str            |
| appointment_date   | datetime64[us] |
| service_type       | str            |
| scheduled_time     | datetime64[us] |
| arrival_time       | datetime64[us] |
| cancelled          | bool           |
| no_show            | bool           |
| service_start_time | datetime64[us] |
| service_end_time   | datetime64[us] |
| staff_id           | str            |
| role               | str            |
| walked_out         | bool           |
| completed          | bool           |
| satisfaction_score | float64        |
| complaint_flag     | boolean        |

## Time and range sanity checks

- Appointment dates range from **2026-01-01** to **2026-06-30**.
- Scheduled times range from **2026-01-01 08:00:00** to **2026-06-30 16:50:00**; clinics operate Monday–Saturday only.
- Negative waits among completed visits: **0** (expected 0).
- Service end at/before service start among completed visits: **0** (expected 0).
- Arrival offsets for attended appointments: median **-3.0 min**, 1st–99th percentile **-27.0 to 20.0 min**; all are within the configured -32 to +45 minute envelope.
- Staff-shift consistency: **98.7%** of completed visits start within their assigned provider shift. The remainder are simulated overtime caused by queue carryover; no visit is assigned to a different clinic.

## Plausibility checks

| Measure (completed visits unless noted) | Result |
|---|---:|
| Mean wait | 6.9 min |
| Median / 90th-percentile wait | 0.0 / 23.0 min |
| Mean service duration | 19.5 min |
| Service-duration 1st–99th percentile | 5.0–55.0 min |
| Walkout rate (all appointments) | 4.6% |
| No-show rate (not cancelled) | 5.0% |
| Complaint rate (completed) | 5.5% |

## Known simulation limitations

This is simulated data, not a forecast or a representation of a real clinic. The model uses a provider-queue abstraction and does not model rooms, clinician specialty matching, insurance, emergencies, rescheduling, or individual patient behavior. Staffing is planned at the shift level; unplanned absences and real-time breaks are not simulated. Causal patterns are intentionally encoded for analysis practice and should not be interpreted as measured effects.
