
import streamlit as st
import os
import logging
from src.ui.run_workflow import run_workflow

# ========== Streamlit Config ==========
st.set_page_config(page_title="AI DevOps Workflow", layout="wide")
st.title("🚀 AI-Powered Software Development Workflow")

# ========== Streamlit Logger Handler ==========


class StreamlitLoggerHandler(logging.Handler):
    def __init__(self, container):
        super().__init__()
        self.container = container
        self.logs = []

    def emit(self, record):
        msg = self.format(record)
        self.logs.append(msg)
        self.container.text("\n".join(self.logs[-30:]))


# ========== Requirement Upload ==========
uploaded_file = st.file_uploader(
    "📄 Upload Requirement File (.md)", type=["md"])
if uploaded_file:
    requirement_path = "req_build.md"
    with open(requirement_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("Requirement file uploaded successfully!")

# ========== Start Workflow ==========
if st.button("Start Workflow 🚦"):
    log_container = st.empty()
    logger_handler = StreamlitLoggerHandler(log_container)
    logger_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logging.getLogger().addHandler(logger_handler)

    with st.spinner("Running the automated dev workflow..."):
        chat_placeholder = st.empty()  # Live chat container

        def live_chat_view(messages):
            with chat_placeholder.container():
                st.markdown("### 💬 Live Chat Trace")
                for msg in messages[-10:]:  # Show only recent messages
                    role = msg.__class__.__name__
                    icon = {
                        "HumanMessage": "🧑‍💻",
                        "SystemMessage": "⚙️",
                        "AIMessage": "🤖"
                    }.get(role, "💬")
                    st.markdown(
                        f"**{icon} {role}**\n\n{msg.content.strip()}\n\n---")

        result = run_workflow(live_callback=live_chat_view)

    logging.getLogger().removeHandler(logger_handler)
    st.success("✅ Workflow completed!")
    st.markdown("---")

    # ========== Helper to Show and Download Sections ==========
    def show_section(title, key, file_prefix="output"):
        st.subheader(title)
        content = result.get(key, "")
        st.markdown(f"```\n{content}\n```")
        st.download_button(
            label=f"⬇ Download {title}",
            data=content,
            file_name=f"{file_prefix}_{key}.md",
            mime="text/markdown"
        )

    # ========== Show Output Sections ==========
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

    # ========== Chat History Section ==========
    with st.expander("💬 Chat History"):
        st.markdown("#### Conversation Trace")
        for msg in result.get("messages", []):
            role = msg.__class__.__name__
            icon = {
                "HumanMessage": "🧑‍💻",
                "SystemMessage": "⚙️",
                "AIMessage": "🤖"
            }.get(role, "💬")
            content = msg.content.strip()
            st.markdown(f"**{icon} {role}**\n\n{content}\n\n---")

else:
    st.info("Upload a requirement file and click the button above to run the workflow.")
