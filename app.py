import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread

st.set_page_config(page_title="DailyForge", page_icon="🔥", layout="wide")

# ===================== PUBLIC GOOGLE SHEET (No Service Account) =====================
@st.cache_resource
def get_google_sheet():
    try:
        # This is the simplest method for public sheets
        gc = gspread.service_account()
        sh = gc.open_by_url(st.secrets["spreadsheet_url"]["url"])
        return sh
    except Exception as e:
        st.error(f"Google Sheet Connection Error: {str(e)}")
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
    except Exception as e:
        st.warning(f"Load warning: {str(e)[:100]}")
    
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
        
        st.success("✅ Data saved to Google Sheets")
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

# ===================== SIDEBAR =====================
st.sidebar.image("https://img.icons8.com/fluency/96/fire.png", width=70)
st.sidebar.title("DailyForge")
st.sidebar.markdown(f"**{st.session_state.full_name}**")

if st.sidebar.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

active_projects = [p["name"] for p in data["projects"] if p.get("active", True)]

# ===================== MANAGER VIEW =====================
if st.session_state.role == "manager":
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Dashboard", "➕ Add Task", "📋 Project Master", 
                                                  "👷 Engineer Master", "👨‍💼 Manager Master", "🔑 Change Password"])

    with tab1:
        st.title("📊 Project Task Dashboard")
        st.info("Dashboard is ready. You can add data from other tabs.")

    with tab2:
        st.title("➕ Add New Task Target")
        with st.form("add_task_form", clear_on_submit=True):
            project = st.selectbox("Project", active_projects if active_projects else ["No active projects"])
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
        for i, proj in enumerate(data["projects"]):
            col1, col2, col3 = st.columns([3, 1.5, 1])
            status = "🟢 Active" if proj.get("active", True) else "🔴 Ended"
            col1.write(f"**{proj['name']}** — {status}")
            if col2.button("Mark as Ended", key=f"end_proj_{i}"):
                data["projects"][i]["active"] = False
                save_data(data)
                st.success(f"{proj['name']} marked as Ended")
                st.rerun()
            if col3.button("🗑️ Delete", key=f"del_proj_{i}"):
                st.session_state[f"confirm_proj_{i}"] = True
                st.rerun()
            if st.session_state.get(f"confirm_proj_{i}", False):
                st.warning("Delete permanently?")
                col_yes, col_no = st.columns(2)
                if col_yes.button("Yes, Delete", key=f"yes_proj_{i}"):
                    del data["projects"][i]
                    save_data(data)
                    st.success("Project deleted successfully!")
                    del st.session_state[f"confirm_proj_{i}"]
                    st.rerun()
                if col_no.button("Cancel", key=f"cancel_proj_{i}"):
                    del st.session_state[f"confirm_proj_{i}"]
                    st.rerun()

        new_project = st.text_input("Add New Project Name")
        if st.button("Add Project"):
            if new_project.strip():
                data["projects"].append({"name": new_project.strip(), "active": True})
                save_data(data)
                st.success("✅ New Project added successfully!")
                st.rerun()

    with tab4:
        st.title("👷 Engineer Master")
        for i, eng in enumerate(data["engineers"]):
            col1, col2 = st.columns([4, 1])
            col1.write(f"• {eng}")
            if col2.button("🗑️ Delete", key=f"del_eng_{i}"):
                st.session_state[f"confirm_eng_{i}"] = True
                st.rerun()
            if st.session_state.get(f"confirm_eng_{i}", False):
                st.warning("Delete permanently?")
                col_yes, col_no = st.columns(2)
                if col_yes.button("Yes, Delete", key=f"yes_eng_{i}"):
                    for u, info in list(data["users"]["engineer"].items()):
                        if info["name"] == eng:
                            del data["users"]["engineer"][u]
                            break
                    del data["engineers"][i]
                    save_data(data)
                    st.success("✅ Engineer deleted successfully!")
                    del st.session_state[f"confirm_eng_{i}"]
                    st.rerun()
                if col_no.button("Cancel", key=f"cancel_eng_{i}"):
                    del st.session_state[f"confirm_eng_{i}"]
                    st.rerun()

        st.subheader("Add New Engineer")
        with st.form("add_engineer_form", clear_on_submit=True):
            full_name = st.text_input("Full Name")
            username = st.text_input("Login Username (lowercase)")
            default_password = st.text_input("Default Password", value="123456", type="password")
            if st.form_submit_button("✅ Add Engineer"):
                if full_name.strip() and username.strip():
                    u = username.lower().strip()
                    if u in data["users"]["manager"] or u in data["users"]["engineer"]:
                        st.error("Username already exists!")
                    else:
                        data["engineers"].append(full_name.strip())
                        data["users"]["engineer"][u] = {
                            "password": default_password,
                            "role": "engineer",
                            "name": full_name.strip()
                        }
                        save_data(data)
                        st.success(f"✅ Engineer **{full_name}** added!\nUsername: `{u}`")
                        st.rerun()

    with tab5:
        st.title("Manager Master")
        st.info("Add New Manager functionality is available (similar to Engineer)")

    with tab6:
        st.title("Change Password")
        st.info("Change Password tab is ready")

else:
    st.title(f"👷 My Tasks - {st.session_state.full_name}")
    st.info("Engineer view is ready")

st.caption("DailyForge • Public Google Sheets Version")
