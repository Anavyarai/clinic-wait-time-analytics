# Stage 2 Metric Definitions — Simulated Data

All measures below are calculated exclusively from the validated **simulated data** produced in Stage 1. These outputs are intended for later dashboard development and should not be interpreted as real clinic performance.

## Core timing measures

| Measure | Definition | Population |
|---|---|---|
| `wait_time_minutes` | `service_start_time - arrival_time` | Completed appointments |
| `service_duration_minutes` | `service_end_time - service_start_time` | Completed appointments |
| `late_arrival_minutes` | `max(arrival_time - scheduled_time, 0)` | Attended appointments |
| `hour_of_day` | Arrival hour; scheduled hour when arrival is unavailable | All scheduled appointments |
| `staff_shift` | Assigned provider's planned `shift_start–shift_end`; `Not assigned` otherwise | All scheduled appointments |

## KPI definitions

| KPI | Definition |
|---|---|
| Scheduled appointments | Count of appointment records. |
| Attended appointments | Not cancelled and not a no-show; walkouts are included. |
| Completed appointments | `completed = true`. |
| Completion rate | Completed appointments / scheduled appointments. |
| Cancellation rate | Cancelled appointments / scheduled appointments. |
| No-show rate | No-shows / non-cancelled appointments. |
| Walkout rate | Walkouts / attended appointments. |
| Average / median / P90 wait | Corresponding distribution statistic for completed appointments only. |
| Wait over 15 / 30 minutes | Percent of completed appointments exceeding the named threshold. |
| Average late arrival / percent arriving late | Mean positive minutes late / share of attended appointments with a positive arrival offset. |
| Average service duration | Mean completed-visit service duration. |
| Average satisfaction / complaint rate | Completed-visit feedback average / complaint flags divided by completed visits. |
| Appointments per provider | Attended appointments in the clinic-date-hour / providers scheduled in that same hour. |

## Outputs

All CSVs are in `data/cleaned/metrics/` and are dashboard-ready, tidy tables:

- `appointment_metrics_simulated.csv` — appointment-level enriched fact table for drill-through.
- `kpi_overall.csv` — headline metrics.
- `kpi_by_location.csv`, `kpi_by_hour.csv`, `kpi_by_weekday.csv`, `kpi_by_service_type.csv`, `kpi_by_staff_shift.csv` — requested operational breakdowns.
- `hourly_capacity_simulated.csv` — clinic-date-hour demand, scheduled provider coverage, appointments per provider, wait, and walkouts for capacity analysis.
