import uuid

import logfire
import requests
import streamlit as st


AI_AVATAR = "🤖"
USER_AVATAR = "👤"

SUGGESTED_PROMPTS = (
    (
        "Kubernetes rollout",
        "How can I roll out a Kubernetes deployment safely with minimal downtime?",
    ),
    (
        "Intel networking",
        "Compare Intel SR-IOV with virtio networking for virtualized workloads.",
    ),
    (
        "BGP routing",
        "Explain the BGP route-selection process for an enterprise network.",
    ),
)


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --ink: #152238;
                --muted: #64748b;
                --line: #dfe7f1;
                --brand: #315efb;
                --brand-soft: #eef3ff;
                --sidebar: #0b1324;
            }

            .stApp {
                background:
                    radial-gradient(circle at 88% 5%, rgba(49, 94, 251, 0.09), transparent 24rem),
                    #f7f9fc;
                color: var(--ink);
            }

            .block-container {
                max-width: 1080px;
                padding-top: 2.5rem;
                padding-bottom: 7rem;
            }

            [data-testid="stSidebar"] {
                background: var(--sidebar);
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }

            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] .stCaption {
                color: #b8c4d8;
            }

            [data-testid="stSidebar"] hr {
                border-color: rgba(255, 255, 255, 0.1);
            }

            [data-testid="stSidebar"] .stButton button {
                min-height: 2.8rem;
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 0.75rem;
                background: rgba(255, 255, 255, 0.08);
                color: #f8fafc;
                font-weight: 600;
            }

            [data-testid="stSidebar"] .stButton button:hover {
                border-color: #7394ff;
                background: rgba(49, 94, 251, 0.22);
                color: #ffffff;
            }

            .brand-lockup {
                padding: 0.6rem 0 1.2rem;
            }

            .brand-mark {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 2.4rem;
                height: 2.4rem;
                margin-bottom: 0.85rem;
                border-radius: 0.75rem;
                background: linear-gradient(135deg, #315efb, #69a8ff);
                color: white;
                font-size: 1.15rem;
                font-weight: 800;
                box-shadow: 0 8px 22px rgba(49, 94, 251, 0.3);
            }

            .brand-name {
                color: #ffffff;
                font-size: 1.25rem;
                font-weight: 750;
                letter-spacing: -0.02em;
            }

            .brand-subtitle {
                margin-top: 0.2rem;
                color: #91a1b9;
                font-size: 0.82rem;
            }

            .sidebar-label {
                margin: 1.1rem 0 0.65rem;
                color: #71829d;
                font-size: 0.68rem;
                font-weight: 750;
                letter-spacing: 0.12em;
                text-transform: uppercase;
            }

            .status-card {
                margin-bottom: 0.65rem;
                padding: 0.72rem 0.8rem;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 0.7rem;
                background: rgba(255, 255, 255, 0.035);
            }

            .status-card-title {
                color: #eef4ff;
                font-size: 0.79rem;
                font-weight: 650;
            }

            .status-card-copy {
                margin-top: 0.18rem;
                color: #8292aa;
                font-size: 0.7rem;
            }

            .status-dot {
                display: inline-block;
                width: 0.46rem;
                height: 0.46rem;
                margin-right: 0.45rem;
                border-radius: 50%;
                background: #38d39f;
                box-shadow: 0 0 0 4px rgba(56, 211, 159, 0.1);
            }

            .domain-list {
                color: #b8c4d8;
                font-size: 0.78rem;
                line-height: 1.9;
            }

            .domain-list span {
                display: block;
            }

            .hero {
                margin-bottom: 1.7rem;
                padding: 0.3rem 0 0.2rem;
            }

            .eyebrow {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                margin-bottom: 0.8rem;
                color: var(--brand);
                font-size: 0.72rem;
                font-weight: 750;
                letter-spacing: 0.1em;
                text-transform: uppercase;
            }

            .eyebrow-dot {
                width: 0.45rem;
                height: 0.45rem;
                border-radius: 50%;
                background: var(--brand);
            }

            .hero h1 {
                max-width: 760px;
                margin: 0;
                color: var(--ink);
                font-size: clamp(2.05rem, 4vw, 3.25rem);
                font-weight: 760;
                letter-spacing: -0.045em;
                line-height: 1.06;
            }

            .hero p {
                max-width: 720px;
                margin: 1rem 0 0;
                color: var(--muted);
                font-size: 1rem;
                line-height: 1.65;
            }

            .trust-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin-top: 1.1rem;
            }

            .trust-chip {
                padding: 0.38rem 0.65rem;
                border: 1px solid #dce5f2;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.75);
                color: #53647c;
                font-size: 0.72rem;
                font-weight: 600;
            }

            .section-label {
                margin: 0.2rem 0 0.65rem;
                color: #64748b;
                font-size: 0.74rem;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }

            div[data-testid="stHorizontalBlock"] .stButton button {
                min-height: 4.5rem;
                padding: 0.75rem 0.9rem;
                border: 1px solid var(--line);
                border-radius: 0.85rem;
                background: rgba(255, 255, 255, 0.88);
                color: #334155;
                font-size: 0.82rem;
                font-weight: 600;
                line-height: 1.3;
                white-space: normal;
                box-shadow: 0 4px 16px rgba(24, 39, 75, 0.035);
            }

            div[data-testid="stHorizontalBlock"] .stButton button:hover {
                border-color: #9bb2ff;
                background: #f8faff;
                color: #2046ce;
                transform: translateY(-1px);
            }

            [data-testid="stChatMessage"] {
                margin-bottom: 0.8rem;
                padding: 1rem 1.1rem;
                border: 1px solid var(--line);
                border-radius: 1rem;
                background: rgba(255, 255, 255, 0.9);
                box-shadow: 0 6px 22px rgba(24, 39, 75, 0.035);
            }

            [data-testid="stChatMessageAvatarUser"] {
                background: #e8eeff;
                color: #315efb;
            }

            [data-testid="stChatInput"] {
                border: 1px solid #ccd8e8;
                border-radius: 0.95rem;
                background: #ffffff;
                box-shadow: 0 10px 30px rgba(24, 39, 75, 0.09);
            }

            [data-testid="stStatusWidget"] {
                border: 1px solid #dfe7f1;
                border-radius: 0.8rem;
                background: #f8faff;
            }

            [data-testid="stExpander"] {
                margin-top: 0.75rem;
                border: 1px solid var(--line);
                border-radius: 0.8rem;
                background: #fbfcfe;
            }

            @media (max-width: 700px) {
                .block-container {
                    padding-top: 1.5rem;
                }

                .hero h1 {
                    font-size: 2.1rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _ensure_session() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        logfire.info("New user session created: {session_id}", session_id=st.session_state.session_id)

    if "messages" not in st.session_state:
        st.session_state.messages = []


def _render_sidebar(logfire_status: str) -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-lockup">
                <div class="brand-mark">N</div>
                <div class="brand-name">Nexus</div>
                <div class="brand-subtitle">Enterprise Knowledge Assistant</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("＋  New conversation", width="stretch"):
            previous_session = st.session_state.session_id
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            logfire.warning("Conversation reset: {session_id}", session_id=previous_session)
            st.rerun()

        st.markdown('<div class="sidebar-label">Workspace</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-card-title"><span class="status-dot"></span>Secure session active</div>
                <div class="status-card-copy">Session {st.session_state.session_id[:8].upper()}</div>
            </div>
            <div class="status-card">
                <div class="status-card-title">Observability</div>
                <div class="status-card-copy">{logfire_status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-label">Knowledge domains</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="domain-list">
                <span>◈ &nbsp; Kubernetes operations</span>
                <span>◈ &nbsp; Intel infrastructure</span>
                <span>◈ &nbsp; Enterprise networking</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.caption("Responses are grounded in your approved technical documentation.")


def _render_header() -> None:
    st.markdown(
        """
        <section class="hero">
            <div class="eyebrow"><span class="eyebrow-dot"></span> Documentation copilot</div>
            <h1>Infrastructure answers, grounded in your knowledge.</h1>
            <p>
                Explore Kubernetes, Intel hardware, and enterprise networking with
                answers synthesized from your technical documentation and conversation context.
            </p>
            <div class="trust-row">
                <span class="trust-chip">Grounded responses</span>
                <span class="trust-chip">Source transparency</span>
                <span class="trust-chip">Conversation memory</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_prompt_starters() -> str | None:
    if st.session_state.messages:
        return None

    st.markdown('<div class="section-label">Start with a common question</div>', unsafe_allow_html=True)
    columns = st.columns(len(SUGGESTED_PROMPTS))
    selected_prompt = None

    for index, (label, prompt) in enumerate(SUGGESTED_PROMPTS):
        with columns[index]:
            if st.button(f"{label}\n\n{prompt}", key=f"prompt_starter_{index}", width="stretch"):
                selected_prompt = prompt

    return selected_prompt


def _render_history() -> None:
    for message in st.session_state.messages:
        avatar = AI_AVATAR if message["role"] == "assistant" else USER_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])


def _render_sources(sources: list) -> None:
    if not sources:
        return

    with st.expander(f"Sources and retrieved context · {len(sources)}"):
        for index, source in enumerate(sources, start=1):
            st.markdown(f"**Reference {index}**")
            st.text(str(source))
            if index < len(sources):
                st.divider()


def _submit_prompt(prompt: str, base_url: str) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AI_AVATAR):
        with st.status("Researching your documentation…", expanded=True) as status:
            try:
                with logfire.span(
                    "User chat interaction",
                    user_query=prompt,
                    session_id=st.session_state.session_id,
                ):
                    response = requests.post(
                        f"{base_url.rstrip('/')}/query",
                        json={"q": prompt, "thread_id": st.session_state.session_id},
                        timeout=60,
                    )
                    response.raise_for_status()
                    data = response.json()

                for step in data.get("thought_process", []):
                    st.caption(f"→ {step}")

                status.update(label="Response ready", state="complete", expanded=False)
            except (requests.RequestException, ValueError) as exc:
                logfire.error("UI-backend request failed: {error}", error=str(exc))
                status.update(label="Unable to reach the knowledge service", state="error")
                st.error(
                    "The knowledge service is temporarily unavailable. "
                    "Please confirm the backend is running and try again."
                )
                return

        full_answer = data.get("answer") or "No answer was returned."
        sources = data.get("sources") or []
        response_status = data.get("status") or "Response generated"

        st.markdown(full_answer)
        st.caption(f"{response_status} · {len(sources)} source{'s' if len(sources) != 1 else ''}")
        _render_sources(sources)

    st.session_state.messages.append({"role": "assistant", "content": full_answer})
    logfire.info("Chat cycle completed successfully.")


def render_chat_interface(base_url: str, logfire_status: str) -> None:
    _apply_styles()
    _ensure_session()
    _render_sidebar(logfire_status)
    _render_header()

    suggested_prompt = _render_prompt_starters()
    _render_history()

    typed_prompt = st.chat_input("Ask a question about your infrastructure documentation…")
    prompt = typed_prompt or suggested_prompt

    if prompt:
        _submit_prompt(prompt, base_url)
