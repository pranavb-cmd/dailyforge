import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread

st.set_page_config(page_title="DailyForge", page_icon="🔥", layout="wide")

# ===================== SIMPLE GOOGLE SHEETS CONNECTION =====================
@st.cache_resource
def get_google_sheet():
    try:
        # Simple method - using public sheet
        gc = gspread.service_account_from_dict({
            "type": "service_account",
            "project_id": "dailyforge",
            "private_key_id": "dummy",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",  # dummy
            "client_email": "dummy@dummy.iam.gserviceaccount.com",
            "client_id": "dummy",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        })
        sh = gc.open_by_url(st.secrets["spreadsheet_url"]["url"])
        st.sidebar.success("Connected to Google Sheet")
        return sh
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        st.stop()

def load_data():
    sheet = get_google_sheet()
    data = {"tasks": [], "projects": [], "engineers": [], "users": {"manager": {}, "engineer": {}}}
    
    try:
        # Tasks
        df = pd.DataFrame(sheet.worksheet("Tasks").get_all_records())
        data["tasks"] = df.to_dict('records') if not df.empty else []
        
        # Projects
        df = pd.DataFrame(sheet.worksheet("Projects").get_all_records())
        data["projects"] = df.to_dict('records') if not df.empty else []
        
        # Engineers
        df = pd.DataFrame(sheet.worksheet("Engineers").get_all_records())
        data["engineers"] = df['name'].tolist() if not df.empty else []
        
        # Users
        df = pd.DataFrame(sheet.worksheet("Users").get_all_records())
        for _, row in df.iterrows():
            role = str(row.get('role', '')).strip()
            username = str(row.get('username', '')).strip()
            if role and username:
                data["users"][role][username] = {
                    "password": str(row.get('password', '')),
                    "role": role,
                    "name": str(row.get('name', ''))
                }
    except:
        pass  # fallback to defaults
    
    return data

def save_data(data):
    try:
        sheet = get_google_sheet()
        
        # Tasks
        if data["tasks"]:
            df = pd.DataFrame(data["tasks"])
            ws = sheet.worksheet("Tasks")
            ws.clear()
            ws.update([df.columns.tolist()] + df.values.tolist())
        
        # Projects
        if data["projects"]:
            df = pd.DataFrame(data["projects"])
            ws = sheet.worksheet("Projects")
            ws.clear()
            ws.update([df.columns.tolist()] + df.values.tolist())
        
        # Engineers
        if data["engineers"]:
            df = pd.DataFrame({"name": data["engineers"]})
            ws = sheet.worksheet("Engineers")
            ws.clear()
            ws.update([df.columns.tolist()] + df.values.tolist())
        
        # Users
        users_list = []
        for role, user_dict in data["users"].items():
            for username, info in user_dict.items():
                users_list.append({
                    "role": role,
                    "username": username,
                    "password": info.get("password", ""),
                    "name": info.get("name", "")
                })
        if users_list:
            df = pd.DataFrame(users_list)
            ws = sheet.worksheet("Users")
            ws.clear()
            ws.update([df.columns.tolist()] + df.values.tolist())
        
        return True
    except Exception as e:
        st.error(f"Save failed: {str(e)}")
        return False

data = load_data()

# Login and rest of the app (same as before)
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

# Sidebar and main app (shortened for this test)
st.sidebar.image("https://img.icons8.com/fluency/96/fire.png", width=70)
st.sidebar.title("DailyForge")
st.sidebar.markdown(f"**{st.session_state.full_name}**")

if st.sidebar.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.title("Test Page")
st.write("If you can see this, the app is running.")
st.info("Please test adding an engineer or project now.")

# Add Engineer Test
st.subheader("Add New Engineer Test")
with st.form("test_add_eng"):
    name = st.text_input("Full Name")
    if st.form_submit_button("Add Engineer"):
        if name:
            if name not in data["engineers"]:
                data["engineers"].append(name)
                if save_data(data):
                    st.success("✅ Engineer added and saved!")
                st.rerun()
            else:
                st.error("Already exists")

st.caption("DailyForge Test Version")
