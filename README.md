
# 🧠 AI Agentic SDLC

A fully automated, LLM-powered Software Development Life Cycle (SDLC) orchestrated using LangGraph and LangChain, visualized through a clean Streamlit interface.

This project emulates a multi-role AI team that collaborates to:
- Gather requirements
- Generate user stories
- Perform PO reviews
- Create design documents
- Write and review code
- Conduct security reviews
- Generate and test cases
- Plan deployment, monitoring, and maintenance

---

## 🚀 Features

✅ Real-time chat stream from AI agents  
✅ Streamlit UI with rich, scroll-free output blocks  
✅ LangGraph-powered agentic architecture  
✅ Modular and scalable Python codebase  
✅ Session persistence on page refresh  
✅ Role-specific filtering

---

## 📁 Project Structure

```
├── src/
│   ├── graph/               # LangGraph orchestration
│   ├── llms/                # Model selection + setup
│   ├── nodes/               # Agent nodes performing tasks
│   ├── state/               # Global shared state and schema
│   └── ui/                  # Entrypoint runner for the workflow
├── streamlit_app_live_chat_persistent.py   # Final production UI
├── README.md
```

---

## 🧪 Getting Started

### 📦 Install dependencies

```bash
pip install -r requirements.txt
```

### ▶️ Launch the app

```bash
streamlit run streamlit_app_live_chat_persistent.py
```

### 📤 Upload requirements

- Upload a `.md` file named `req_build.md` when prompted to trigger the flow.

---

## 🧩 Technologies

- **LangChain + LangGraph** for LLM workflow execution
- **Streamlit** for interactive UI
- **Python** as the core implementation language
- **Azure**, **Snowflake**, and other integrations supported optionally
- **OpenAI**, **Groq**, **Gemini**, or any LangChain-compatible model

---

## 👤 Author

**Deepak K Alevoor**  
📧 [deepualevoor@gmail.com](mailto:deepualevoor@gmail.com)  
🔗 [GitHub](https://github.com/deepakalevoor2) | [LinkedIn](https://linkedin.com/in/deepak-alevoor-09a1b296)

---

## 📜 License

This project is licensed under the MIT License.

---

## 🙌 Contributions

---

## 📸 Screenshots


