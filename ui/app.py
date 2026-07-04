import os
import streamlit as st
import logfire
from dotenv import load_dotenv

try:
    # Works when Streamlit is launched from the project root.
    from ui.chat_interface import render_chat_interface
except ModuleNotFoundError as exc:
    if exc.name != "ui":
        raise
    # Works when ui/ itself is the active script directory.
    from chat_interface import render_chat_interface


# Load environment variables explicitly from the root directory
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)


st.set_page_config(
    page_title="Nexus | Enterprise Knowledge Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize Logfire
try:
    token = os.getenv("LOGFIRE_TOKEN")
    if not token:
        print("ERROR: LOGFIRE_TOKEN is empty or None!")
    logfire.configure(token=token)
    # logfire.instrument_requests() # Disabled due to OpenTelemetry bug on Windows: MeterProvider.get_meter() got multiple values for argument 'version'
    LOGFIRE_STATUS = "Connected and tracing"
except Exception as e:
    print(f"Logfire Init Error in UI: {e}")
    LOGFIRE_STATUS = "Standby"


render_chat_interface(
    base_url=os.getenv("BACKEND_URL", "http://localhost:8000"),
    logfire_status=LOGFIRE_STATUS,
)
