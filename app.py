import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread

st.set_page_config(page_title="DailyForge", page_icon="🔥", layout="wide")

# ===================== SIMPLE PUBLIC GOOGLE SHEET CONNECTION =====================
@st.cache_resource
def get_google_sheet():
    try:
        # This method works with public sheets
        gc = gspread.service_account_from_dict({
            "type": "service_account",
            "project_id": "dailyforge",
            "private_key_id": "1",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",  
            "client_email": "dummy@dummy.iam.gserviceaccount.com",
            "client_id": "1",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        })
        sh = gc.open_by_url(st.secrets["spreadsheet_url"]["url"])
        st.sidebar.success("✅ Connected to Google Sheet")
        return sh
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        st.stop()

def load_data():
    sheet = get_google_sheet()
    data = {"tasks": [], "projects": [], "engineers": [], "users": {"manager": {}, "engineer": {}}}
    
    try:
        df = pd.DataFrame(sheet.worksheet("Tasks").get_all_records())
        data["tasks"] = df.to_dict('records') if not df.empty else []
        
        df = pd.DataFrame(sheet.worksheet("Projects").get_all_records())
        data["projects"] = df.to_dict('records') if not df.empty else []
        
        df = pd.DataFrame(sheet.worksheet("Engineers").get_all_records())
        data["engineers"] = df['name'].tolist() if not df.empty else []
        
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
        pass
    
    return data

def save_data(data):
    try:
        sheet = get_google_sheet()
        
        if data.get("tasks"):
            df = pd.DataFrame(data["tasks"])
            ws = sheet.worksheet("Tasks")
            ws.clear()
            ws.update([df.columns.tolist()] + df.values.tolist())
        
        if data.get("projects"):
            df = pd.DataFrame(data["projects"])
            ws = sheet.worksheet("Projects")
            ws.clear()
            ws.update([df.columns.tolist()] + df.values.tolist())
        
        if data.get("engineers"):
            df = pd.DataFrame({"name": data["engineers"]})
            ws = sheet.worksheet("Engineers")
            ws.clear()
            ws.update([df.columns.tolist()] + df.values.tolist())
        
        users_list = []
        for role, user_dict in data.get("users", {}).items():
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
        
        st.success("Data saved successfully!")
        return True
    except Exception as e:
        st.error(f"Save failed: {str(e)}")
        return False

data = load_data()

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

# ===================== MAIN APP =====================
st.sidebar.image("https://img.icons8.com/fluency/96/fire.png", width=70)
st.sidebar.title("DailyForge")
st.sidebar.markdown(f"**{st.session_state.full_name}**")

if st.sidebar.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

if st.session_state.role == "manager":
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Dashboard", "➕ Add Task", "📋 Project Master", 
                                                  "👷 Engineer Master", "👨‍💼 Manager Master", "🔑 Change Password"])

    with tab1:
        st.title("📊 Dashboard")
        st.info("Dashboard ready")

    with tab2:
        st.title("➕ Add New Task Target")
        with st.form("add_task_form", clear_on_submit=True):
            project = st.selectbox("Project", [p.get("name", "") for p in data["projects"] if p.get("active", True)])
            description = st.text_area("Task Description")
            assigned = st.selectbox("Assign to Engineer", data["engineers"])
            if st.form_submit_button("✅ Add Task Target"):
                if description.strip():
                    new_task = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "project": project,
                        "description": description.strip(),
                        "assigned": assigned,
                        "progress": 0,
                        "notes": "",
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    data["tasks"].append(new_task)
                    if save_data(data):
                        st.success("✅ Task added successfully!")
                    st.rerun()

    with tab3:
        st.title("📋 Project Master")
        new_project = st.text_input("New Project Name")
        if st.button("Add Project"):
            if new_project.strip():
                data["projects"].append({"name": new_project.strip(), "active": True})
                save_data(data)
                st.success("✅ Project added!")
                st.rerun()

    with tab4:
        st.title("👷 Engineer Master")
        new_eng = st.text_input("New Engineer Name")
        if st.button("Add Engineer"):
            if new_eng.strip() and new_eng.strip() not in data["engineers"]:
                data["engineers"].append(new_eng.strip())
                save_data(data)
                st.success("✅ Engineer added!")
                st.rerun()

    st.info("Other tabs coming soon")

else:
    st.title("My Tasks")
    st.info("Engineer view coming soon")

st.caption("DailyForge • Simple Google Sheets Version")
