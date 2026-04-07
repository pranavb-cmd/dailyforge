import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

DATA_FILE = "daily_tasks.json"

st.set_page_config(page_title="DailyForge", page_icon="🔥", layout="wide")

# ===================== SAFE LOAD DATA =====================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                loaded.setdefault("tasks", [])
                loaded.setdefault("projects", [
                    {"name": "Mobile Banking App", "active": True},
                    {"name": "E-commerce Platform", "active": True},
                    {"name": "Internal CRM", "active": True},
                    {"name": "Payment Gateway", "active": True}
                ])
                loaded.setdefault("engineers", ["Alice Sharma", "Rahul Verma", "Priya Patel", "Arjun Rao", "Neha Gupta", "Vikram Singh"])
                loaded.setdefault("users", {
                    "manager": {"pranav": {"password": "manager123", "role": "manager", "name": "PRANAV"}},
                    "engineer": {
                        "alice": {"password": "alice123", "role": "engineer", "name": "Alice Sharma"},
                        "rahul": {"password": "rahul123", "role": "engineer", "name": "Rahul Verma"},
                        "priya": {"password": "priya123", "role": "engineer", "name": "Priya Patel"},
                        "arjun": {"password": "arjun123", "role": "engineer", "name": "Arjun Rao"},
                        "neha": {"password": "neha123", "role": "engineer", "name": "Neha Gupta"},
                        "vikram": {"password": "vikram123", "role": "engineer", "name": "Vikram Singh"}
                    }
                })
                return loaded
        except:
            pass
    
    default_data = {
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
                "rahul": {"password": "rahul123", "role": "engineer", "name": "Rahul Verma"},
                "priya": {"password": "priya123", "role": "engineer", "name": "Priya Patel"},
                "arjun": {"password": "arjun123", "role": "engineer", "name": "Arjun Rao"},
                "neha": {"password": "neha123", "role": "engineer", "name": "Neha Gupta"},
                "vikram": {"password": "vikram123", "role": "engineer", "name": "Vikram Singh"}
            }
        }
    }
    save_data(default_data)
    return default_data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

data = load_data()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.full_name = None

# ===================== CLEAN LOGIN SCREEN (No Credentials Shown) =====================
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
        st.info("""
        **Need access?**  
        Contact your administrator to get your login credentials.
        """)

    st.caption("Only authorized users can access the dashboard.")
    st.stop()

# ===================== REST OF THE APP =====================
st.sidebar.image("https://img.icons8.com/fluency/96/fire.png", width=70)
st.sidebar.title("DailyForge")
st.sidebar.markdown(f"**{st.session_state.full_name}** ({st.session_state.role.upper()})")

if st.sidebar.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

active_projects = [p["name"] for p in data["projects"] if p.get("active", True)]

# Manager Dashboard with Date Range
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
            
            tasks_list = []
            for t in data.get("tasks", []):
                if from_str <= t.get("date", "") <= to_str:
                    progress = t.get("progress", 0)
                    if (status_filter == "All Tasks") or \
                       (status_filter == "Only Pending" and progress == 0) or \
                       (status_filter == "Only In Progress" and 0 < progress < 100):
                        tasks_list.append(t)

        if tasks_list:
            df = pd.DataFrame(tasks_list)
            df["Progress %"] = df["progress"]
            df["Status"] = df["progress"].apply(lambda x: 
                "✅ Completed" if x == 100 else "🔄 In Progress" if x > 0 else "⏳ Pending")
            
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
            st.info("No tasks found in the selected range/filter.")

    # Add Task Tab
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
                    save_data(data)
                    st.success("Task added successfully!")
                    st.rerun()

    # Other tabs (Project Master, Engineer Master, etc.) - Keep them as they were in previous version
    # For brevity, I'm showing only the important change. You can keep the rest same.

    with tab3:
        st.title("Project Master")
        st.info("Project Master functionality remains the same.")

    with tab4:
        st.title("Engineer Master")
        st.info("Engineer Master functionality remains the same.")

    with tab5:
        st.title("Manager Master")
        st.info("Manager Master functionality remains the same.")

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

st.caption("DailyForge • Secure Login")
