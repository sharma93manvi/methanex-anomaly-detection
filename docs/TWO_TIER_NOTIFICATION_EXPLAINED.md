# Two-Tier Notification System – Presentation Guide

## How to Explain It in Your Presentation

### 1. What Is the Two-Tier Notification System?

We use a **two-tier** alert system so operators get the right level of attention at the right time:

| Tier | Name | When It Fires | Purpose |
|------|------|----------------|---------|
| **Tier 1** | **Early Warning** | As soon as an anomaly is **first detected** (start of a new anomaly period) | Immediate awareness: “Something just went out of range.” |
| **Tier 2** | **Priority Escalation** | When the **same** anomaly has been present for **3+ hours** (configurable) | Escalation: “This isn’t a blip; it needs attention.” |

- **Early Warning** = first sign of trouble (one notification per new anomaly period).  
- **Priority Escalation** = sustained trouble (one escalation per period, only after 3+ hours).

This reduces noise from short spikes and highlights persistent issues.

---

### 2. Where Is It Implemented? (Backend)

- **Module:** `src/notification_system.py`  
- **Class:** `NotificationManager`  
- **Config:** `config.py`  
  - `NOTIFICATION_ESCALATION_HOURS = 3`  
  - `SUSTAINED_ANOMALY_DURATION = 3` (same 3 hours used for “sustained” anomaly in detection)

**Logic in short:**

1. Pipeline produces a dataframe with an `anomaly_combined` flag and `Timestamp`.
2. `NotificationManager.process_anomaly_detection(df, asset_name)` walks the data in time order.
3. **Tier 1 – Early Warning:** On the **first** row where `anomaly_combined` is True in a new continuous block, it calls `send_early_warning(asset, timestamp, details)`.
4. **Tier 2 – Priority Escalation:** For that same block, once duration from start ≥ 3 hours, it calls `send_priority_escalation(asset, timestamp, duration_hours, details)` (once per period).
5. Notifications are logged to console (and to `notifications.log` when enabled) and stored in `notification_manager.notifications` for summaries.

So **yes, the app backend is actually following a two-tier notification system** whenever the **full pipeline** runs and calls `NotificationManager`.

---

### 3. When Does the Two-Tier System Run?

| Context | Two-tier notifications run? | What the user sees |
|--------|------------------------------|--------------------|
| **Full pipeline** (e.g. `python src/main.py` or notebook end-to-end) | **Yes** – `NotificationManager` runs on combined results for Asset 1 and Asset 2. | Console + log file; batch summary at the end. |
| **Pipeline service** (`services/pipeline_service.process_pipeline_with_progress`) | **Yes** – same pipeline, same `NotificationManager`. | Today: only if the caller uses the returned notification summary (see below). |
| **Streamlit – Upload & Analyze** | **No** – this path uses **model inference only** (e.g. `ModelManager.predict_on_new_data`), not the full pipeline. | Early warning **indicators** and **recommendation priorities** (Critical / High / Medium / Low), which are related but not the same as the two-tier events. |
| **Streamlit – Mock Stream** | **No** – demo uses phases (Normal → Early Warning → Anomaly) and recommendation priorities. | Phase labels and “Recommended Actions” with priority; no `NotificationManager` calls. |

So:

- **Two-tier system:** Implemented and runs in **batch/full pipeline** (main.py, notebook, or pipeline_service).
- **Streamlit app:** Uses **inference + recommendations**; the UI shows “early warning” in the sense of indicators and priorities, not the same two-tier event stream (unless we surface pipeline notifications in the app; see below).

---

### 4. One-Liner for the Presentation

- **Technical:** “We implement a two-tier notification system: **Early Warning** when an anomaly is first detected, and **Priority Escalation** when it persists for 3 or more hours. It runs in our batch pipeline and is logged; the Streamlit app shows related early-warning indicators and prioritized recommendations.”
- **Business:** “Operators get an immediate early warning when something goes out of range, and a second, higher-priority alert if the issue is still there after 3 hours, so we focus attention on sustained problems instead of brief spikes.”

---

### 5. Optional: Showing Two-Tier Notifications in the Streamlit App

To show the **actual** two-tier notifications in the app:

1. **When full pipeline runs** (e.g. a “Run full pipeline” flow using `pipeline_service`):
   - Have `process_pipeline_with_progress` return the notification summary (and optionally the list of events) from `NotificationManager`.
   - In the Streamlit page that runs the pipeline, display a “Notification summary” section: counts of Early Warnings and Priority Escalations per asset, and optionally the last N events.

2. **Where it runs:**  
   Right now no Streamlit page calls `process_pipeline_with_progress`. Adding a “Run full pipeline” (or “Batch analysis”) option that calls it and then shows the returned notification summary would make the two-tier system visible in the UI.

**Note:** `process_pipeline_with_progress()` now returns `results['notifications']` with:
- `summary`: full text summary (Early Warnings + Priority Escalations by asset)
- `list`: all notification events (each with `type`, `asset`, `timestamp`, `message`, `details`)
- `early_warning_count`, `escalation_count`: counts for quick display
