"""PULSE — Customer Purchase Intelligence Streamlit application."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st
from pymongo.errors import PyMongoError

from src.customer_service import (
    create_customer,
    delete_customer,
    list_customers,
    search_customers,
    update_customer,
)
from src.feature_service import get_customer_prediction_status
from src.mongodb import check_connection, get_database
from src.prediction_service import (
    get_prediction_history,
    predict_customer_by_id,
)


# -----------------------------------------------------------------------------
# Page setup
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="PULSE | Customer Intelligence",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Design tokens & styling
# -----------------------------------------------------------------------------

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

      :root {
        --ink: #e2e8f0;
        --muted: #94a3b8;
        --line: #334155;
        --paper: #1e293b;
        --canvas: #0f172a;

        --accent: #b9ed68;
        --accent-strong: #a4e04f;
        --accent-ink: #0f172a;
        --accent-border: #7fa845;

        --brand-green: #1f4c3f;
        --brand-green-hover: #2a5c4d;

        --radius: 14px;
        --radius-sm: 10px;
      }

      /* ---------- Base ---------- */
      html, body, [class*="css"] {
        font-family: 'Manrope', system-ui, -apple-system, sans-serif;
        color: var(--ink);
      }

      [data-testid="stAppViewContainer"] {
        background: var(--canvas);
        color: var(--ink);
      }

      [data-testid="stHeader"] {
        background: rgba(15, 23, 42, 0.9);
        backdrop-filter: blur(6px);
      }

      .block-container {
        max-width: 1360px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
      }

      /* ---------- Typography helpers ---------- */
      .pulse-eyebrow {
        font-family: 'DM Mono', monospace;
        color: var(--muted);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        margin-bottom: 0.45rem;
      }
      .pulse-title {
        font-size: clamp(1.7rem, 3vw, 2.5rem);
        letter-spacing: -0.045em;
        line-height: 1.08;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 0.6rem 0;
      }
      .pulse-subtitle {
        color: var(--muted);
        font-size: 0.96rem;
        line-height: 1.6;
        max-width: 760px;
      }
      .pulse-section-head {
        font-size: 1.08rem;
        color: #ffffff;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 1.1rem 0 0.15rem 0;
      }
      .pulse-section-copy {
        color: var(--muted);
        margin-bottom: 0.8rem;
        font-size: 0.84rem;
      }

      /* ---------- Sidebar ---------- */
      [data-testid="stSidebar"] {
        background: #020617;
        border-right: 1px solid var(--line);
      }
      [data-testid="stSidebar"] * {
        color: var(--ink) !important;
      }
      [data-testid="stSidebar"] .pulse-brand-name { color: #ffffff !important; }
      [data-testid="stSidebar"] .pulse-brand-sub  { color: var(--muted) !important; }
      [data-testid="stSidebar"] .pulse-mark {
        background: var(--accent);
        color: var(--accent-ink) !important;
      }
      [data-testid="stSidebar"] .pulse-sidebar-label {
        color: var(--muted) !important;
        font-family: 'DM Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }
      [data-testid="stSidebar"] .pulse-sidebar-copy {
        color: var(--muted) !important;
        font-size: 0.78rem;
        line-height: 1.6;
      }

      [data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] {
        gap: 0.25rem;
      }
      [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 0.5rem 0.7rem !important;
        border-radius: var(--radius-sm) !important;
        transition: background 120ms ease;
      }
      [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: var(--paper) !important;
      }
      [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
      [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: var(--paper) !important;
      }
      [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        color: var(--ink) !important;
        font-weight: 600;
        font-size: 0.9rem;
      }

      /* ---------- Hero ---------- */
      .pulse-hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #f1f6ec;
        padding: 1.7rem 1.9rem;
        border-radius: 20px;
        margin: 0.4rem 0 1.4rem 0;
        border: 1px solid var(--line);
      }
      .pulse-hero:after {
        content: '';
        position: absolute;
        width: 260px;
        height: 260px;
        right: -70px;
        top: -120px;
        border: 1px solid rgba(185, 237, 104, 0.15);
        border-radius: 50%;
        box-shadow: 0 0 0 24px rgba(185, 237, 104, 0.02),
                    0 0 0 52px rgba(185, 237, 104, 0.01);
        pointer-events: none;
      }
      .pulse-hero-kicker {
        color: var(--accent);
        font-family: 'DM Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
      }
      .pulse-hero-title {
        color: #ffffff;
        font-size: clamp(1.5rem, 2.5vw, 2.25rem);
        font-weight: 800;
        letter-spacing: -0.045em;
        line-height: 1.12;
        max-width: 780px;
        margin: 0;
      }
      .pulse-hero-copy {
        color: #cbd5e1;
        margin-top: 0.85rem;
        font-size: 0.92rem;
        line-height: 1.65;
        max-width: 720px;
      }

      /* ---------- Inline note ---------- */
      .pulse-inline-note {
        border-left: 3px solid var(--accent);
        padding: 0.6rem 0.85rem;
        background: rgba(185, 237, 104, 0.05);
        color: var(--ink);
        border-radius: 0 10px 10px 0;
        font-size: 0.84rem;
        line-height: 1.55;
        margin: 0.6rem 0 1rem 0;
      }

      /* ---------- Result card ---------- */
      .pulse-result {
        border: 1px solid var(--line);
        border-radius: var(--radius);
        background: var(--paper);
        padding: 1.2rem 1.25rem;
      }
      .pulse-result-label {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-family: 'DM Mono', monospace;
        font-size: 0.68rem;
        color: var(--muted);
      }
      .pulse-result-value {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        color: #ffffff;
        margin: 0.35rem 0;
      }
      .pulse-result-foot {
        color: var(--muted);
        font-size: 0.8rem;
      }

      /* ---------- Footer ---------- */
      .pulse-footer {
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top: 1px solid var(--line);
        color: var(--muted);
        font-size: 0.72rem;
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        flex-wrap: wrap;
      }
      .pulse-code {
        font-family: 'DM Mono', monospace;
        font-size: 0.78rem;
      }

      /* ---------- Metrics ---------- */
      [data-testid="stMetric"] {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: var(--radius);
        padding: 1rem 1.05rem;
      }
      [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: 0.78rem;
        font-weight: 700;
      }
      [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800;
        letter-spacing: -0.04em;
      }

      /* ---------- Forms ---------- */
      [data-testid="stForm"] {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: var(--radius);
        padding: 1.2rem 1.2rem 0.9rem 1.2rem;
      }

      /* Widget labels */
      [data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"],
      [data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] *,
      [data-testid="stAppViewContainer"] [data-testid="stCheckbox"] label,
      [data-testid="stAppViewContainer"] [data-testid="stCheckbox"] label *,
      [data-testid="stAppViewContainer"] [data-testid="stRadio"] label,
      [data-testid="stAppViewContainer"] [data-testid="stRadio"] label * {
        color: var(--ink) !important;
        opacity: 1 !important;
        font-weight: 700;
      }

      [data-testid="stCaptionContainer"],
      [data-testid="stCaptionContainer"] * {
        color: var(--muted) !important;
      }

      /* Inputs */
      [data-testid="stTextInput"] input,
      [data-testid="stTextArea"] textarea,
      [data-testid="stNumberInput"] input,
      [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--line) !important;
        color: var(--ink) !important;
        background-color: var(--canvas) !important;
        font-size: 0.92rem;
        box-shadow: none !important;
      }
      [data-testid="stTextInput"] input::placeholder,
      [data-testid="stTextArea"] textarea::placeholder {
        color: var(--muted) !important;
        opacity: 1 !important;
      }
      [data-testid="stTextInput"] input:focus,
      [data-testid="stTextArea"] textarea:focus,
      [data-testid="stNumberInput"] input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(185, 237, 104, 0.2) !important;
      }

      /* Dropdown popovers */
      [data-baseweb="popover"],
      [role="listbox"],
      [role="option"] {
        background-color: var(--paper) !important;
      }
      [data-baseweb="popover"] *,
      [role="listbox"] *,
      [role="option"] * {
        color: var(--ink) !important;
      }
      [role="option"]:hover {
        background-color: var(--line) !important;
      }

      /* ---------- Buttons ---------- */
      .stButton button,
      [data-testid="stFormSubmitButton"] button,
      button[kind="primary"],
      button[kind="secondary"] {
        border-radius: var(--radius-sm) !important;
        font-weight: 800 !important;
        min-height: 2.65rem;
        background: var(--accent) !important;
        border: 1px solid var(--accent) !important;
        color: var(--accent-ink) !important;
        transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
      }
      .stButton button:hover,
      [data-testid="stFormSubmitButton"] button:hover,
      button[kind="primary"]:hover,
      button[kind="secondary"]:hover {
        background: var(--accent-strong) !important;
        color: var(--accent-ink) !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(185, 237, 104, 0.15);
      }
      .stButton button:focus,
      [data-testid="stFormSubmitButton"] button:focus {
        box-shadow: 0 0 0 3px rgba(185, 237, 104, 0.3) !important;
      }

      /* ---------- Tabs (Fixed visibility issue) ---------- */
      [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: none !important;
        padding-bottom: 0.5rem;
      }
      /* Force off-white text on inactive tabs */
      [data-testid="stTabs"] button[role="tab"] {
        border: 1px solid transparent !important;
        border-radius: var(--radius-sm) !important;
        background: transparent !important;
        color: var(--muted) !important;
        font-weight: 700 !important;
        padding: 0.55rem 1rem !important;
        opacity: 1 !important;
      }
      [data-testid="stTabs"] button[role="tab"] * {
        color: var(--muted) !important;
      }
      [data-testid="stTabs"] button[role="tab"]:hover {
        background: var(--paper) !important;
      }
      [data-testid="stTabs"] button[role="tab"]:hover * {
        color: var(--ink) !important;
      }
      [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: var(--paper) !important;
        border-color: var(--line) !important;
      }
      [data-testid="stTabs"] button[role="tab"][aria-selected="true"] * {
        color: #ffffff !important;
      }
      /* Remove Streamlit's default red underline completely */
      [data-testid="stTabs"] [data-baseweb="tab-highlight"],
      [data-testid="stTabs"] [data-baseweb="tab-border"] {
        display: none !important;
      }

      /* ---------- Alerts ---------- */
      [data-testid="stAlert"] {
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--line);
        background: var(--paper) !important;
      }
      [data-testid="stAlert"] * {
        color: var(--ink) !important;
        opacity: 1 !important;
      }

      /* ---------- DataFrames ---------- */
      [data-testid="stDataFrame"],
      [data-testid="stTable"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
        background: var(--paper);
      }
      [data-testid="stDataFrame"] *,
      [data-testid="stTable"] * {
        color: var(--ink) !important;
      }

      /* ---------- Progress ---------- */
      [data-testid="stProgress"] > div > div > div > div {
        background-color: var(--accent);
      }

      /* ---------- Brand block (sidebar) ---------- */
      .pulse-brand {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin: 0.2rem 0 1.4rem 0;
      }
      .pulse-mark {
        width: 39px;
        height: 39px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.45rem;
        font-weight: 800;
      }
      .pulse-brand-name {
        font-size: 1rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: 0.08em;
      }
      .pulse-brand-sub {
        font-size: 0.65rem;
        margin-top: 0.26rem;
        letter-spacing: 0.13em;
        text-transform: uppercase;
      }

      /* Responsive */
      @media (max-width: 700px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .pulse-hero { padding: 1.25rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Small helpers
# -----------------------------------------------------------------------------

def page_header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div style="margin-bottom:1.25rem;">
          <div class="pulse-eyebrow">{kicker}</div>
          <div class="pulse-title">{title}</div>
          <div class="pulse-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, copy: str = "") -> None:
    st.markdown(
        f'<div class="pulse-section-head">{title}</div>'
        + (f'<div class="pulse-section-copy">{copy}</div>' if copy else ""),
        unsafe_allow_html=True,
    )


def pretty_date(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%d %b %Y · %H:%M")
    return str(value)


def safe_database() -> bool:
    try:
        check_connection()
        return True
    except Exception as exc:
        st.error(
            "PULSE couldn't reach MongoDB Atlas. Check the local .env file, "
            "the Atlas network access list, and your active virtual environment."
        )
        st.caption(f"Connection error type: {type(exc).__name__}")
        return False


def display_customer_table(records: list[dict]) -> None:
    if not records:
        st.info("No customer records match this view yet.")
        return
    frame = pd.DataFrame(records)
    if "updated_at" in frame.columns:
        frame["updated_at"] = frame["updated_at"].map(pretty_date)
    if "created_at" in frame.columns:
        frame["created_at"] = frame["created_at"].map(pretty_date)
    st.dataframe(frame, use_container_width=True, hide_index=True)


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="pulse-brand">
          <div class="pulse-mark">◉</div>
          <div>
            <div class="pulse-brand-name">PULSE</div>
            <div class="pulse-brand-sub">Customer intelligence</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="pulse-sidebar-label" style="margin-bottom:.5rem;">Workspace</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Overview", "Customer records", "Purchase prediction", "Prediction history"],
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="pulse-sidebar-label">System status</div>',
        unsafe_allow_html=True,
    )
    connection_ok = safe_database()
    if connection_ok:
        st.markdown(
            "<div style='display:flex;align-items:center;gap:.5rem;"
            "color:#d8f4bb !important;font-size:.82rem;margin-top:.45rem;'>"
            "<span style='width:7px;height:7px;border-radius:50%;"
            "background:#b9ed68;display:inline-block;box-shadow:0 0 0 3px rgba(185,237,104,.18);'>"
            "</span>Atlas connected</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.3rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="pulse-sidebar-copy">'
        "A compact workspace for customer records and purchase-likelihood analysis."
        "</div>",
        unsafe_allow_html=True,
    )

if not connection_ok:
    st.stop()

db = get_database()


# -----------------------------------------------------------------------------
# Overview
# -----------------------------------------------------------------------------

if page == "Overview":
    st.markdown(
        """
        <div class="pulse-hero">
          <div class="pulse-hero-kicker">Retail intelligence · project workspace</div>
          <div class="pulse-hero-title">Know the pattern.<br>Understand the next purchase.</div>
          <div class="pulse-hero-copy">
            Manage customer records, explore historical buying signals, and generate
            model-based purchase predictions from one connected workspace.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        customer_count = db["customers"].count_documents({})
        feature_count = db["customer_features"].count_documents({})
        prediction_count = db["prediction_history"].count_documents({})
        positive_count = db["prediction_history"].count_documents({"predicted_purchase": 1})
        latest_prediction = get_prediction_history(limit=1)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Customer profiles", f"{customer_count:,}", help="Profiles managed through this application.")
        m2.metric("Feature snapshots", f"{feature_count:,}", help="Historical customer snapshots available to the model.")
        m3.metric("Predictions saved", f"{prediction_count:,}")
        m4.metric("Purchase predicted", f"{positive_count:,}")

        left, right = st.columns([1.2, 0.8], gap="large")
        with left:
            section_header("Recent customer records", "Profiles most recently updated in the application")
            display_customer_table(list_customers(limit=8))
        with right:
            section_header("Latest model activity", "The most recently saved prediction")
            if latest_prediction:
                p = latest_prediction[0]
                outcome = "Purchase predicted" if p.get("predicted_purchase") == 1 else "No purchase predicted"
                probability = p.get("purchase_probability", 0.0)
                st.markdown(
                    f"""
                    <div class="pulse-result">
                      <div class="pulse-result-label">Customer {p.get('customer_id', '—')}</div>
                      <div class="pulse-result-value">{probability:.1%}</div>
                      <div style="font-weight:800;color:#1f4c3f;margin-bottom:.55rem;">{outcome}</div>
                      <div class="pulse-result-foot">Model · {p.get('model_name', '—')}</div>
                      <div class="pulse-result-foot">Saved · {pretty_date(p.get('created_at'))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(max(0.0, min(float(probability), 1.0)))
                st.caption("Probability is a model estimate, not a guarantee of future behaviour.")
            else:
                st.markdown(
                    '<div class="pulse-result">'
                    '<div class="pulse-result-label">No activity yet</div>'
                    '<div style="font-weight:800;font-size:1.15rem;margin:.45rem 0;color:#14211f;">'
                    "Your first prediction goes here.</div>"
                    '<div class="pulse-result-foot">'
                    "Open Purchase prediction and choose a customer with historical features.</div></div>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                '<div class="pulse-inline-note">The model was trained on historical retail transactions from 2010–2011. '
                "Results demonstrate the project workflow and should not be treated as live customer forecasts.</div>",
                unsafe_allow_html=True,
            )

    except PyMongoError as exc:
        st.error(f"Could not load dashboard data: {type(exc).__name__}")


# -----------------------------------------------------------------------------
# Customer records — CRUD
# -----------------------------------------------------------------------------

elif page == "Customer records":
    page_header(
        "Data workspace · records",
        "Customer records",
        "Create and maintain the profiles used by the application. Profile records are kept separate from historical ML feature snapshots.",
    )

    add_tab, view_tab, edit_tab, remove_tab = st.tabs(
        ["＋ Add new", "⌕ Search & view", "↗ Edit details", "− Remove profile"]
    )

    with add_tab:
        section_header("Register a customer", "Fields marked * are required")
        with st.form("create_customer_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                new_id = st.text_input("Customer ID *", max_chars=50, placeholder="e.g. CUST-1008")
                new_name = st.text_input("Customer name *", max_chars=100, placeholder="Full name")
            with c2:
                new_country = st.text_input("Country *", max_chars=100, placeholder="e.g. India")
                new_notes = st.text_area("Notes", max_chars=500, placeholder="Optional customer notes", height=100)
            submitted = st.form_submit_button("Create customer record", type="primary", use_container_width=True)
        if submitted:
            try:
                document_id = create_customer(new_id, new_name, new_country, new_notes)
                st.success("Customer profile created successfully.")
                st.caption(f"MongoDB document ID: {document_id}")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
            except PyMongoError as exc:
                st.error(f"Database operation failed: {type(exc).__name__}")

    with view_tab:
        section_header("Find a record", "Search by customer ID or name. Add a country filter if useful.")
        with st.form("search_customer_form"):
            c1, c2 = st.columns([1, 1])
            with c1:
                search_text = st.text_input("Customer ID or name", max_chars=100)
            with c2:
                country_filter = st.text_input("Country filter", max_chars=100)
            c3, c4 = st.columns([1, 1])
            with c3:
                page_number = st.number_input("Page", min_value=1, value=1, step=1)
            with c4:
                page_size = st.selectbox("Rows per page", [10, 20, 50, 100], index=1)
            search_submitted = st.form_submit_button("Search records", type="primary", use_container_width=True)
        if search_submitted:
            try:
                st.session_state["pulse_customer_search"] = search_customers(
                    search_text=search_text,
                    country=country_filter or None,
                    page=int(page_number),
                    page_size=page_size,
                )
            except ValueError as exc:
                st.error(str(exc))
            except PyMongoError as exc:
                st.error(f"Search failed: {type(exc).__name__}")
        result = st.session_state.get("pulse_customer_search")
        if result is not None:
            st.caption(f"{result['total']:,} matching record(s) · page {result['page']} of {max(result['total_pages'], 1)}")
            display_customer_table(result["items"])

    with edit_tab:
        section_header("Edit an existing profile", "Leave a field blank to keep its current value.")
        with st.form("update_customer_form"):
            update_id = st.text_input("Customer ID *", max_chars=50, key="pulse_update_id")
            c1, c2 = st.columns(2)
            with c1:
                update_name = st.text_input("New customer name", max_chars=100)
            with c2:
                update_country = st.text_input("New country", max_chars=100)
            update_notes = st.text_area("New notes", max_chars=500, height=100)
            update_submitted = st.form_submit_button("Save changes", type="primary", use_container_width=True)
        if update_submitted:
            try:
                changed = update_customer(
                    customer_id=update_id,
                    customer_name=update_name or None,
                    country=update_country or None,
                    notes=update_notes or None,
                )
                if changed:
                    st.success("Customer profile updated.")
                    st.rerun()
                else:
                    st.warning("No customer profile with that ID was found.")
            except ValueError as exc:
                st.error(str(exc))
            except PyMongoError as exc:
                st.error(f"Update failed: {type(exc).__name__}")

    with remove_tab:
        section_header(
            "Remove a profile",
            "This removes the profile document only. Historical features and prediction history are retained.",
        )
        with st.form("delete_customer_form"):
            delete_id = st.text_input("Customer ID *", max_chars=50, key="pulse_delete_id")
            confirm_delete = st.checkbox("I understand this deletion cannot be undone.")
            delete_submitted = st.form_submit_button("Delete profile", type="primary", use_container_width=True)
        if delete_submitted:
            if not confirm_delete:
                st.warning("Confirm the deletion before continuing.")
            else:
                try:
                    deleted = delete_customer(delete_id)
                    if deleted:
                        st.success("Customer profile deleted.")
                        st.rerun()
                    else:
                        st.warning("No customer profile with that ID was found.")
                except ValueError as exc:
                    st.error(str(exc))
                except PyMongoError as exc:
                    st.error(f"Delete failed: {type(exc).__name__}")


# -----------------------------------------------------------------------------
# Purchase prediction
# -----------------------------------------------------------------------------

elif page == "Purchase prediction":
    page_header(
        "Model workspace · inference",
        "Purchase prediction",
        "Choose a customer with an available historical feature snapshot. PULSE will retrieve the latest snapshot, score it with the saved model, and store the result in MongoDB.",
    )

    st.markdown(
        '<div class="pulse-inline-note">The model reads six features calculated from the previous 90 days '
        "of transactions and estimates a purchase during the following 30-day window. "
        "A profile by itself is not enough to make a prediction.</div>",
        unsafe_allow_html=True,
    )

    with st.form("purchase_prediction_form"):
        c1, c2 = st.columns([2, 1])
        with c1:
            prediction_customer_id = st.text_input(
                "Customer ID", max_chars=50, placeholder="Try an ID such as 12347"
            )
        with c2:
            st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "Run prediction  →", type="primary", use_container_width=True
            )

    if submitted:
        if not prediction_customer_id.strip():
            st.warning("Enter a customer ID to continue.")
        else:
            try:
                status = get_customer_prediction_status(prediction_customer_id)
                if not status["can_predict"]:
                    st.warning(status["message"])
                    st.session_state.pop("pulse_last_prediction", None)
                else:
                    with st.spinner("Retrieving history and scoring customer…"):
                        result = predict_customer_by_id(prediction_customer_id)
                    st.session_state["pulse_last_prediction"] = result
                    st.success("Prediction completed and saved to prediction history.")
            except (ValueError, LookupError, FileNotFoundError) as exc:
                st.error(str(exc))
            except PyMongoError as exc:
                st.error(f"A database operation failed: {type(exc).__name__}")
            except Exception as exc:
                st.error(
                    f"Prediction could not be completed ({type(exc).__name__}). "
                    "Check the application logs."
                )

    result = st.session_state.get("pulse_last_prediction")
    if result:
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        section_header(
            "Prediction result",
            f"Customer {result['customer_id']} · feature snapshot {result.get('feature_snapshot_date') or 'date not recorded'}",
        )
        prob = float(result["purchase_probability"])
        threshold = float(result["threshold"])
        predicted = int(result["predicted_purchase"])
        outcome = "Purchase predicted" if predicted == 1 else "No purchase predicted"
        accent = "#1f4c3f" if predicted == 1 else "#93633c"

        summary_left, summary_right = st.columns([1, 1.25], gap="large")
        with summary_left:
            st.markdown(
                f"""
                <div class="pulse-result">
                  <div class="pulse-result-label">Estimated purchase probability</div>
                  <div class="pulse-result-value">{prob:.2%}</div>
                  <div style="display:inline-block;padding:.35rem .6rem;border-radius:7px;background:{'#e4f3d1' if predicted else '#fff0df'};color:{accent};font-size:.78rem;font-weight:800;margin:.15rem 0 .7rem 0;">{outcome}</div>
                  <div class="pulse-result-foot">Decision threshold · {threshold:.1%}</div>
                  <div class="pulse-result-foot">Model · {result['model_name']}</div>
                  <div class="pulse-result-foot">Version · <span class="pulse-code">{result['model_version']}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with summary_right:
            section_header("Score vs. decision threshold", "The outcome changes when the score crosses the threshold.")
            st.progress(max(0.0, min(prob, 1.0)))
            st.caption(f"Model score: {prob:.1%}")
            st.progress(max(0.0, min(threshold, 1.0)))
            st.caption(f"Decision threshold: {threshold:.1%}")
            if predicted:
                st.markdown('<div class="pulse-inline-note">The score is at or above the selected threshold, so the model assigns class 1.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="pulse-inline-note">The score is below the selected threshold, so the model assigns class 0.</div>', unsafe_allow_html=True)

        with st.expander("Inspect the six model inputs"):
            feature_df = pd.DataFrame(
                [{"Feature": key, "Value": value} for key, value in result["features"].items()]
            )
            st.dataframe(feature_df, hide_index=True, use_container_width=True)
        st.caption(f"Prediction record ID: {result.get('prediction_id', '—')}")
        st.caption("Research prototype: the model uses historical 2010–2011 retail data; its output is not a guarantee of future customer behaviour.")


# -----------------------------------------------------------------------------
# Prediction history
# -----------------------------------------------------------------------------

elif page == "Prediction history":
    page_header(
        "Model workspace · audit trail",
        "Prediction history",
        "Explore saved prediction records, compare outcomes, and trace each result to the model version that generated it.",
    )

    with st.form("prediction_history_form"):
        c1, c2 = st.columns([2, 1])
        with c1:
            history_customer_id = st.text_input("Filter by customer ID (optional)", max_chars=50)
        with c2:
            history_limit = st.selectbox("Records to retrieve", [10, 20, 50, 100], index=1)
        history_submitted = st.form_submit_button("Load records", type="primary", use_container_width=True)

    # Fetch history immediately by default, or when the form is submitted
    try:
        history = get_prediction_history(
            customer_id=history_customer_id or None,
            limit=history_limit,
        )
    except Exception as exc:
        st.error(f"Could not retrieve prediction history: {type(exc).__name__}")
        history = []

    if not history:
        st.info("No prediction records found for this filter.")
    else:
        probs = [float(item["purchase_probability"]) for item in history if item.get("purchase_probability") is not None]
        positive = sum(1 for item in history if item.get("predicted_purchase") == 1)
        h1, h2, h3 = st.columns(3)
        h1.metric("Records shown", len(history))
        h2.metric("Purchase predictions", positive)
        h3.metric("Mean model score", f"{sum(probs) / len(probs):.1%}" if probs else "—")

        rows = []
        for item in history:
            probability = item.get("purchase_probability")
            outcome = "Purchase predicted" if item.get("predicted_purchase") == 1 else "No purchase predicted"
            rows.append({
                "Customer ID": item.get("customer_id", "—"),
                "Outcome": outcome,
                "Purchase probability": f"{probability:.2%}" if probability is not None else "—",
                "Threshold": f"{item['threshold']:.1%}" if item.get("threshold") is not None else "—",
                "Feature snapshot": pretty_date(item.get("feature_snapshot_date")),
                "Prediction saved": pretty_date(item.get("created_at")),
                "Model": item.get("model_name", "—"),
                "Version": item.get("model_version", "—"),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("Prediction history is an audit trail of model outputs, not a record of confirmed purchases.")


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------

st.markdown(
    """
    <div class="pulse-footer">
      <span>PULSE · Customer Purchase Intelligence</span>
      <span>Machine learning × MongoDB Atlas · Academic project prototype</span>
    </div>
    """,
    unsafe_allow_html=True,
)