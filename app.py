import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import json

st.set_page_config(page_title="DailyForge", page_icon="🔥", layout="wide")

# ===================== JSONBIN CONFIG =====================
BIN_ID = "69d878a136566621a898e722"
MASTER_KEY = "$2a$10$NSKmpUiTMsoarXkJeNDTReI6DkE6/OsW0tmRFImAumbDsd5I3aSL2"
API_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": MASTER_KEY
}

def load_data():
    try:
        response = requests.get(f"{API_URL}/latest", headers=HEADERS)
        if response.status_code == 200:
            record = response.json()["record"]
            data = {
                "tasks": record.get("tasks", []),
                "projects": record.get("projects", []),
                "engineers": record.get("engineers", []),
                "users": record.get("users", {"manager": {}, "engineer": {}})
            }
            return data
        else:
            st.warning("Could not load data from cloud. Using defaults.")
    except:
        st.warning("Connection issue. Using defaults.")
    
    # Default data
    return {
        "tasks": [],
        "projects": [
            {"name": "Mobile Banking App", "active": True},
            {"name": "E-commerce Platform", "active": True},
            {"name": "Internal CRM", "active": True},
            {"name": "Payment Gateway", "active": True}
        ],
        "engineers": ["Alice Sharma", "Rahul Verma", "Priya Patel", "Arjun Rao", "Neha Gupta", "Vikram Singh"],
        "users": {
            "manager": {"pranav": {"password": "manager123", "role": "manager", "name": "PRANAV"}},
            "engineer": {
                "alice": {"password": "alice123", "role": "engineer", "name": "Alice Sharma"},
                "rahul": {"password": "rahul123", "role": "engineer", "name": "Rahul Verma"}
            }
        }
    }

def save_data(data):
    try:
        response = requests.put(API_URL, headers=HEADERS, json=data)
        if response.status_code in [200, 201]:
            st.toast("✅ Data saved successfully to cloud!", icon="✅")
            return True
        else:
            st.error(f"Save failed. Status: {response.status_code}")
            return False
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
st.sidebar.markdown(f"**{st.session_state.full_name}** ({st.session_state.role.upper()})")

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
        view_mode = st.radio("View Mode", ["Single Date", "Date Range Overview"], horizontal=True)

        if view_mode == "Single Date":
            selected_date = st.date_input("Select Date", datetime.now().date())
            tasks_list = [t for t in data.get("tasks", []) if t.get("date") == selected_date.strftime("%Y-%m-%d")]
            st.subheader(f"Tasks for {selected_date.strftime('%Y-%m-%d')}")
        else:
            st.subheader("Date Range Overview")
            col_a, col_b, col_c = st.columns([2, 2, 1.5])
            with col_a:
                from_date = st.date_input("From Date", datetime.now().date() - timedelta(days=30))
            with col_b:
                to_date = st.date_input("To Date", datetime.now().date())
            with col_c:
                status_filter = st.selectbox("Filter Tasks", ["All Tasks", "Only Pending", "Only In Progress"])

            from_str = from_date.strftime("%Y-%m-%d")
            to_str = to_date.strftime("%Y-%m-%d")
            
            tasks_list = [t for t in data.get("tasks", []) if from_str <= t.get("date", "") <= to_str]
            if status_filter == "Only Pending":
                tasks_list = [t for t in tasks_list if t.get("progress", 0) == 0]
            elif status_filter == "Only In Progress":
                tasks_list = [t for t in tasks_list if 0 < t.get("progress", 0) < 100]

        if tasks_list:
            df = pd.DataFrame(tasks_list)
            df["Progress %"] = df["progress"]
            df["Status"] = df["progress"].apply(lambda x: "✅ Completed" if x == 100 else "🔄 In Progress" if x > 0 else "⏳ Pending")
            
            def color_row(row):
                if row['progress'] == 100:
                    return ['background-color: #d4edda'] * len(row)
                elif row['progress'] > 0:
                    return ['background-color: #fff3cd'] * len(row)
                else:
                    return ['background-color: #f8d7da'] * len(row)
            
            styled_df = df.style.apply(color_row, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

            total = len(tasks_list)
            completed = sum(1 for t in tasks_list if t.get("progress", 0) == 100)
            pending = sum(1 for t in tasks_list if t.get("progress", 0) == 0)
            in_progress = total - completed - pending
            avg = sum(t.get("progress", 0) for t in tasks_list) // total if total > 0 else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Tasks", total)
            c2.metric("Completed", completed)
            c3.metric("In Progress", in_progress)
            c4.metric("Pending", pending)
            st.metric("Average Progress", f"{avg}%")
        else:
            st.info("No tasks found.")

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
        for uname, info in data["users"]["manager"].items():
            st.write(f"• **{info['name']}** (Username: `{uname}`)")

        st.subheader("Add New Manager")
        with st.form("add_manager_form", clear_on_submit=True):
            manager_name = st.text_input("Full Name")
            manager_username = st.text_input("Login Username")
            manager_password = st.text_input("Password", value="manager123", type="password")
            if st.form_submit_button("✅ Add Manager"):
                if manager_name.strip() and manager_username.strip():
                    mu = manager_username.lower().strip()
                    if mu in data["users"]["manager"] or mu in data["users"]["engineer"]:
                        st.error("Username already exists!")
                    else:
                        data["users"]["manager"][mu] = {
                            "password": manager_password,
                            "role": "manager",
                            "name": manager_name.strip()
                        }
                        save_data(data)
                        st.success(f"✅ New Manager **{manager_name}** added!\nUsername: `{mu}`")
                        st.rerun()

    with tab6:
        st.title("Change Password")
        np = st.text_input("New Password", type="password")
        cp = st.text_input("Confirm Password", type="password")
        if st.button("Update Password"):
            if np == cp and np:
                if st.session_state.role == "manager":
                    data["users"]["manager"][st.session_state.username]["password"] = np
                else:
                    data["users"]["engineer"][st.session_state.username]["password"] = np
                save_data(data)
                st.success("Password changed successfully!")
            else:
                st.error("Passwords do not match")

# ===================== ENGINEER VIEW =====================
else:
    st.title(f"👷 My Tasks - {st.session_state.full_name}")
    my_tasks = [t for t in data.get("tasks", []) if t.get("assigned") == st.session_state.full_name]
    
    if my_tasks:
        for task in my_tasks:
            status_emoji = "🟢" if task.get("progress",0) == 100 else "🟠" if task.get("progress",0) > 0 else "🔴"
            with st.expander(f"{status_emoji} {task.get('date','')} | {task['project']} — {task['description'][:60]}...", expanded=False):
                new_progress = st.slider("Progress", 0, 100, task.get("progress", 0), key=f"p_{task['id']}")
                new_notes = st.text_area("Update Note", value=task.get("notes",""), key=f"n_{task['id']}")
                if st.button("Save Update", key=f"s_{task['id']}"):
                    for t in data["tasks"]:
                        if t["id"] == task["id"]:
                            t["progress"] = new_progress
                            t["notes"] = new_notes.strip()
                            t["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            break
                    save_data(data)
                    st.success("✅ Progress updated successfully!")
                    st.rerun()
    else:
        st.info("No tasks assigned to you.")

st.caption("DailyForge • Persistent Storage via JSONBin")
