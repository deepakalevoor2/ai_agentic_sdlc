import streamlit as st
import os
import logging
import re
from src.ui.run_workflow import run_workflow
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import pickle
import json

# Initialize session state for persistence
if "workflow_ran" not in st.session_state:
    st.session_state["workflow_ran"] = False
if "workflow_result" not in st.session_state:
    st.session_state["workflow_result"] = None
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []
if "file_uploaded" not in st.session_state:
    st.session_state["file_uploaded"] = False

# Set page config
st.set_page_config(
    page_title="AI Dev Workflow (Live + Persistent)", layout="wide")
st.title("🚀 AI Dev Workflow with Live Chat & Refresh Persistence")

# ========== File Loading Helper ==========


def load_saved_state():
    """Load state from disk if available"""
    try:
        if os.path.exists("streamlit_state.json"):
            with open("streamlit_state.json", "r") as f:
                data = json.load(f)
                st.session_state["workflow_ran"] = data["workflow_ran"]
                st.session_state["file_uploaded"] = data["file_uploaded"]

                # Handle workflow result if it exists
                if data["has_workflow_result"] and os.path.exists("workflow_result.pkl"):
                    with open("workflow_result.pkl", "rb") as rf:
                        st.session_state["workflow_result"] = pickle.load(rf)

            st.success("Previous session restored!")
    except Exception as e:
        st.error(f"Error loading previous session: {e}")


def save_current_state():
    """Save current state to disk"""
    try:
        # Save simple session variables to JSON
        with open("streamlit_state.json", "w") as f:
            data = {
                "workflow_ran": st.session_state["workflow_ran"],
                "file_uploaded": st.session_state["file_uploaded"],
                "has_workflow_result": st.session_state["workflow_result"] is not None
            }
            json.dump(data, f)

        # Save complex workflow result object using pickle
        if st.session_state["workflow_result"]:
            with open("workflow_result.pkl", "wb") as f:
                pickle.dump(st.session_state["workflow_result"], f)
    except Exception as e:
        st.error(f"Error saving session: {e}")


# Try to load saved state from disk at startup
load_saved_state()

# ========== Live Logger for Progress ==========


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
uploaded_file = st.file_uploader(
    "📄 Upload Requirement File (.md)", type=["md"],
    key="file_uploader")

if uploaded_file:
    with open("req_build.md", "wb") as f:
        f.write(uploaded_file.read())
    st.session_state["file_uploaded"] = True
    save_current_state()  # Save state after file upload
    st.success("Requirement file uploaded successfully!")

# ========== Live Chat Placeholder ==========
chat_placeholder = st.empty()


def live_chat_renderer(messages):
    # Save messages to session state for persistence
    st.session_state["chat_messages"] = messages

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

# ========== Run Workflow Function ==========


def run_and_save_workflow():
    log_container = st.empty()
    logger_handler = StreamlitLoggerHandler(log_container)
    logger_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logging.getLogger().addHandler(logger_handler)

    with st.spinner("Running the workflow with live chat..."):
        result = run_workflow(live_callback=live_chat_renderer)

    # Save results to session state
    st.session_state["workflow_ran"] = True
    st.session_state["workflow_result"] = result

    # Save state to disk immediately
    save_current_state()

    return result


# ========== Run on button click ==========
if st.button("Start Workflow 🚦", key="start_workflow"):
    result = run_and_save_workflow()
    st.success("✅ Workflow completed!")
else:
    # Use cached result from session state if available
    result = st.session_state["workflow_result"]

# Display saved chat messages if they exist (from previous runs)
if st.session_state["chat_messages"]:
    live_chat_renderer(st.session_state["chat_messages"])

# ========== Output Display ==========
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

    # Output sections...
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

    with st.expander("💬 Chat History"):
        st.markdown("#### Conversation Trace")
        all_messages = result.get("messages", [])
        ai_roles = set()

        for msg in all_messages:
            if isinstance(msg, AIMessage):
                match = re.search(
                    r"AI is now acting as (.*?)[.:]", msg.content)
                if match:
                    ai_roles.add(match.group(1).strip())

        filter_options = ["All", "Human", "System"] + sorted(ai_roles)
        selected_filter = st.selectbox(
            "Filter by Message Type or AI Role", filter_options)

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
                if role_class != "AIMessage" or f"AI is now acting as {selected_filter}" not in content:
                    continue

            st.markdown(f"**{icon} {role_class}**\n\n{content}\n\n---")
else:
    st.info("Upload a requirement file and click the button above to run the workflow.")

# Add a reset button to clear session state if needed
if st.session_state["workflow_ran"]:
    if st.button("Reset Workflow", key="reset_workflow"):
        # Clear session state
        st.session_state["workflow_ran"] = False
        st.session_state["workflow_result"] = None
        st.session_state["chat_messages"] = []
        st.session_state["file_uploaded"] = False

        # Remove saved files
        if os.path.exists("streamlit_state.json"):
            os.remove("streamlit_state.json")
        if os.path.exists("workflow_result.pkl"):
            os.remove("workflow_result.pkl")

        st.rerun()

# Display persistence status
st.sidebar.markdown("### Session Status")
st.sidebar.write(f"Workflow ran: {st.session_state['workflow_ran']}")
st.sidebar.write(f"File uploaded: {st.session_state['file_uploaded']}")
st.sidebar.write(
    f"Has results: {st.session_state['workflow_result'] is not None}")
