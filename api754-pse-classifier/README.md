# API RP 754 PSE Screening — Windows / Browser App

A Streamlit-based, sequential screening prototype for preliminary API RP 754 Tier 1 / Tier 2 assessment. It runs locally on Windows and opens in your browser (Chrome or Edge). The Android APK is maintained separately in `api754-android/`.

## Quick start on Windows

1. Install **Python 3.11 or newer** from https://www.python.org/downloads/windows/
2. During installation, select **Add Python to PATH**.
3. Download this repository as a ZIP from GitHub and extract it.
4. Open the extracted folder, then open `api754-pse-classifier`.
5. Double-click **Run_API754_Windows.bat**.
6. The first launch creates a local Python environment and installs the required packages. The app then opens in your browser at `http://localhost:8501`.
7. Keep the black command window open while using the application. Press **Ctrl+C** in that window to stop it.

If Windows cannot find Python, install Python and restart the command prompt / launcher.

## Run manually

```powershell
cd api754-pse-classifier
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Features

- One-stage-at-a-time guided screening wizard with Back / Next navigation
- Preliminary Tier 1 / Tier 2 / hold outcome with rationale and unresolved items
- Event details, assessor, reviewer, evidence and assumptions
- Editable site threshold inputs
- Downloadable full Word assessment report (.docx)
- CSV and JSON decision-record exports
- Runs locally on the laptop; assessment data is not automatically sent to a hosted server

## Important safety and compliance notice

This is a decision-support prototype, not an approved compliance tool. Its decision structure is based on the publicly available API *Guide to Reporting Process Safety Events*, Appendix C. API announced the Fourth Edition of API RP 754 on 6 August 2026.

Before operational deployment, the process safety owner must validate the complete logic, terminology, definitions, tables, chemical thresholds, mixture rules, cost thresholds and examples against the licensed current edition and the site's approved procedure. The current app requires site-approved thresholds to be entered; displayed legacy cost values are placeholders only.

No classification should be finalized automatically where facts or threshold calculations are unknown. Human review and formal incident investigation remain mandatory. The app is not API-certified and does not establish API compliance.

## References

- [API — Fourth Edition announcement (6 August 2026)](https://www.api.org/news-policy-and-issues/news/2026/08/06/api-publishes-fourth-edition-process-safety-performance-indicators-standard)
- [API — Guide to Reporting Process Safety Events (Appendix C)](https://www.api.org/-/media/files/oil-and-gas/refining/process%20safety/api_guide_to_report_pses.pdf)
- [API — RP 754 publication information](https://www.api.org/products-and-services/standards)

## Not production-ready

No authentication, database, electronic signatures, immutable audit log, role-based access, cybersecurity review, validation test suite or deployment hardening is included. Do not use it as the sole basis for regulatory or corporate reporting.
