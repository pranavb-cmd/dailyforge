import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="DailyForge", page_icon="🔥", layout="wide")

st.title("🔥 DailyForge")
st.error("Google Sheets connection is having issues. Using local fallback for now.")

# Temporary local fallback (so the app at least opens)
data = {
    "tasks": [],
    "projects": [{"name": "Mobile Banking App", "active": True}, {"name": "E-commerce Platform", "active": True}],
    "engineers": ["Alice Sharma", "Rahul Verma", "Priya Patel", "Arjun Rao", "Neha Gupta", "Vikram Singh"],
    "users": {
        "manager": {"pranav": {"password": "manager123", "role": "manager", "name": "PRANAV"}},
        "engineer": {
            "alice": {"password": "alice123", "role": "engineer", "name": "Alice Sharma"},
            "rahul": {"password": "rahul123", "role": "engineer", "name": "Rahul Verma"}
        }
    }
}

# ===================== LOGIN =====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔥 DailyForge")
    st.markdown("### Project Task Dashboard")
    st.markdown("#### Login")

    col1, col2 = st.columns([1, 1])
    with col1:
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True, type="primary"):
            if username in data["users"].get("manager", {}) and data["users"]["manager"][username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = "manager"
                st.session_state.full_name = data["users"]["manager"][username]["name"]
                st.rerun()
            elif username in data["users"].get("engineer", {}) and data["users"]["engineer"][username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = "engineer"
                st.session_state.full_name = data["users"]["engineer"][username]["name"]
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    with col2:
        st.info("Contact your administrator if you don't have login credentials.")

    st.caption("Only authorized users can access the dashboard.")
    st.stop()

st.sidebar.image("https://img.icons8.com/fluency/96/fire.png", width=70)
st.sidebar.title("DailyForge")
st.sidebar.markdown(f"**{st.session_state.full_name}**")

if st.sidebar.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.title("App is running in fallback mode")
st.info("Google Sheets connection failed. Using local memory for this session.")

st.caption("DailyForge - Fallback Mode")
