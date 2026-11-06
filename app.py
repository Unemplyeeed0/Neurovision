import os, sqlite3, random
from datetime import datetime, date
import pandas as pd
import streamlit as st

DB = os.getenv("NEUROVISION_DB", "neurovision.db")
st.set_page_config(page_title="NeuroVision Therapy", page_icon="👁️", layout="wide")

def db():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.execute("""CREATE TABLE IF NOT EXISTS patients(
        patient_id TEXT PRIMARY KEY, display_name TEXT, age INTEGER, created_at TEXT, notes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS assessments(
        id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, date TEXT, diagnosis_label TEXT,
        npc_cm REAL, near_phoria_pd REAL, distance_phoria_pd REAL, pfv_break REAL,
        nfv_break REAL, accommodative_amplitude REAL, maf_cpm REAL, baf_cpm REAL,
        stereo_arcsec REAL, symptom_score REAL, notes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS plans(
        id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, created_at TEXT, clinician TEXT,
        target_domain TEXT, activity TEXT, instructions TEXT, duration_min INTEGER,
        frequency TEXT, progression_rule TEXT, review_date TEXT, status TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, plan_id INTEGER, date TEXT,
        activity TEXT, duration_min INTEGER, completion TEXT, feedback TEXT, clinician_notes TEXT)""")
    c.commit()
    return c

conn = db()
st.title("👁️ NeuroVision Therapy")
st.caption("SEE • THINK • TRAIN | Clinical workflow + child-friendly home engagement")
st.warning("MVP / NOT A MEDICAL DEVICE. No diagnosis, prescribing, calibrated vergence/accommodation stimulus, eye tracking or validated outcome measurement. No login/access controls in this prototype. Use fictional/demo data only; do not enter identifiable patient or health information into public/unapproved hosting.")
role = st.sidebar.radio("Workspace", ["Clinician portal", "Patient / parent portal", "Evidence library"])

def patients_df():
    return pd.read_sql_query("SELECT * FROM patients ORDER BY created_at DESC", conn)

if role == "Clinician portal":
    tabs = st.tabs(["Dashboard", "Patients", "Assessment", "Therapy plans", "Session log", "Outcomes"])
    pts = patients_df()
    with tabs[0]:
        plans = pd.read_sql_query("SELECT * FROM plans WHERE status='Active'", conn)
        sessions = pd.read_sql_query("SELECT * FROM sessions", conn)
        a,b,c = st.columns(3)
        a.metric("Demo patients",len(pts)); b.metric("Active plans",len(plans)); c.metric("Logged sessions",len(sessions))
        st.write("Workflow: register pseudonymous patient → record clinician-measured baseline → create individualized plan → log sessions → review outcomes.")
        st.info("The app does not auto-diagnose or automatically select therapy.")
        if not pts.empty: st.dataframe(pts[["patient_id","display_name","age","created_at"]],use_container_width=True,hide_index=True)
    with tabs[1]:
        st.subheader("Register a pseudonymous patient")
        with st.form("patient"):
            pid=st.text_input("Patient code (e.g. NV-001)")
            name=st.text_input("Display name / initials")
            age=st.number_input("Age",1,100,10)
            notes=st.text_area("Non-identifying notes")
            save=st.form_submit_button("Save patient")
        if save:
            try:
                conn.execute("INSERT INTO patients VALUES (?,?,?,?,?)",(pid.strip(),name.strip(),int(age),datetime.now().isoformat(timespec="seconds"),notes))
                conn.commit(); st.success("Patient saved.")
            except sqlite3.IntegrityError: st.error("Patient code already exists.")
    with tabs[2]:
        pts=patients_df()
        if pts.empty: st.info("Register a demo patient first.")
        else:
            pid=st.selectbox("Patient",pts.patient_id.tolist(),key="assess_pid")
            with st.form("assessment"):
                d=st.date_input("Assessment date",date.today())
                diagnosis=st.text_input("Clinician's diagnostic impression")
                x=st.columns(3)
                npc=x[0].number_input("NPC break (cm)",0.0,100.0,0.0,0.5)
                near=x[1].number_input("Near phoria (Δ; exo + / eso −)",-100.0,100.0,0.0,0.5)
                dist=x[2].number_input("Distance phoria (Δ; exo + / eso −)",-100.0,100.0,0.0,0.5)
                y=st.columns(3)
                pfv=y[0].number_input("PFV break (Δ)",0.0,100.0,0.0,0.5)
                nfv=y[1].number_input("NFV break (Δ)",0.0,100.0,0.0,0.5)
                aa=y[2].number_input("Amplitude of accommodation (D)",0.0,30.0,0.0,0.25)
                z=st.columns(3)
                maf=z[0].number_input("MAF (cpm)",0.0,100.0,0.0,0.5)
                baf=z[1].number_input("BAF (cpm)",0.0,100.0,0.0,0.5)
                stereo=z[2].number_input("Stereoacuity (arcsec)",0.0,10000.0,0.0,10.0)
                symptom=st.number_input("Symptom score (identify instrument in notes)",0.0,200.0,0.0,1.0)
                notes=st.text_area("Test method, correction worn, target, reliability and notes")
                save=st.form_submit_button("Save assessment")
            if save:
                conn.execute("""INSERT INTO assessments(patient_id,date,diagnosis_label,npc_cm,near_phoria_pd,
                distance_phoria_pd,pfv_break,nfv_break,accommodative_amplitude,maf_cpm,baf_cpm,stereo_arcsec,
                symptom_score,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (pid,str(d),diagnosis,npc,near,dist,pfv,nfv,aa,maf,baf,stereo,symptom,notes))
                conn.commit(); st.success("Saved. No automated interpretation is performed.")
            hist=pd.read_sql_query("SELECT * FROM assessments WHERE patient_id=? ORDER BY date DESC",(pid,))
            st.dataframe(hist,use_container_width=True,hide_index=True)
    with tabs[3]:
        pts=patients_df()
        if pts.empty: st.info("Register a demo patient first.")
        else:
            pid=st.selectbox("Patient for plan",pts.patient_id.tolist(),key="plan_pid")
            clinician=st.text_input("Responsible clinician")
            domain=st.selectbox("Target domain",["Vergence","Accommodation","Oculomotor","Visual perception","Other / adjunct"])
            activity=st.selectbox("Activity / procedure",[
                "Brock string (physical equipment; supervised instruction)",
                "Vectogram / tranaglyph (physical equipment; clinician supervised)",
                "Near-far accommodative rock (clinician selected)",
                "Hart chart (physical chart; clinician selected)",
                "Pursuit / saccade task (clinician selected)",
                "Computerized vergence task (validated/calibrated system only)",
                "Visual search game (engagement only; not validated therapy)",
                "Other clinician-defined activity"])
            instructions=st.text_area("Individualized instructions: setup, correction, working distance and stop criteria")
            q=st.columns(2)
            duration=q[0].number_input("Duration (minutes)",1,60,5)
            frequency=q[1].text_input("Frequency","As prescribed by clinician")
            progression=st.text_area("Measurable progression / regression criteria")
            review=st.date_input("Review date",date.today())
            if st.button("Create active plan"):
                if not clinician.strip() or not instructions.strip() or not progression.strip():
                    st.error("Clinician, individualized instructions and progression criteria are required.")
                else:
                    conn.execute("""INSERT INTO plans(patient_id,created_at,clinician,target_domain,activity,instructions,
                    duration_min,frequency,progression_rule,review_date,status) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (pid,datetime.now().isoformat(timespec="seconds"),clinician,domain,activity,instructions,
                     int(duration),frequency,progression,str(review),"Active"))
                    conn.commit(); st.success("Plan saved. Clinician controls review and progression.")
            st.dataframe(pd.read_sql_query("SELECT * FROM plans WHERE patient_id=? ORDER BY id DESC",(pid,)),use_container_width=True,hide_index=True)
    with tabs[4]:
        active=pd.read_sql_query("SELECT * FROM plans WHERE status='Active'",conn)
        if active.empty: st.info("No active plans. Create one first.")
        else:
            planid=st.selectbox("Assigned plan",active.id.tolist(),format_func=lambda i:f"Plan {i} · {active.loc[active.id==i,'patient_id'].iloc[0]} · {active.loc[active.id==i,'activity'].iloc[0]}")
            p=active[active.id==planid].iloc[0]
            st.write("**Instructions:**",p.instructions)
            with st.form("session"):
                d=st.date_input("Session date",date.today())
                mins=st.number_input("Minutes completed",0,120,int(p.duration_min))
                completion=st.selectbox("Completion",["Completed","Partially completed","Not completed"])
                feedback=st.text_input("Child / parent feedback")
                notes=st.text_area("Clinician notes / observed performance")
                save=st.form_submit_button("Log session")
            if save:
                conn.execute("INSERT INTO sessions(patient_id,plan_id,date,activity,duration_min,completion,feedback,clinician_notes) VALUES (?,?,?,?,?,?,?,?)",
                (p.patient_id,int(planid),str(d),p.activity,int(mins),completion,feedback,notes))
                conn.commit(); st.success("Session logged.")
    with tabs[5]:
        pts=patients_df()
        if pts.empty: st.info("No patients.")
        else:
            pid=st.selectbox("Patient for outcome review",pts.patient_id.tolist(),key="outcome_pid")
            hist=pd.read_sql_query("SELECT * FROM assessments WHERE patient_id=? ORDER BY date",(pid,))
            sess=pd.read_sql_query("SELECT * FROM sessions WHERE patient_id=? ORDER BY date",(pid,))
            if hist.empty: st.info("No assessments recorded.")
            else:
                st.dataframe(hist[["date","diagnosis_label","npc_cm","pfv_break","maf_cpm","baf_cpm","stereo_arcsec","symptom_score"]],use_container_width=True,hide_index=True)
                metric=st.selectbox("Plot measure",["npc_cm","pfv_break","maf_cpm","baf_cpm","stereo_arcsec","symptom_score"])
                st.line_chart(hist.set_index("date")[[metric]])
            st.subheader("Session adherence"); st.dataframe(sess,use_container_width=True,hide_index=True)

elif role == "Patient / parent portal":
    st.subheader("🌟 My vision journey")
    st.caption("Demo patient selector only. A production patient portal requires secure guardian authentication and strict record separation.")
    pts=patients_df()
    if pts.empty: st.info("Ask clinician to create a demo patient code.")
    else:
        pid=st.selectbox("Patient code",pts.patient_id.tolist())
        p=pts[pts.patient_id==pid].iloc[0]
        st.title(f"Hello, {p.display_name or 'Vision Explorer'}! 👋")
        plans=pd.read_sql_query("SELECT * FROM plans WHERE patient_id=? AND status='Active' ORDER BY id DESC",(pid,))
        if plans.empty: st.info("No activities assigned. Ask your optometrist.")
        for _,plan in plans.iterrows():
            with st.container(border=True):
                st.markdown(f"### 🎯 {plan.activity}")
                st.write("**Your clinician's instructions:**",plan.instructions)
                st.write(f"**Time:** {plan.duration_min} minutes · **Schedule:** {plan.frequency}")
                st.caption("Only do this as demonstrated and prescribed. Stop and tell an adult/clinician about pain, significant headache, nausea, dizziness or new/worsening double vision.")
        st.divider(); st.subheader("🕹️ Visual explorer")
        st.caption("Interface-engagement demo only; not validated vision therapy and does not measure eye movements, acuity, vergence or treatment response.")
        if "target" not in st.session_state: st.session_state.target=random.choice(["⭐","🐠","🦋","🍎"])
        st.write(f"Find the **{st.session_state.target}**.")
        choices=["🌙","🐢","🍀","🚀","🎈","🐠","⭐","🍎","🦋"]; random.shuffle(choices)
        cols=st.columns(3)
        for i,v in enumerate(choices):
            if cols[i%3].button(v,key=f"g_{i}_{st.session_state.get('round',0)}",use_container_width=True):
                st.success("Great finding! 🌈" if v==st.session_state.target else "Try again!")
        if st.button("New round"):
            st.session_state.target=random.choice(["⭐","🐠","🦋","🍎"])
            st.session_state.round=st.session_state.get("round",0)+1
            st.rerun()
else:
    st.subheader("📚 Evidence library")
    st.markdown("""
    Evidence is condition-specific. The strongest trial evidence in this starter concerns selected children with symptomatic convergence insufficiency (CI), not every binocular vision anomaly or learning difficulty.

    - CITT found office-based vergence/accommodative therapy with home reinforcement improved symptoms and clinical signs versus selected home-based and placebo approaches in children with symptomatic CI.
    - CITT-ART found greater improvement in NPC and PFV, but no significant between-group advantage in standardized reading outcomes.
    - These findings do not justify claiming that vision therapy treats dyslexia or learning disabilities.
    """)
    refs=[
    ("CITT Study Group (2008). Randomized clinical trial of treatments for symptomatic convergence insufficiency in children. Arch Ophthalmol. DOI: 10.1001/archopht.126.10.1336","https://doi.org/10.1001/archopht.126.10.1336"),
    ("CITT-ART (2019). Treatment of symptomatic convergence insufficiency in children. Optom Vis Sci. DOI: 10.1097/OPX.0000000000001443","https://doi.org/10.1097/OPX.0000000000001443"),
    ("CITT-ART (2019). Effect of vergence/accommodative therapy on reading. Optom Vis Sci. DOI: 10.1097/OPX.0000000000001442","https://doi.org/10.1097/OPX.0000000000001442"),
    ("Scheiman et al. (2011). Treatment of accommodative dysfunction in children. Optom Vis Sci. DOI: 10.1097/OPX.0b013e31822f4d7c","https://doi.org/10.1097/OPX.0b013e31822f4d7c"),
    ("CITT Study Group (2008). Design, methods and baseline data. Ophthalmic Epidemiol. DOI: 10.1080/09286580701772037","https://doi.org/10.1080/09286580701772037")]
    for label,url in refs: st.markdown(f"- [{label}]({url})")

st.divider()
st.caption("NeuroVision Therapy MVP • Educational workflow prototype • No autonomous diagnosis, treatment recommendation or calibrated optical stimulus.")
