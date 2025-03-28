
import streamlit as st
import os
import logging
import re
from src.ui.run_workflow import run_workflow
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

st.set_page_config(page_title="AI DevOps Workflow", layout="wide")
st.title("🚀 AI-Powered Software Development Workflow")

# ========== Logger for Live Updates ==========
class StreamlitLoggerHandler(logging.Handler):
    def __init__(self, container):
        super().__init__()
        self.container = container
        self.logs = []

    def emit(self, record):
        msg = self.format(record)
        self.logs.append(msg)
        self.container.text("\n".join(self.logs[-30:]))

# ========== File Upload ==========
uploaded_file = st.file_uploader("📄 Upload Requirement File (.md)", type=["md"])
if uploaded_file:
    with open("req_build.md", "wb") as f:
        f.write(uploaded_file.read())
    st.success("Requirement file uploaded successfully!")
    st.cache_data.clear()
    st.session_state.pop("workflow_result", None)

# ========== Run Workflow (cached) ==========
@st.cache_data(show_spinner="Running workflow...")
def cached_run_workflow():
    return run_workflow()

# ========== Start Button ==========
if "workflow_result" not in st.session_state and st.button("Start Workflow 🚦"):
    log_container = st.empty()
    logger_handler = StreamlitLoggerHandler(log_container)
    logger_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logging.getLogger().addHandler(logger_handler)

    chat_placeholder = st.empty()

    def live_chat_view(messages):
        with chat_placeholder.container():
            st.markdown("### 💬 Live Chat Trace")
            for msg in messages[-10:]:
                role = msg.__class__.__name__
                icon = {
                    "HumanMessage": "🧑‍💻",
                    "SystemMessage": "⚙️",
                    "AIMessage": "🤖"
                }.get(role, "💬")
                st.markdown(f"**{icon} {role}**\n\n{msg.content.strip()}\n\n---")

    st.session_state["workflow_result"] = cached_run_workflow()
    logging.getLogger().removeHandler(logger_handler)
    st.success("✅ Workflow completed!")
    st.markdown("---")

# ========== Use Result ==========
result = st.session_state.get("workflow_result")
if result:
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

    # ========== Chat History with Role Filtering ==========
    with st.expander("💬 Chat History"):
        all_messages = result.get("messages", [])
        ai_roles = set()

        for msg in all_messages:
            if isinstance(msg, AIMessage):
                match = re.search(r"AI is now acting as (.*?)[.:]", msg.content, re.IGNORECASE)
                if match:
                    ai_roles.add(match.group(1).strip())

        filter_options = ["All", "Human", "System"] + sorted(ai_roles)
        selected_filter = st.selectbox("Filter by Message Type or AI Role", filter_options)

        icon_map = {
            "HumanMessage": "🧑‍💻",
            "SystemMessage": "⚙️",
            "AIMessage": "🤖"
        }

        for msg in all_messages:
            role_class = msg.__class__.__name__
            icon = icon_map.get(role_class, "💬")
            content = msg.content.strip()

            if selected_filter == "Human" and role_class != "HumanMessage":
                continue
            elif selected_filter == "System" and role_class != "SystemMessage":
                continue
            elif selected_filter not in ["All", "Human", "System"]:
                if role_class != "AIMessage":
                    continue
                role_match = re.search(r"AI is now acting as (.*?)[.:]", content, re.IGNORECASE)
                if not role_match or role_match.group(1).strip() != selected_filter:
                    continue

            st.markdown(f"**{icon} {role_class}**\n\n{content}\n\n---")
else:
    st.info("Upload a requirement file and click the button above to run the workflow.")
