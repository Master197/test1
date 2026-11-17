# PSE Classifier — API RP 754

A Streamlit-based, operator-guided screening prototype for preliminary API RP 754 Tier 1 / Tier 2 classification.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Important safety and compliance notice

This is a decision-support prototype, not an approved compliance tool. Its decision structure is based on the publicly available API *Guide to Reporting Process Safety Events*, Appendix C. API announced the Fourth Edition of API RP 754 on 6 August 2026, including updated direct-cost thresholds and refined event assessment guidance.

Before operational deployment, the process safety owner must validate the complete logic, terminology, definitions, tables, chemical thresholds, mixture rules, cost thresholds and examples against the licensed current edition and the site's approved procedure. The current app deliberately requires site-approved thresholds to be entered; the displayed legacy cost values are placeholders only.

No classification should be finalized automatically where facts or threshold calculations are unknown. Human review and formal incident investigation remain mandatory.

## Features

- Guided operator questionnaire
- Sequential Tier 1 then Tier 2 screening
- Explicit unknown / hold state
- Evidence and reviewer fields
- Editable site thresholds
- CSV and JSON assessment export
- Methodology and limitations panel

## References

- [API — Fourth Edition announcement (6 August 2026)](https://www.api.org/news-policy-and-issues/news/2026/08/06/api-publishes-fourth-edition-process-safety-performance-indicators-standard)
- [API — Guide to Reporting Process Safety Events (Appendix C)](https://www.api.org/-/media/files/oil-and-natural-gas/refining/process%20safety/api_guide_to_report_pses.pdf)

## Not production-ready

No authentication, database, electronic signatures, audit-log immutability, role-based access, cybersecurity review, validation test suite or deployment hardening is included in this prototype. Add these before commercial or site-wide use.
