import os, json
import streamlit as st
import pandas as pd
from services.ocr_service import extract_text_from_upload
from services.parser import parse_lab_results
from services.analyzer import analyze_results
from services.llm_service import generate_patient_summary
from storage import save_analysis, load_history

st.set_page_config(page_title="Intelligent Healthcare Report Analysis", page_icon="🩺", layout="wide")

st.markdown("""
<style>
.main-title{font-size:34px;font-weight:700}
.card{padding:18px;border-radius:12px;border:1px solid #ddd;background:#fafafa}
.small{color:#666;font-size:13px}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🩺 Intelligent Healthcare Report Analysis</div>', unsafe_allow_html=True)
st.caption("Vision + OCR + rule-based clinical reference analysis + optional LLM/VLM explanation")
st.warning("Educational support only. This prototype does not diagnose disease or replace a qualified healthcare professional.")

with st.sidebar:
    st.header("System")
    st.write("**OCR:** PyMuPDF + Tesseract fallback")
    st.write("**Analysis:** Reference-range engine")
    st.write("**AI:** Optional LLM/VLM")
    st.write("**Storage:** Local SQLite")
    api_status = bool(os.getenv("OPENAI_API_KEY"))
    st.write("AI API:", "🟢 configured" if api_status else "🟡 optional / not configured")

tab1, tab2, tab3 = st.tabs(["📄 Analyze Report", "📊 Dashboard", "🕘 History"])

with tab1:
    uploaded = st.file_uploader("Upload a medical report", type=["pdf","png","jpg","jpeg"])
    if uploaded:
        st.success(f"Uploaded: {uploaded.name}")
        if st.button("🔍 Analyze Report", type="primary"):
            with st.spinner("Extracting and analyzing..."):
                raw_text, pages = extract_text_from_upload(uploaded)
                parsed = parse_lab_results(raw_text)
                analyzed = analyze_results(parsed)
                summary = generate_patient_summary(analyzed, raw_text)
                record_id = save_analysis(uploaded.name, raw_text, analyzed, summary)

            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Tests detected", len(analyzed))
            c2.metric("Abnormal", sum(x["status"]!="Normal" for x in analyzed))
            c3.metric("Normal", sum(x["status"]=="Normal" for x in analyzed))
            c4.metric("Record ID", record_id)

            st.subheader("📌 Patient-friendly summary")
            st.info(summary)

            st.subheader("🧪 Extracted laboratory values")
            if analyzed:
                df = pd.DataFrame(analyzed)
                cols = ["test","value","unit","reference_range","status","source"]
                st.dataframe(df[[c for c in cols if c in df.columns]], use_container_width=True, hide_index=True)
            else:
                st.warning("No structured lab values were detected. Check OCR text below or use a clearer report.")

            st.subheader("📝 OCR text")
            with st.expander("Show extracted text"):
                st.text_area("OCR/Text", raw_text, height=300)

            st.download_button(
                "Download analysis JSON",
                data=json.dumps({"file":uploaded.name,"results":analyzed,"summary":summary}, indent=2),
                file_name="healthcare_analysis.json",
                mime="application/json"
            )

with tab2:
    history = load_history()
    if history:
        rows=[]
        for h in history:
            rows.append({
                "ID":h["id"], "Report":h["filename"], "Date":h["created_at"],
                "Tests":len(h["results"]), "Abnormal":sum(x["status"]!="Normal" for x in h["results"])
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        all_results=[r for h in history for r in h["results"]]
        if all_results:
            st.subheader("Abnormal-value overview")
            counts = pd.Series([x["test"] for x in all_results if x["status"]!="Normal"]).value_counts()
            st.bar_chart(counts)
    else:
        st.info("No analyses stored yet.")

with tab3:
    history = load_history()
    if not history:
        st.info("No saved reports.")
    else:
        for h in history:
            with st.expander(f'#{h["id"]} — {h["filename"]} — {h["created_at"]}'):
                st.write(h["summary"])
                st.dataframe(pd.DataFrame(h["results"]), use_container_width=True, hide_index=True)
