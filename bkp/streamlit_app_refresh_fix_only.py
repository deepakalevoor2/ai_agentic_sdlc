
import streamlit as st
import os
from src.ui.run_workflow import run_workflow

st.set_page_config(page_title="AI Dev Workflow", layout="wide")
st.title("🚀 AI Dev Workflow (Wrapped Output, No Scroll)")

# ========== File Upload ==========
uploaded_file = st.file_uploader(
    "📄 Upload Requirement File (.md)", type=["md"])
if uploaded_file:
    with open("req_build.md", "wb") as f:
        f.write(uploaded_file.read())
    st.success("Requirement file uploaded successfully!")
    st.cache_data.clear()

# ========== Cached Workflow ==========


@st.cache_data(show_spinner="Running the full workflow...")
def cached_run():
    return run_workflow()


# ========== Trigger ==========
if st.button("Start Workflow 🚦"):
    result = cached_run()
    st.success("✅ Workflow completed!")
else:
    result = cached_run()

# ========== Show Results ==========
if result:
    def show_section(title, key, file_prefix="output"):
        st.subheader(title)
        content = result.get(key, "")
        st.markdown(f"""
<div style='white-space: pre-wrap; word-wrap: break-word; overflow-x: auto; padding: 1em; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;'>
{content}
</div>
""", unsafe_allow_html=True)
        st.download_button(
            label=f"⬇ Download {title}",
            data=content,
            file_name=f"{file_prefix}_{key}.md",
            mime="text/markdown"
        )

    show_section("📌 User Requirement", "user_requirement")
    show_section("📝 Generated User Stories", "generated_user_stories")
    show_section("🧑‍💼 PO Review Comments", "po_review_comment")
    show_section("🧱 Design Document", "design_doc")
    show_section("🔍 Design Doc Review", "design_doc_review_comments")
    show_section("💻 Generated Code", "generated_code", "code")
    show_section("🧪 Code Review Comments", "code_review_comments")
    show_section("🔐 Security Review Comments", "security_review_comments")
    show_section("📋 Test Cases", "generated_test_cases", "tests")
    show_section("🧠 Test Case Review", "test_case_review_comments")
    show_section("✅ QA Testing Result", "qa_testing_result")
    show_section("📦 Deployment Plan", "deployment_plan")
    show_section("📊 Monitoring Plan", "monitoring_plan")
    show_section("🔧 Maintenance Plan", "maintenance_plan")
else:
    st.info("Upload a requirement file and click the button above to run the workflow.")
