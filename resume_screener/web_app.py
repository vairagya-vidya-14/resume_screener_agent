import os
import sys

# Add directory paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
repo_root = os.path.dirname(parent_dir)

for p in [current_dir, parent_dir, repo_root]:
    if p and p not in sys.path:
        sys.path.insert(0, p)

import tempfile
import pandas as pd
import streamlit as st

try:
    from agent import ResumeScreeningAgent
    from parsers.resume_parser import ResumeParser
except (ImportError, ModuleNotFoundError):
    from resume_screener.agent import ResumeScreeningAgent
    from resume_screener.parsers.resume_parser import ResumeParser

st.set_page_config(
    page_title="AI Resume Screening Agent | Rooman Challenge",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #1E88E5; margin-bottom: 0.1rem; }
    .sub-header { font-size: 1.05rem; color: #555; margin-bottom: 1.5rem; }
    .card-box { background-color: #f8f9fa; border-radius: 10px; padding: 1rem; border-left: 4px solid #1E88E5; }
</style>
""", unsafe_allow_html=True)

def load_preset_jds():
    presets = {}
    
    # Senior AI Engineer
    jd1_path = os.path.join(parent_dir, "data", "sample_jds", "senior_ai_engineer.txt")
    if os.path.exists(jd1_path):
        with open(jd1_path, "r", encoding="utf-8") as f:
            presets["Senior AI / ML Engineer"] = f.read()
    else:
        presets["Senior AI / ML Engineer"] = "We are seeking a Senior AI/ML Engineer to build PyTorch, LLM, RAG, and MLOps pipelines."

    # Python & Full Stack Developer
    presets["Python & Full Stack Developer"] = """Job Title: Python & Full Stack Developer
Department: Engineering
Requirements:
- Strong hands-on experience with Python, Flask, MySQL, PostgreSQL, and REST APIs.
- Frontend proficiency in HTML5, CSS3, JavaScript, React.
- Working knowledge of Object-Oriented Programming, Data Structures, Git, GitHub, and Agile.
- B.Tech or Bachelor's degree in Computer Science, Engineering, or STEM field."""

    # Lead Data Scientist
    jd2_path = os.path.join(parent_dir, "data", "sample_jds", "data_scientist.txt")
    if os.path.exists(jd2_path):
        with open(jd2_path, "r", encoding="utf-8") as f:
            presets["Lead Data Scientist"] = f.read()
    else:
        presets["Lead Data Scientist"] = "Looking for a Data Scientist skilled in Python, SQL, Pandas, NumPy, Scikit-Learn, and statistical modeling."

    return presets

def main():
    st.markdown('<div class="main-header">🤖 AI Resume Screening Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Batch Resume Parsing, Multi-Dimensional Hybrid NLP Scoring & Shortlisting</div>', unsafe_allow_html=True)

    # Initialize Session State for Job Descriptions
    if "custom_jds" not in st.session_state:
        st.session_state["custom_jds"] = load_preset_jds()
    if "new_jd_title" not in st.session_state:
        st.session_state["new_jd_title"] = ""
    if "new_jd_desc" not in st.session_state:
        st.session_state["new_jd_desc"] = ""

    # Sidebar Controls
    st.sidebar.header("⚙️ Agent Controls")
    api_key = st.sidebar.text_input("OpenAI / Groq API Key (Optional)", type="password", help="Optional. If omitted, agent runs in Deterministic NLP Fallback mode.")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Job Description Manager")

    # JD Mode Switch: Select Existing vs Create New
    jd_mode = st.sidebar.radio("JD Options", ["Select Active JD", "➕ Create New JD"], horizontal=True)

    if jd_mode == "➕ Create New JD":
        st.sidebar.markdown("#### Create Custom Job Description")
        new_title = st.sidebar.text_input("Job Title", key="new_jd_title", placeholder="e.g. Python Developer / Data Analyst")
        new_desc = st.sidebar.text_area("Job Description Details", key="new_jd_desc", placeholder="Enter key responsibilities, required skills, and qualification details...", height=180)
        
        if st.sidebar.button("💾 Save & Create JD", type="primary", use_container_width=True):
            if new_title.strip() and new_desc.strip():
                title_clean = new_title.strip()
                desc_clean = new_desc.strip()
                st.session_state["custom_jds"][title_clean] = desc_clean
                st.session_state["selected_jd_title"] = title_clean
                
                # Clear input fields after creation
                st.session_state["new_jd_title"] = ""
                st.session_state["new_jd_desc"] = ""
                
                st.sidebar.success(f"Created & Selected JD: '{title_clean}'!")
                st.rerun()
            else:
                st.sidebar.error("Please provide both Job Title and Description.")

    # Select Active JD from dict
    jd_titles = list(st.session_state["custom_jds"].keys())
    
    default_sel_idx = 0
    if "selected_jd_title" in st.session_state and st.session_state["selected_jd_title"] in jd_titles:
        default_sel_idx = jd_titles.index(st.session_state["selected_jd_title"])

    selected_jd_title = st.sidebar.selectbox("Active Job Description", options=jd_titles, index=default_sel_idx)
    st.session_state["selected_jd_title"] = selected_jd_title

    if selected_jd_title and selected_jd_title in st.session_state["custom_jds"]:
        active_jd_text = st.sidebar.text_area("View / Edit Active JD Text", value=st.session_state["custom_jds"][selected_jd_title], height=180)
        st.session_state["custom_jds"][selected_jd_title] = active_jd_text
        
        # Delete JD Button
        if len(jd_titles) > 1:
            if st.sidebar.button(f"🗑️ Delete '{selected_jd_title}'", use_container_width=True):
                del st.session_state["custom_jds"][selected_jd_title]
                st.session_state["selected_jd_title"] = list(st.session_state["custom_jds"].keys())[0]
                st.sidebar.warning(f"Deleted Job Description '{selected_jd_title}'")
                st.rerun()
    else:
        active_jd_text = "Please select or create a Job Description."

    st.sidebar.markdown("---")

    # Main Page Uploader Area
    st.subheader("📤 Upload Resumes to Screen")
    uploaded_files = st.file_uploader(
        "Drag & drop multiple PDF, DOCX, or TXT resumes here at once",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="You can select and upload multiple candidate resumes at the same time."
    )

    sample_dir = os.path.join(parent_dir, "data", "sample_resumes")
    use_sample_btn = st.checkbox("Include Benchmark Sample Resumes (13 Candidates)", value=False)

    run_btn = st.button("🚀 Screen Resumes & Rank Shortlist", type="primary", use_container_width=True)

    if run_btn:
        if not uploaded_files and not use_sample_btn:
            st.warning("⚠️ Please upload resume files (PDF, DOCX, TXT) above or check 'Include Benchmark Sample Resumes' to screen.")
        else:
            agent = ResumeScreeningAgent(api_key=api_key if api_key else None)

            with st.spinner(f"Processing & scoring resumes against '{selected_jd_title}'..."):
                if uploaded_files:
                    temp_dir = tempfile.mkdtemp()
                    temp_paths = []
                    for uf in uploaded_files:
                        path = os.path.join(temp_dir, uf.name)
                        with open(path, "wb") as f:
                            f.write(uf.getbuffer())
                        temp_paths.append(path)
                    
                    if use_sample_btn and os.path.exists(sample_dir):
                        for sf in os.listdir(sample_dir):
                            if os.path.splitext(sf)[1].lower() in ResumeParser.SUPPORTED_EXTENSIONS:
                                temp_paths.append(os.path.join(sample_dir, sf))
                    
                    results = agent.screen_resume_files(temp_paths, active_jd_text)
                else:
                    results = agent.screen_resumes_folder(sample_dir, active_jd_text)

            st.session_state["last_results"] = results

    # Display results if available
    if "last_results" in st.session_state:
        results = st.session_state["last_results"]
        candidates = results["ranked_candidates"]
        total = results["total_candidates"]
        avg_score = results["average_score"]
        top = results["top_candidate"]

        st.markdown("---")

        # Key Performance Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Resumes Screened", total)
        m2.metric("Average Relevance Score", f"{avg_score} / 100")
        m3.metric("Top Ranked Candidate", top["candidate_name"] if top else "N/A")
        m4.metric("Top Candidate Score", f"{top['final_score']} / 100" if top else "N/A")

        # Leaderboard Table & Filtering
        st.subheader("🏆 Candidate Leaderboard & Shortlist")
        
        filter_option = st.radio(
            "Filter Candidates",
            ["All Candidates", "Shortlisted Only (Priority 1 & 2)", "Top 3 Only"],
            horizontal=True
        )

        filtered_cands = candidates
        if filter_option == "Shortlisted Only (Priority 1 & 2)":
            filtered_cands = [c for c in candidates if c["final_score"] >= 55]
        elif filter_option == "Top 3 Only":
            filtered_cands = candidates[:3]

        if not filtered_cands:
            st.warning("No candidates met the selected filter criteria.")
        else:
            table_data = []
            for c in filtered_cands:
                table_data.append({
                    "Rank": f"#{c['rank']}",
                    "Candidate Name": c["candidate_name"],
                    "Final Score": c["final_score"],
                    "Recommendation Tier": c["recommendation"],
                    "Format": c["format"],
                    "Experience": f"{c['experience_years']} Yrs",
                    "Education": ", ".join(c["education"]),
                    "Email": c["email"],
                    "Phone": c["phone"],
                    "LinkedIn": c["linkedin"],
                    "GitHub": c["github"],
                    "Matched Skills Count": len(c["matched_skills"]),
                    "Matched Skills": ", ".join(c["matched_skills"][:5]) + (f" (+{len(c['matched_skills'])-5})" if len(c["matched_skills"]) > 5 else "")
                })

            df_table = pd.DataFrame(table_data)
            
            # Interactive selection dataframe
            event = st.dataframe(
                df_table,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                column_config={
                    "Final Score": st.column_config.ProgressColumn(
                        "Final Score",
                        help="Composite hybrid score (0-100)",
                        format="%f",
                        min_value=0,
                        max_value=100
                    ),
                    "LinkedIn": st.column_config.LinkColumn("LinkedIn"),
                    "GitHub": st.column_config.LinkColumn("GitHub")
                }
            )

            # Check if user clicked a row in table
            selected_from_table = None
            if event and hasattr(event, "selection") and event.selection.get("rows"):
                selected_row_idx = event.selection["rows"][0]
                if selected_row_idx < len(filtered_cands):
                    selected_from_table = filtered_cands[selected_row_idx]["candidate_name"]

        # Export Options
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            with open(results["outputs"]["csv"], "rb") as f:
                st.download_button("📥 Export Shortlist CSV", f, file_name="ranked_candidates.csv", mime="text/csv", use_container_width=True)
        with exp_col2:
            with open(results["outputs"]["json"], "rb") as f:
                st.download_button("📥 Export Full JSON Report", f, file_name="ranked_candidates.json", mime="application/json", use_container_width=True)

        st.markdown("---")

        # Candidate Detail Inspector (Name-based Selection)
        st.subheader("🔍 Candidate Profile Inspector")
        cand_names = [c["candidate_name"] for c in candidates]
        
        default_name_idx = 0
        if selected_from_table and selected_from_table in cand_names:
            default_name_idx = cand_names.index(selected_from_table)

        selected_cand_name = st.selectbox(
            "Select Candidate by Name to View Detailed Profile",
            options=cand_names,
            index=default_name_idx
        )

        sel_c = next(c for c in candidates if c["candidate_name"] == selected_cand_name)

        d_col1, d_col2 = st.columns([1, 1])

        with d_col1:
            st.markdown(f"### {sel_c['candidate_name']} (Rank #{sel_c['rank']})")
            st.write(f"**Recommendation:** {sel_c['recommendation']}")
            st.write(f"**Email:** `{sel_c['email']}` | **Phone:** `{sel_c['phone']}`")
            
            if sel_c['linkedin'] != "N/A":
                st.write(f"**LinkedIn:** [{sel_c['linkedin']}]({sel_c['linkedin']})")
            else:
                st.write("**LinkedIn:** N/A")

            if sel_c['github'] != "N/A":
                st.write(f"**GitHub:** [{sel_c['github']}]({sel_c['github']})")
            else:
                st.write("**GitHub:** N/A")

            st.write(f"**Education:** {', '.join(sel_c['education'])} | **Experience:** {sel_c['experience_years']} years")
            st.write(f"**File Format:** {sel_c['format']} (`{sel_c['filename']}`)")

            st.markdown("#### 💡 Candidate Rationale")
            st.info(sel_c["reasoning"])

        with d_col2:
            st.markdown("#### 📊 Score Breakdown")
            st.write(f"**Final Score:** {sel_c['final_score']} / 100")
            st.progress(int(sel_c['final_score']))

            st.write(f"**TF-IDF Text Similarity:** {sel_c['tfidf_similarity']}%")
            st.progress(int(sel_c['tfidf_similarity']))

            st.write(f"**Skill Coverage Ratio:** {sel_c['skill_coverage_score']}%")
            st.progress(int(sel_c['skill_coverage_score']))

            st.markdown("#### ✅ Key Strengths")
            for s in sel_c["strengths"]:
                st.success(f"• {s}")

            st.markdown("#### ⚠️ Skill / Experience Gaps")
            for g in sel_c["gaps"]:
                st.warning(f"• {g}")

if __name__ == "__main__":
    main()
