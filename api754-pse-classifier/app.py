import streamlit as st
import pandas as pd
import json
from datetime import datetime, timezone

st.set_page_config(page_title="PSE Classifier | API RP 754", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
.main {background:#f5f7fb}
.block-container {padding-top:2rem;max-width:1200px}
.hero {background:linear-gradient(115deg,#10243a,#174b67);padding:28px 32px;border-radius:16px;color:white;margin-bottom:20px}
.hero h1 {color:white;margin:0;font-size:2rem}
.hero p {color:#d9e7f1;margin:8px 0 0}
.panel {background:white;border:1px solid #e2e8f0;border-radius:14px;padding:18px 20px;margin-bottom:14px}
.small {color:#64748b;font-size:.85rem}
.result {padding:18px;border-radius:12px;border:1px solid #dbe3ec;background:white}
.stButton>button {border-radius:9px;font-weight:600}
</style>
<div class="hero"><h1>🛡️ Process Safety Event Classifier</h1>
<p>API RP 754 • Guided Tier 1 / Tier 2 screening • Refining & Petrochemical Operations</p></div>
""", unsafe_allow_html=True)

st.warning("CONTROLLED SCREENING TOOL — This prototype is based on the publicly available API Guide to Reporting Process Safety Events decision tree. API announced the 4th Edition in August 2026 with updated cost thresholds and refined assessment guidance. Before operational use, the site owner must verify every criterion and threshold against its licensed current edition and approved corporate procedure. This tool does not replace competent review or incident investigation.")

with st.sidebar:
    st.header("Assessment settings")
    site = st.text_input("Facility / site", "Refinery")
    unit = st.text_input("Process unit / area")
    assessor = st.text_input("Assessor")
    event_id = st.text_input("Event / notification ID")
    st.divider()
    st.subheader("Site-approved thresholds")
    st.caption("Enter values from your controlled copy of the applicable API RP 754 edition / company procedure. Do not rely on illustrative defaults.")
    currency = st.selectbox("Currency", ["USD","EGP","EUR","GBP","SAR","AED"])
    tier1_fire = st.number_input("Tier 1 direct fire / explosion cost threshold", min_value=0.0, value=100000.0, step=1000.0)
    tier2_fire = st.number_input("Tier 2 direct fire / explosion cost threshold", min_value=0.0, value=25000.0, step=500.0)
    st.caption("The cost values above are editable placeholders from older public guidance, not verified 4th-edition thresholds.")
    st.divider()
    st.caption("Application build 0.1 • Decision support only")

st.markdown("### 1 · Event overview")
c1,c2,c3 = st.columns(3)
with c1: event_date = st.date_input("Event date")
with c2: event_time = st.time_input("Event time")
with c3: event_type = st.selectbox("Event type", ["Unplanned / uncontrolled release","Fire or explosion","Injury / occupational event","Other / not yet known"])

st.markdown("### 2 · Entry condition")
release = st.radio("Was there an unplanned or uncontrolled release of material from a process?", ["Yes","No","Unknown"], horizontal=True,
 help="Includes non-toxic and non-flammable materials. Evaluate whether the event meets the applicable API definition of a process and release.")
material = st.text_input("Material / substance (include mixture composition where relevant)")
release_route = st.selectbox("Release source / route", ["Process equipment / piping","Pressure relief device (PRD)","SIS / emergency depressuring","Upset emission from permitted or regulated source","Other / unknown"])
quantity = st.number_input("Estimated quantity released (kg; enter 0 if not applicable / unknown)", min_value=0.0, value=0.0, step=1.0)
duration = st.number_input("Release duration (minutes; best estimate)", min_value=0.0, value=0.0, step=1.0)

st.markdown("### 3 · Tier 1 consequence screening")
st.caption("Answer each item from verified facts. A YES to any applicable Tier 1 criterion results in Tier 1; record evidence and source.")
a,b = st.columns(2)
with a:
    employee_dafw = st.radio("Employee / contractor / subcontractor fatality or days-away-from-work injury?",["No","Yes","Unknown"],horizontal=True)
    third_party_hosp = st.radio("Third-party hospital admission or fatality?",["No","Yes","Unknown"],horizontal=True)
    community_action = st.radio("Officially declared community evacuation or shelter-in-place (including precautionary)?",["No","Yes","Unknown"],horizontal=True)
    fire_cost = st.number_input(f"Direct fire / explosion damage cost ({currency})",min_value=0.0,value=0.0,step=1000.0)
with b:
    prd_consequence = st.radio("For PRD / SIS / manual emergency depressuring discharge: did any qualifying consequence occur?",["Not applicable","No","Yes","Unknown"],horizontal=True)
    upset_consequence = st.radio("For upset emission from permitted / regulated source: did any qualifying consequence occur?",["Not applicable","No","Yes","Unknown"],horizontal=True)
    qualifying = st.multiselect("Qualifying consequences (select all that apply)",["Rainout / liquid carryover","Discharge to potentially unsafe location","Non-precautionary on-site shelter-in-place / evacuation","Public protective measures (e.g. road closure)"])
    t1_qty = st.radio("Does released quantity meet/exceed the applicable Tier 1 threshold (Table 1 / applicable category)?",["No","Yes","Unknown","Not applicable / threshold not yet determined"],horizontal=True)

st.markdown("### 4 · Tier 2 consequence screening")
c,d = st.columns(2)
with c:
    recordable = st.radio("Recordable work-related injury (not already captured as Tier 1)?",["No","Yes","Unknown"],horizontal=True)
    t2_qty = st.radio("Does released quantity meet/exceed the applicable Tier 2 threshold (Table 2 / applicable category)?",["No","Yes","Unknown","Not applicable / threshold not yet determined"],horizontal=True)
with d:
    t2_prd = st.radio("PRD / SIS / manual depressuring release meets Tier 2 quantity and consequence criteria?",["No","Yes","Unknown","Not applicable"],horizontal=True)
    t2_upset = st.radio("Upset emission meets Tier 2 quantity and consequence criteria?",["No","Yes","Unknown","Not applicable"],horizontal=True)

st.markdown("### 5 · Evidence and review")
evidence = st.text_area("Evidence / references (SAP notification, operator log, historian trend, permit, medical report, cost estimate, release calculation)",height=100)
notes = st.text_area("Additional notes / assumptions",height=80)
reviewer = st.text_input("Reviewer / process safety focal point")
confirmed = st.checkbox("I have checked the event facts and the applicable site-approved API RP 754 thresholds.")

if st.button("Run classification",type="primary",use_container_width=True):
    tier1_reasons=[]
    tier2_reasons=[]
    unresolved=[]
    if release=="No":
        outcome="NOT TIER 1 OR TIER 2 — entry condition not met"
        rationale=["No unplanned or uncontrolled process release reported."]
    elif release=="Unknown":
        outcome="HOLD — INSUFFICIENT INFORMATION"
        rationale=["Entry condition is unknown; obtain incident facts before classification."]
    else:
        if employee_dafw=="Yes": tier1_reasons.append("Employee / contractor / subcontractor fatality or days-away-from-work injury")
        if third_party_hosp=="Yes": tier1_reasons.append("Third-party hospital admission or fatality")
        if community_action=="Yes": tier1_reasons.append("Officially declared community evacuation / shelter-in-place")
        if fire_cost>=tier1_fire and fire_cost>0: tier1_reasons.append(f"Fire / explosion direct cost meets entered Tier 1 threshold ({currency} {tier1_fire:,.0f})")
        if t1_qty=="Yes": tier1_reasons.append("Release quantity meets entered / verified Tier 1 threshold")
        if prd_consequence=="Yes" and qualifying and t1_qty=="Yes": tier1_reasons.append("PRD / SIS / emergency depressuring discharge: qualifying consequence and Tier 1 quantity")
        if upset_consequence=="Yes" and qualifying and t1_qty=="Yes": tier1_reasons.append("Upset emission: qualifying consequence and Tier 1 quantity")
        if employee_dafw=="Unknown": unresolved.append("Tier 1 injury / fatality status")
        if third_party_hosp=="Unknown": unresolved.append("Third-party hospital admission / fatality status")
        if community_action=="Unknown": unresolved.append("Community protective action status")
        if t1_qty=="Unknown" or t1_qty=="Not applicable / threshold not yet determined": unresolved.append("Tier 1 chemical threshold / quantity assessment")
        if prd_consequence=="Unknown" or upset_consequence=="Unknown": unresolved.append("Release consequence assessment")
        if tier1_reasons:
            outcome="TIER 1 PSE — preliminary"
            rationale=tier1_reasons
        elif unresolved:
            outcome="HOLD — INSUFFICIENT INFORMATION"
            rationale=["No confirmed Tier 1 criterion identified, but unresolved items remain."]
        else:
            if recordable=="Yes": tier2_reasons.append("Recordable work-related injury")
            if fire_cost>=tier2_fire and fire_cost>0: tier2_reasons.append(f"Fire / explosion direct cost meets entered Tier 2 threshold ({currency} {tier2_fire:,.0f})")
            if t2_qty=="Yes": tier2_reasons.append("Release quantity meets entered / verified Tier 2 threshold")
            if t2_prd=="Yes": tier2_reasons.append("PRD / SIS / emergency depressuring discharge meets Tier 2 criteria")
            if t2_upset=="Yes": tier2_reasons.append("Upset emission meets Tier 2 criteria")
            if recordable=="Unknown" or t2_qty=="Unknown" or t2_prd=="Unknown" or t2_upset=="Unknown":
                unresolved.append("One or more Tier 2 criteria remain unknown")
            if tier2_reasons:
                outcome="TIER 2 PSE — preliminary"
                rationale=tier2_reasons
            elif unresolved:
                outcome="HOLD — INSUFFICIENT INFORMATION"
                rationale=["No confirmed Tier 1 or Tier 2 criterion identified, but unresolved items remain."]
            else:
                outcome="NOT TIER 1 OR TIER 2 — consider company-defined Tier 3 recording"
                rationale=["No Tier 1 or Tier 2 criterion was identified from the answers entered. Consider other LOPC / Tier 3 recording under the site procedure."]
    st.session_state["classification"]={"outcome":outcome,"rationale":rationale,"unresolved":unresolved,
      "event_id":event_id,"site":site,"unit":unit,"assessor":assessor,"reviewer":reviewer,"date":str(event_date),"time":str(event_time),
      "event_type":event_type,"release":release,"material":material,"source":release_route,"quantity_kg":quantity,"duration_min":duration,
      "evidence":evidence,"notes":notes,"threshold_currency":currency,"tier1_fire_threshold":tier1_fire,"tier2_fire_threshold":tier2_fire,
      "threshold_confirmation":confirmed,"generated_utc":datetime.now(timezone.utc).isoformat()}

if "classification" in st.session_state:
    r=st.session_state["classification"]
    st.divider()
    st.markdown("## Classification result")
    color="🟥" if r["outcome"].startswith("TIER 1") else "🟧" if r["outcome"].startswith("TIER 2") else "🟨" if r["outcome"].startswith("HOLD") else "🟩"
    st.markdown(f'<div class="result"><h2>{color} {r["outcome"]}</h2><p class="small">Preliminary decision-support output • Human review required</p></div>',unsafe_allow_html=True)
    for item in r["rationale"]: st.write("• "+item)
    if r["unresolved"]:
        st.error("Resolve before final approval: "+"; ".join(r["unresolved"]))
    if not r["threshold_confirmation"]:
        st.warning("Threshold confirmation box was not checked. Treat result as unverified.")
    st.markdown("### Decision record")
    st.json(r)
    csv=pd.DataFrame([{"Event ID":r["event_id"],"Outcome":r["outcome"],"Site":r["site"],"Unit":r["unit"],"Date":r["date"],"Assessor":r["assessor"],"Reviewer":r["reviewer"],"Rationale":"; ".join(r["rationale"]),"Unresolved":"; ".join(r["unresolved"]),"Evidence":r["evidence"]}]).to_csv(index=False).encode("utf-8-sig")
    st.download_button("Download classification record (CSV)",csv,file_name=f"PSE_{r['event_id'] or 'assessment'}.csv",mime="text/csv")
    st.download_button("Download full assessment (JSON)",json.dumps(r,indent=2,ensure_ascii=False).encode("utf-8"),file_name=f"PSE_{r['event_id'] or 'assessment'}.json",mime="application/json")

with st.expander("Methodology, limitations & references"):
    st.markdown("""
**Decision basis:** Publicly available API *Guide to Reporting Process Safety Events*, Appendix C (Tier 1 / Tier 2 determination decision logic tree). It describes the entry condition, Tier 1 criteria, Tier 2 criteria and the option to record other LOPC as Tier 3.

**Current edition caution:** API announced API RP 754 Fourth Edition on 6 August 2026. The announcement identifies updated direct-cost thresholds, refined guidance for fires, explosions and unignited releases, and expanded data capture. The complete licensed Fourth Edition must be used to validate and configure this application before deployment.

**Important limitations**
- Chemical / material threshold tables and mixture calculations are intentionally not embedded. They must be populated and checked against the current licensed standard and site procedure.
- The cost thresholds are editable placeholders based on older public guidance and are not represented as Fourth Edition values.
- This prototype does not establish whether an event is within the API-defined process boundary, determine chemical hazard categories, calculate release quantities, or adjudicate medical / regulatory definitions.
- An answer of “unknown” should trigger follow-up, not be treated as “no”.
- A qualified process safety reviewer must approve the final classification.
""")
    st.markdown("[API official announcement — Fourth Edition](https://www.api.org/news-policy-and-issues/news/2026/08/06/api-publishes-fourth-edition-process-safety-performance-indicators-standard)  ")
    st.markdown("[API public Guide to Reporting PSEs — Appendix C](https://www.api.org/-/media/files/oil-and-natural-gas/refining/process%20safety/api_guide_to_report_pses.pdf)")
    st.markdown("[API RP 754 publication information](https://www.api.org/products-and-services/standards)")
