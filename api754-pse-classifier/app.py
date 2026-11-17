import streamlit as st
import pandas as pd
import json
import io
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime, timezone

st.set_page_config(page_title="API 754 | PSE Screening", page_icon="🛡️", layout="wide")

def build_word_report(record):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    title = doc.add_heading("Process Safety Event Screening Report", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("API RP 754 — Preliminary Tier 1 / Tier 2 decision-support assessment")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("CONTROLLED SCREENING OUTPUT — Human review and verification against the licensed applicable API RP 754 edition and approved site procedure are required.")
    doc.add_heading("1. Screening outcome", level=1)
    doc.add_heading(record.get("outcome", "Not classified"), level=2)
    for item in record.get("rationale", []):
        doc.add_paragraph(item, style="List Bullet")
    if record.get("unresolved"):
        doc.add_heading("Items requiring resolution", level=2)
        for item in record["unresolved"]:
            doc.add_paragraph(item, style="List Bullet")
    doc.add_heading("2. Event and assessment details", level=1)
    details = [
        ("Event / notification ID", record.get("event_id")),
        ("Facility / site", record.get("site")),
        ("Process unit / area", record.get("unit")),
        ("Event date", record.get("date")),
        ("Event time", record.get("time")),
        ("Event type", record.get("event_type")),
        ("Material / substance", record.get("material")),
        ("Release reported", record.get("release")),
        ("Release source / route", record.get("source")),
        ("Estimated quantity (kg)", record.get("quantity_kg")),
        ("Estimated duration (minutes)", record.get("duration_min")),
        ("Assessor", record.get("assessor")),
        ("Reviewer", record.get("reviewer")),
    ]
    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    for label, value in details:
        cells = table.add_row().cells
        cells[0].text = str(label)
        cells[1].text = "" if value is None else str(value)
    doc.add_heading("3. Screening answers", level=1)
    answers = record.get("answers", {})
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = "Question / field"
    table.rows[0].cells[1].text = "Recorded answer"
    for key, value in answers.items():
        cells = table.add_row().cells
        cells[0].text = str(key)
        cells[1].text = ", ".join(map(str, value)) if isinstance(value, list) else str(value)
    doc.add_heading("4. Thresholds and confirmation", level=1)
    doc.add_paragraph(f"Currency: {record.get('threshold_currency', '')}")
    doc.add_paragraph(f"Entered Tier 1 fire / explosion cost threshold: {record.get('threshold_currency', '')} {record.get('tier1_fire_threshold', '')}")
    doc.add_paragraph(f"Entered Tier 2 fire / explosion cost threshold: {record.get('threshold_currency', '')} {record.get('tier2_fire_threshold', '')}")
    doc.add_paragraph(f"Assessor confirmed threshold review: {'Yes' if record.get('threshold_confirmation') else 'No'}")
    doc.add_paragraph("Entered thresholds are site inputs. Confirm that they match the controlled current standard and approved site procedure; this report does not validate them.")
    doc.add_heading("5. Evidence and notes", level=1)
    doc.add_paragraph("Evidence / references:")
    doc.add_paragraph(record.get("evidence") or "Not provided")
    doc.add_paragraph("Additional notes / assumptions:")
    doc.add_paragraph(record.get("notes") or "Not provided")
    doc.add_heading("6. Methodology, limitations and approval", level=1)
    doc.add_paragraph("This is a preliminary screening record only. It does not replace incident investigation, competent process safety review, or the site's formal reporting and approval process.")
    doc.add_paragraph("Chemical thresholds, mixture calculations, definitions, special release-route rules and cost thresholds must be checked against the licensed applicable edition of API RP 754 and the approved company procedure.")
    doc.add_paragraph("No API certification or compliance determination is represented by this application.")
    doc.add_paragraph(f"Report generated (UTC): {record.get('generated_utc', '')}")
    doc.add_paragraph(f"Reviewer: {record.get('reviewer') or 'Not specified'}")
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output.getvalue()


st.markdown("""
<style>
.block-container{max-width:1050px;padding-top:1.8rem;padding-bottom:3rem}
.hero{background:linear-gradient(115deg,#10243a,#174b67);padding:25px 30px;border-radius:16px;color:#fff;margin-bottom:18px}
.hero h1{color:#fff;margin:0;font-size:1.9rem}
.hero p{color:#d9e7f1;margin:7px 0 0}
.step-card{background:#f3f6fa;border:1px solid #dce5ef;padding:15px 18px;border-radius:12px;margin:10px 0 18px}
div.stButton>button{border-radius:9px;font-weight:600;min-height:2.7rem}
div[data-testid="stProgress"]>div>div{background-color:#176b87}
.small-note{color:#64748b;font-size:.88rem}
</style>
<div class="hero"><h1>🛡️ Process Safety Event Classifier</h1>
<p>API RP 754 • Sequential Tier 1 / Tier 2 screening • Refining & Petrochemical Operations</p></div>
""", unsafe_allow_html=True)

st.warning("CONTROLLED SCREENING TOOL — This prototype is based on the publicly available API Guide to Reporting Process Safety Events decision tree. API announced the 4th Edition in August 2026 with updated cost thresholds and refined assessment guidance. Verify every criterion and threshold against your licensed current edition and approved corporate procedure. This tool does not replace competent review or incident investigation.")

if "step" not in st.session_state:
    st.session_state.step = 0

STEPS = ["Event details", "Entry condition", "Tier 1 screening", "Tier 2 screening", "Evidence & review"]
step = st.session_state.step

with st.sidebar:
    st.header("Assessment record")
    st.text_input("Facility / site", "Refinery", key="site")
    st.text_input("Process unit / area", key="unit")
    st.text_input("Assessor", key="assessor")
    st.text_input("Event / notification ID", key="event_id")
    st.divider()
    st.subheader("Site-approved thresholds")
    st.caption("Enter values from your controlled copy of the applicable API RP 754 edition / company procedure. Illustrative defaults must not be used for official classification.")
    st.selectbox("Currency", ["USD", "EGP", "EUR", "GBP", "SAR", "AED"], key="currency")
    st.number_input("Tier 1 direct fire / explosion cost threshold", min_value=0.0, value=100000.0, step=1000.0, key="tier1_fire")
    st.number_input("Tier 2 direct fire / explosion cost threshold", min_value=0.0, value=25000.0, step=500.0, key="tier2_fire")
    st.caption("Cost values are editable placeholders, not verified 4th-edition thresholds.")
    st.divider()
    if st.button("Start new assessment", use_container_width=True):
        for k in ["event_date","event_time","event_type","release","material","release_route","quantity","duration",
                  "employee_dafw","third_party_hosp","community_action","fire_cost","prd_consequence",
                  "upset_consequence","qualifying","t1_qty","recordable","t2_qty","t2_prd","t2_upset",
                  "evidence","notes","reviewer","confirmed","classification"]:
            st.session_state.pop(k, None)
        st.session_state.step = 0
        st.rerun()
    st.caption("Build 0.2 • Guided decision support")

if step < len(STEPS):
    st.markdown(f"### Step {step + 1} of {len(STEPS)} — {STEPS[step]}")
    st.progress((step + 1) / len(STEPS))
    st.markdown(f'<div class="step-card"><b>{STEPS[step]}</b><br><span class="small-note">Complete this stage, then use Next to continue. Your answers remain available when you go back.</span></div>', unsafe_allow_html=True)
else:
    st.markdown("### Assessment complete")

def navigation():
    left, right = st.columns([1, 1])
    with left:
        if step > 0 and st.button("← Back", use_container_width=True):
            st.session_state.step -= 1
            st.rerun()
    with right:
        if step < len(STEPS) - 1 and st.button("Next step →", type="primary", use_container_width=True):
            st.session_state.step += 1
            st.rerun()

if step == 0:
    st.subheader("Identify the event")
    a, b = st.columns(2)
    with a:
        st.date_input("Event date", key="event_date")
        st.time_input("Event time", key="event_time")
    with b:
        st.selectbox("Event type", ["Unplanned / uncontrolled release", "Fire or explosion", "Injury / occupational event", "Other / not yet known"], key="event_type")
        st.text_input("Material / substance (if known)", key="material")
    st.info("Start with the event facts. Do not decide the tier at this stage.")
    navigation()

elif step == 1:
    st.subheader("API reporting entry condition")
    st.radio("Was there an unplanned or uncontrolled release of material from a process?",
             ["Yes", "No", "Unknown"], horizontal=True, key="release",
             help="Includes non-toxic and non-flammable materials. Confirm the applicable API definitions of process and release.")
    st.selectbox("Release source / route",
                 ["Process equipment / piping", "Pressure relief device (PRD)", "SIS / emergency depressuring",
                  "Upset emission from permitted or regulated source", "Other / unknown"], key="release_route")
    a, b = st.columns(2)
    with a:
        st.number_input("Estimated quantity released (kg)", min_value=0.0, value=0.0, step=1.0, key="quantity")
    with b:
        st.number_input("Estimated release duration (minutes)", min_value=0.0, value=0.0, step=1.0, key="duration")
    if st.session_state.get("release") == "No":
        st.success("If confirmed, the API PSE entry condition is not met. Continue to document the assessment and consider other site reporting requirements.")
    elif st.session_state.get("release") == "Unknown":
        st.warning("The entry condition is unresolved. The final outcome will be placed on hold unless clarified.")
    navigation()

elif step == 2:
    st.subheader("Tier 1 — consequence screening")
    st.caption("Answer from verified facts. A confirmed applicable Tier 1 criterion takes precedence over Tier 2.")
    st.radio("Employee / contractor / subcontractor fatality or days-away-from-work injury?",
             ["No", "Yes", "Unknown"], horizontal=True, key="employee_dafw")
    st.radio("Third-party hospital admission or fatality?",
             ["No", "Yes", "Unknown"], horizontal=True, key="third_party_hosp")
    st.radio("Officially declared community evacuation or shelter-in-place (including precautionary)?",
             ["No", "Yes", "Unknown"], horizontal=True, key="community_action")
    st.number_input("Direct fire / explosion damage cost", min_value=0.0, value=0.0, step=1000.0, key="fire_cost")
    st.divider()
    st.markdown("**Special release routes**")
    st.radio("For PRD / SIS / manual emergency depressuring discharge: did a qualifying consequence occur?",
             ["Not applicable", "No", "Yes", "Unknown"], horizontal=True, key="prd_consequence")
    st.radio("For upset emission from permitted / regulated source: did a qualifying consequence occur?",
             ["Not applicable", "No", "Yes", "Unknown"], horizontal=True, key="upset_consequence")
    st.multiselect("Qualifying consequences (select all supported by evidence)",
                   ["Rainout / liquid carryover", "Discharge to potentially unsafe location",
                    "Non-precautionary on-site shelter-in-place / evacuation",
                    "Public protective measures (e.g. road closure)"], key="qualifying")
    st.radio("Does released quantity meet/exceed the applicable Tier 1 threshold (Table 1 / applicable category)?",
             ["No", "Yes", "Unknown", "Not applicable / threshold not yet determined"],
             horizontal=True, key="t1_qty")
    st.warning("Chemical thresholds and mixture calculations are not built into this prototype. Confirm the applicable material category, quantity and threshold from the licensed standard.")
    navigation()

elif step == 3:
    st.subheader("Tier 2 — consequence screening")
    st.caption("Complete Tier 2 screening only after checking Tier 1 criteria.")
    st.radio("Recordable work-related injury (not already captured as Tier 1)?",
             ["No", "Yes", "Unknown"], horizontal=True, key="recordable")
    st.radio("Does released quantity meet/exceed the applicable Tier 2 threshold (Table 2 / applicable category)?",
             ["No", "Yes", "Unknown", "Not applicable / threshold not yet determined"],
             horizontal=True, key="t2_qty")
    st.radio("PRD / SIS / manual depressuring release meets Tier 2 quantity and consequence criteria?",
             ["No", "Yes", "Unknown", "Not applicable"], horizontal=True, key="t2_prd")
    st.radio("Upset emission meets Tier 2 quantity and consequence criteria?",
             ["No", "Yes", "Unknown", "Not applicable"], horizontal=True, key="t2_upset")
    st.info("Do not mark a criterion Yes unless the applicable API definition and supporting evidence have been checked.")
    navigation()

elif step == 4:
    st.subheader("Evidence, assumptions and review")
    if st.button("← Back to Tier 2 screening", use_container_width=True):
        st.session_state.step = 3
        st.rerun()
    st.text_area("Evidence / references (SAP notification, operator log, historian trend, permit, medical report, cost estimate, release calculation)", height=120, key="evidence")
    st.text_area("Additional notes / assumptions", height=90, key="notes")
    st.text_input("Reviewer / process safety focal point", key="reviewer")
    st.checkbox("I have checked the event facts and the applicable site-approved API RP 754 thresholds.", key="confirmed")
    st.divider()
    st.caption("When you run the screening, the application will show the preliminary tier, reasons, unresolved items and a downloadable decision record.")
    if st.button("Run classification", type="primary", use_container_width=True):
        tier1_reasons, tier2_reasons, unresolved = [], [], []
        release = st.session_state.get("release", "Unknown")
        if release == "No":
            outcome = "NOT TIER 1 OR TIER 2 — entry condition not met"
            rationale = ["No unplanned or uncontrolled process release reported."]
        elif release == "Unknown":
            outcome = "HOLD — INSUFFICIENT INFORMATION"
            rationale = ["Entry condition is unknown; obtain incident facts before classification."]
        else:
            if st.session_state.get("employee_dafw") == "Yes":
                tier1_reasons.append("Employee / contractor / subcontractor fatality or days-away-from-work injury")
            if st.session_state.get("third_party_hosp") == "Yes":
                tier1_reasons.append("Third-party hospital admission or fatality")
            if st.session_state.get("community_action") == "Yes":
                tier1_reasons.append("Officially declared community evacuation / shelter-in-place")
            fire_cost = st.session_state.get("fire_cost", 0.0)
            if fire_cost > 0 and fire_cost >= st.session_state.get("tier1_fire", 100000.0):
                tier1_reasons.append(f"Fire / explosion direct cost meets entered Tier 1 threshold ({st.session_state.get('currency')} {st.session_state.get('tier1_fire'):,.0f})")
            if st.session_state.get("t1_qty") == "Yes":
                tier1_reasons.append("Release quantity meets entered / verified Tier 1 threshold")
            qualifying = st.session_state.get("qualifying", [])
            if st.session_state.get("prd_consequence") == "Yes" and qualifying and st.session_state.get("t1_qty") == "Yes":
                tier1_reasons.append("PRD / SIS / emergency depressuring discharge: qualifying consequence and Tier 1 quantity")
            if st.session_state.get("upset_consequence") == "Yes" and qualifying and st.session_state.get("t1_qty") == "Yes":
                tier1_reasons.append("Upset emission: qualifying consequence and Tier 1 quantity")
            for key, label in [
                ("employee_dafw", "Tier 1 injury / fatality status"),
                ("third_party_hosp", "Third-party hospital admission / fatality status"),
                ("community_action", "Community protective action status")]:
                if st.session_state.get(key) == "Unknown":
                    unresolved.append(label)
            if st.session_state.get("t1_qty") in ["Unknown", "Not applicable / threshold not yet determined"]:
                unresolved.append("Tier 1 chemical threshold / quantity assessment")
            if st.session_state.get("prd_consequence") == "Unknown" or st.session_state.get("upset_consequence") == "Unknown":
                unresolved.append("Release consequence assessment")
            if tier1_reasons:
                outcome, rationale = "TIER 1 PSE — preliminary", tier1_reasons
            elif unresolved:
                outcome, rationale = "HOLD — INSUFFICIENT INFORMATION", ["No confirmed Tier 1 criterion identified, but unresolved items remain."]
            else:
                if st.session_state.get("recordable") == "Yes":
                    tier2_reasons.append("Recordable work-related injury")
                if fire_cost > 0 and fire_cost >= st.session_state.get("tier2_fire", 25000.0):
                    tier2_reasons.append(f"Fire / explosion direct cost meets entered Tier 2 threshold ({st.session_state.get('currency')} {st.session_state.get('tier2_fire'):,.0f})")
                if st.session_state.get("t2_qty") == "Yes":
                    tier2_reasons.append("Release quantity meets entered / verified Tier 2 threshold")
                if st.session_state.get("t2_prd") == "Yes":
                    tier2_reasons.append("PRD / SIS / manual depressuring release meets Tier 2 criteria")
                if st.session_state.get("t2_upset") == "Yes":
                    tier2_reasons.append("Upset emission meets Tier 2 criteria")
                if any(st.session_state.get(k) == "Unknown" for k in ["recordable", "t2_qty", "t2_prd", "t2_upset"]):
                    unresolved.append("One or more Tier 2 criteria remain unknown")
                if tier2_reasons:
                    outcome, rationale = "TIER 2 PSE — preliminary", tier2_reasons
                elif unresolved:
                    outcome, rationale = "HOLD — INSUFFICIENT INFORMATION", ["No confirmed Tier 1 or Tier 2 criterion identified, but unresolved items remain."]
                else:
                    outcome = "NOT TIER 1 OR TIER 2 — consider company-defined Tier 3 recording"
                    rationale = ["No Tier 1 or Tier 2 criterion was identified from the answers entered. Consider other LOPC / Tier 3 recording under the site procedure."]
        record = {
            "outcome": outcome, "rationale": rationale, "unresolved": unresolved,
            "event_id": st.session_state.get("event_id", ""), "site": st.session_state.get("site", ""),
            "unit": st.session_state.get("unit", ""), "assessor": st.session_state.get("assessor", ""),
            "reviewer": st.session_state.get("reviewer", ""), "date": str(st.session_state.get("event_date", "")),
            "time": str(st.session_state.get("event_time", "")), "event_type": st.session_state.get("event_type", ""),
            "release": release, "material": st.session_state.get("material", ""),
            "source": st.session_state.get("release_route", ""), "quantity_kg": st.session_state.get("quantity", 0.0),
            "duration_min": st.session_state.get("duration", 0.0), "evidence": st.session_state.get("evidence", ""),
            "notes": st.session_state.get("notes", ""), "threshold_currency": st.session_state.get("currency", ""),
            "tier1_fire_threshold": st.session_state.get("tier1_fire", 0.0),
            "tier2_fire_threshold": st.session_state.get("tier2_fire", 0.0),
            "threshold_confirmation": st.session_state.get("confirmed", False),
            "tier1_fire_threshold": st.session_state.get("tier1_fire", 0.0),
            "tier2_fire_threshold": st.session_state.get("tier2_fire", 0.0),
            "answers": {
                "Entry condition — unplanned / uncontrolled process release": st.session_state.get("release", "Unknown"),
                "Release source / route": st.session_state.get("release_route", ""),
                "Estimated quantity (kg)": st.session_state.get("quantity", 0.0),
                "Estimated duration (minutes)": st.session_state.get("duration", 0.0),
                "Employee / contractor fatality or days-away-from-work injury": st.session_state.get("employee_dafw", "Not answered"),
                "Third-party hospital admission or fatality": st.session_state.get("third_party_hosp", "Not answered"),
                "Community evacuation / shelter-in-place": st.session_state.get("community_action", "Not answered"),
                "Direct fire / explosion damage cost": st.session_state.get("fire_cost", 0.0),
                "PRD / SIS / emergency depressuring consequence": st.session_state.get("prd_consequence", "Not answered"),
                "Upset emission consequence": st.session_state.get("upset_consequence", "Not answered"),
                "Qualifying consequences": st.session_state.get("qualifying", []),
                "Tier 1 quantity threshold status": st.session_state.get("t1_qty", "Not answered"),
                "Recordable work-related injury": st.session_state.get("recordable", "Not answered"),
                "Tier 2 quantity threshold status": st.session_state.get("t2_qty", "Not answered"),
                "PRD / SIS Tier 2 criteria": st.session_state.get("t2_prd", "Not answered"),
                "Upset emission Tier 2 criteria": st.session_state.get("t2_upset", "Not answered"),
            },
            "generated_utc": datetime.now(timezone.utc).isoformat()
        }
        st.session_state["classification"] = record
        st.session_state.step = 5
        st.rerun()

if st.session_state.step == 5 and "classification" in st.session_state:
    r = st.session_state["classification"]
    st.divider()
    st.markdown("## Screening result")
    st.markdown(f"### {r['outcome']}")
    st.caption("Preliminary decision-support output • Human review required")
    for item in r["rationale"]:
        st.write("• " + item)
    if r["unresolved"]:
        st.error("Resolve before final approval: " + "; ".join(r["unresolved"]))
    if not r["threshold_confirmation"]:
        st.warning("Threshold confirmation was not checked. Treat this result as unverified.")
    st.markdown("### Decision record")
    st.json(r)
    csv = pd.DataFrame([{
        "Event ID": r["event_id"], "Outcome": r["outcome"], "Site": r["site"], "Unit": r["unit"],
        "Date": r["date"], "Assessor": r["assessor"], "Reviewer": r["reviewer"],
        "Rationale": "; ".join(r["rationale"]), "Unresolved": "; ".join(r["unresolved"]),
        "Evidence": r["evidence"]
    }]).to_csv(index=False).encode("utf-8-sig")
    report_docx = build_word_report(r)
    st.download_button("Download full assessment report (Word)", report_docx,
                       file_name=f"PSE_{r['event_id'] or 'assessment'}_report.docx",
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                       type="primary")
    st.download_button("Download classification record (CSV)", csv,
                       file_name=f"PSE_{r['event_id'] or 'assessment'}.csv", mime="text/csv")
    st.download_button("Download full assessment (JSON)",
                       json.dumps(r, indent=2, ensure_ascii=False).encode("utf-8"),
                       file_name=f"PSE_{r['event_id'] or 'assessment'}.json", mime="application/json")
    if st.button("← Review / edit answers", use_container_width=True):
        st.session_state.step = 0
        st.rerun()
    if st.button("Start another assessment", type="primary", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k not in ["step"]:
                st.session_state.pop(k, None)
        st.session_state.step = 0
        st.rerun()

with st.expander("Methodology, limitations & references"):
    st.markdown("""
**Decision basis:** Publicly available API *Guide to Reporting Process Safety Events*, Appendix C (Tier 1 / Tier 2 determination decision logic tree).

**Current edition caution:** API announced API RP 754 Fourth Edition on 6 August 2026. Validate the complete licensed Fourth Edition and corporate procedure before operational use.

**Important limitations**
- Chemical / material threshold tables and mixture calculations are not embedded.
- Cost thresholds are editable placeholders and are not represented as verified Fourth Edition values.
- This prototype does not determine process boundaries, chemical hazard categories, release quantities, or medical / regulatory definitions.
- Unknown answers must trigger follow-up, not be treated as No.
- A qualified process safety reviewer must approve the final classification.
""")
    st.markdown("[API official announcement — Fourth Edition](https://www.api.org/news-policy-and-issues/news/2026/08/06/api-publishes-fourth-edition-process-safety-performance-indicators-standard)")
    st.markdown("[API public Guide to Reporting PSEs — Appendix C](https://www.api.org/-/media/files/oil-and-natural-gas/refining/process%20safety/api_guide_to_report_pses.pdf)")
    st.markdown("[API RP 754 publication information](https://www.api.org/products-and-services/standards)")
