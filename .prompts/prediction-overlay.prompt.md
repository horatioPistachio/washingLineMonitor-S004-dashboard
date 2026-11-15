---
description: "Add a drying-time plot on the device page: historical resistance plus a red dashed predicted-resistance overlay until predicted drying time."
name: "Prediction Overlay"
agent: "agent"
---

# Prediction Overlay — Drying Time Plot

Add a **Drying Time** chart at the **top of the plots section** on the device detail page. It shows historical resistance from telemetry, then extrapolates future resistance with a red dashed predicted path until the predicted drying time.

Follow [agents.md](../agents.md): keep the change in [app.py](../app.py), reuse existing `fetch_*` / Altair patterns, handle API failures with sensible defaults, and do not over-engineer.

Reference sketch: [image.png](./image.png)

## Goal

On the device page (`?page=device&device_id=...`), above the existing per-metric telemetry charts:

1. Render a chart titled **Drying Time** (or **Resistance** with drying overlay).
2. Plot **historical resistance** as a **solid blue line** (same series already used for the resistance telemetry plot).
3. Overlay **predicted future resistance** as a **red dashed line**.
4. The predicted segment starts at **now** and continues until **predicted drying time** from the device **status** endpoint.
5. Keep the existing individual metric plots below this new chart. Do not remove them.

Do **not** hardcode `wash0001`. Use the `device_id` from the query params, same as the rest of the device page.

## Visual spec

Match [image.png](./image.png):

| Series | Style | Data |
|---|---|---|
| Historical resistance | Solid blue line | Telemetry `payload.resistance` already in `df` |
| Predicted drying path | Red dashed line | Model `R(t)` from `now` to predicted drying time |

Chart requirements:

- Place this chart **first** in the plots section, before temperature/humidity/other metrics.
- Use **Altair** (existing `plot_telemetry_metric()` uses `st.altair_chart`). Layer two encodings rather than adding Plotly.
- X-axis: time, in the **user timezone** already used by `process_telemetry_data()`.
- Y-axis: resistance, `zero=False`, padded domain covering **both** historical and predicted values.
- X-axis domain must extend through **predicted drying time**, even if telemetry ends at now.
- No hover overlay that reintroduces the Vega empty-highlight warning already avoided in `plot_telemetry_metric()`.
- If prediction data is missing, still show historical resistance and skip the dashed overlay (do not fail the page).

## Data sources

### Historical resistance

Already available on the device page:

- `GET /api/v1/telemetry/{device_id}` via `fetch_telemetry_data()`
- Processed by `process_telemetry_data()` into `df` with `timestamp` + payload columns
- Resistance column is typically `resistance`

If `resistance` is missing from `df`, do not render the drying-time chart; show a short info message and continue with the other metric plots.

### State-vector parameters (model)

**GET** `/api/v1/devices/{device_id}/state_vector`

Example:

```json
{
  "start_time": "2026-09-06T10:00:00Z",
  "r": 30000.0,
  "m": 0.02,
  "k": 0.5,
  "tau": 0.81,
  "m_c": 0.000000001,
  "r_offset": 29976.33
}
```

Field mapping:

| JSON field | Symbol | Role |
|---|---|---|
| `start_time` | — | Absolute time when `t = 0` minutes. Parse as UTC, then convert to the user timezone. |
| `m` | \(M_0\) | Initial moisture term |
| `k` | \(k\) | Decay rate |
| `tau` | \(\tau\) | Exponent |
| `m_c` | \(M_c\) | Moisture floor |
| `r_offset` | \(R_{offset}\) | Resistance offset |
| `r` | — | Current resistance snapshot. **Do not use in `R(t)`.** |

Add `fetch_device_state_vector(device_id)` next to `fetch_device_status()`, using the same cache/error style (`@st.cache_data(ttl=30)`, timeout 10s, print warnings, return `(data | None, warning | None)`).

### Predicted drying time (overlay end)

**GET** `/api/v1/devices/{device_id}/status` — already fetched as `status_data` via `fetch_device_status()`.

Extract the predicted drying timestamp from the status JSON. Inspect the real payload and prefer, in order:

1. An explicit datetime field such as `predicted_drying_time`, `completion_time`, `drying_time`, `eta`, or nested equivalents
2. A documented ISO-8601 timestamp string (UTC, `Z` suffix)

Parse with the existing timestamp helpers (`format_timestamp_for_user` / `get_timezone_info`) so the overlay end lines up with the chart timezone.

If status has no usable drying-time value, skip the red overlay and log a console/print warning. Do not invent an end time.

## Model

Predicted resistance:

$$
R(t) = \left(M_0 e^{-kt} - M_c\right)^{-\tau} + R_{offset}
$$

Constraints:

- \(t\) is **minutes** since `start_time` (`t = 0` at `start_time`).
- Only generate predicted points for timestamps \(t_{abs}\) where:

  \[
  \text{now} \le t_{abs} \le \text{predicted drying time}
  \]

- Convert a chart timestamp to model time with:

  \[
  t = \frac{t_{abs} - \text{start_time}}{60\ \text{seconds}}
  \]

  using timezone-aware datetimes (do not mix naive/aware).

Numerical safety:

- Skip a sample if \(M_0 e^{-kt} - M_c \le 0\) (cannot raise a non-positive base to \(-\tau\) in general).
- Skip non-finite results (`NaN`, `inf`).
- If fewer than two valid predicted points remain, omit the dashed series.

Sampling:

- Generate a smooth curve, about **one point per minute**, capped around **200–300 points**.
- Always include the endpoints `now` and `predicted_drying_time` when they are valid.

## Implementation plan

Execute in [app.py](../app.py) only unless a helper file becomes clearly necessary. Keep functions small and next to the existing device-page API helpers.

### 1. Inventory current device-page plot flow

Confirm these existing pieces before editing:

- Device page branch: `if viewing_device:`
- Telemetry fetch + `df = process_telemetry_data(...)`
- `status_data, status_warning = fetch_device_status(device_id)`
- Plots loop over `metric_columns` and calls `plot_telemetry_metric(plot_df, metric)`
- Altair is already imported

Do not regress CSV download, status JSON, time-range selector, or other metric charts.

### 2. Add state-vector fetch

Create `fetch_device_state_vector(device_id)`:

- URL: `{API_ENDPOINT}/api/v1/devices/{device_id}/state_vector`
- Strip `device_id`
- `GET`, timeout 10s, `@st.cache_data(ttl=30)`
- 200 → `(json, None)`
- 404 / other / network → `(None, warning)` and `print` the warning

Call it on the device page alongside the existing status fetch.

### 3. Parse predicted drying time from status

Add a small helper, e.g. `extract_predicted_drying_time(status_data)`:

- Walk likely keys (including one level of nesting)
- Return a timezone-aware datetime or `None`
- Convert to the same tz as telemetry timestamps

If the live status schema uses a different field name, map that field explicitly once identified and keep the helper in one place.

### 4. Implement `R(t)` and predicted series builder

Add helpers such as:

- `resistance_from_state(m, k, tau, m_c, r_offset, t_minutes) -> float | None`
- `build_predicted_resistance_series(state_vector, now, predicted_drying_time, user_timezone) -> DataFrame`

`build_predicted_resistance_series` should:

1. Parse `start_time` as UTC, convert to user tz
2. Abort if `now >= predicted_drying_time`
3. Abort if required numeric fields are missing
4. Sample `t_abs` from `now` to `predicted_drying_time`
5. Convert each sample to minutes since `start_time`
6. Return a DataFrame with columns `timestamp`, `predicted_resistance`

Use pandas/numpy already available via pandas; do not add a new dependency.

### 5. Render a layered Altair chart

Add something like `plot_drying_time_chart(historical_df, predicted_df)`:

- Historical: `alt.Chart(...).mark_line(color="#2176FF")` on `timestamp` / `resistance`
- Predicted: `alt.Chart(...).mark_line(color="red", strokeDash=[6, 4])` on `timestamp` / `predicted_resistance`
- `alt.layer(historical, predicted).interactive()` then `st.altair_chart(..., use_container_width=True)`
- Y domain from min/max of both series, with the same padding behavior as `plot_telemetry_metric()`
- If `predicted_df` is empty, draw historical only

Reuse primary blue `#2176FF` from the dashboard CSS.

### 6. Wire into the device page layout

In the plots section, **before** the existing metric loop:

```text
Device Status (existing)
---
Drying Time chart   <-- new, top of plots
---
Telemetry Data
  Resistance (existing metric plot, keep)
  Temperature
  ...
```

Suggested order:

1. Keep **Device Status** as it is today.
2. Insert **Drying Time** chart next.
3. Then existing **Telemetry Data** metric plots.

Fetch/build prediction even if `df` is empty, but only show the overlay when timestamps are valid. If there is no historical resistance **and** no prediction, show one info message.

Extend the telemetry request `end_time` only if needed so the x-axis can include predicted drying time. Historical points still come from the selected time range; do not fabricate historical samples.

### 7. Edge cases

Handle all of these without crashing the page:

- State-vector 404 / timeout
- Status missing drying-time field
- Predicted drying time in the past
- `start_time` after `now` (still evaluate `t` from `start_time`; only plot samples in `[now, predicted_drying_time]`)
- Missing `resistance` column
- Empty telemetry for the selected range
- Non-finite model output
- Timezone mixed naive/aware datetimes
- Device IDs other than `wash0001`

On failure: print a warning, optional `emit_browser_console_warning()`, skip overlay.

### 8. Validate

- Syntax-check [app.py](../app.py)
- Manually load a device page with Streamlit (`streamlit run app.py`)
- Confirm:
  - [ ] Drying Time chart is at the top of the plots
  - [ ] Historical resistance is solid blue
  - [ ] Prediction is red dashed from now to predicted drying time
  - [ ] X-axis reaches predicted drying time
  - [ ] Other metric plots still render
  - [ ] Missing APIs degrade gracefully
  - [ ] Timezone of overlay matches historical timestamps
  - [ ] No hardcoded `wash0001`

## Out of scope

- Changing the backend model or status schema
- Replacing Altair with Plotly
- Splitting `app.py` into modules
- Adding authentication
- Removing the existing resistance metric plot



