# Simulation Assumptions — Simulated Data

All datasets in this project are fully simulated for portfolio analysis. They contain no real clinic, patient, or staff data and no PII.

## Coverage and demand

- The simulation covers 1 January–30 June 2026, Monday through Saturday; Sunday is closed.
- Four intentionally different locations are modeled: Central City (highest demand and afternoon congestion), Northside (balanced), Lakeside (lower demand and more capacity headroom), and West End (morning constraint from staggered provider starts).
- Daily appointment demand is Poisson-distributed around location-specific baselines (Central City 55, Northside 40, Lakeside 32, West End 36), elevated on Mondays, reduced on Saturdays, and modestly seasonally higher in February–March.
- Appointment slots are every 10 minutes. Demand is concentrated around late morning and mid/late afternoon; Central City has an additional late-afternoon wave and West End an early-morning wave.

## Staffing and capacity

- Provider staffing by location is planned as 3 / 3 / 3 / 2 (Central City / Northside / Lakeside / West End); support staffing is 5 / 4 / 3 / 3. This intentionally leaves Central City and West End with less peak-period headroom than Lakeside.
- Weekday shifts generally run 08:00–17:00 and Saturday shifts end at 13:00. At West End, the second provider starts at 09:00 to create a deliberate opening-period bottleneck.
- Visits are assigned to the earliest available on-shift provider within the same clinic. Provider availability is retained across appointments, so when arrivals exceed coverage, queues and wait times increase. Queue carryover may create simulated overtime.

## Services and timing

- Service mix: Primary Care 38%, Follow-up 27%, Vaccination 16%, Chronic Care 12%, Minor Procedure 7%.
- Service times are normally distributed and truncated at 5 minutes: means / standard deviations are 18/5, 13/4, 9/3, 28/7, and 38/10 minutes respectively. A location pressure multiplier introduces realistic operational variation.
- Attended patients arrive approximately 4 minutes early on average, with a bounded normal offset of -32 to +45 minutes. Peak-hour traffic adds a small late-arrival bias.
- Late arrivals raise demand concentration and add a small incremental walkout likelihood.

## Appointment outcomes and feedback

- Cancellations occur at roughly 3.5%, with a modest Monday uplift.
- No-shows are more likely for appointments before 09:00 and on Mondays (baseline 4.2%, plus selected-slot uplifts). Cancelled appointments are excluded from no-show status.
- Walkout probability rises smoothly—not at a cutoff—with prospective wait time using a logistic curve centered near 42 minutes, plus a small late-arrival effect. Walkouts leave before service and therefore do not consume provider capacity.
- Completed-visit satisfaction declines with wait time plus random response variation. Complaint probability rises gradually with wait time. Feedback is missing for non-completed appointments by design.

## Scope limitation

The simulation encodes known causal relationships deliberately for analysis practice; it is not calibrated to any real clinic and does not represent measured operational effects.
