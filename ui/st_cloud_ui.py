import os
import streamlit as st
import logfire

try:
    # Works when Streamlit is launched from the project root.
    from ui.chat_interface import render_chat_interface
except ModuleNotFoundError as exc:
    if exc.name != "ui":
        raise
    # Works when ui/ itself is the active script directory.
    from chat_interface import render_chat_interface


st.set_page_config(
    page_title="Nexus | Enterprise Knowledge Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize Logfire
try:
    logfire.configure(token=st.secrets.get("LOGFIRE_TOKEN", os.getenv("LOGFIRE_TOKEN")))
    logfire.instrument_requests()   # propagates trace context to the FastAPI backend
    LOGFIRE_STATUS = "Connected and tracing"
except Exception:
    LOGFIRE_STATUS = "Standby"


try:
    BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))
except Exception:
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


render_chat_interface(base_url=BACKEND_URL, logfire_status=LOGFIRE_STATUS)
