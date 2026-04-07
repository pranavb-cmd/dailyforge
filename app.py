import streamlit as st
import pandas as pd
from datetime import datetime
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

# ===================== LOGIN =====================
if not st.session_state.logged_in:
    st.title("🔥 DailyForge - Login")
    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
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
                st.error("Invalid credentials")
    st.caption("Manager: pranav / manager123")
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
        view_mode = st.radio("View Mode", ["Single Date", "All Dates Overview"], horizontal=True)
        
        if view_mode == "Single Date":
            selected_date = st.date_input("Select Date", datetime.now().date())
            current_date_str = selected_date.strftime("%Y-%m-%d")
            tasks_list = [t for t in data.get("tasks", []) if t.get("date") == current_date_str]
            st.subheader(f"Tasks for {current_date_str}")
        else:
            tasks_list = data.get("tasks", [])
            st.subheader("All Tasks Overview")

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
            
            styled = df.style.apply(color_row, axis=1)
            st.dataframe(styled, use_container_width=True, hide_index=True)

            total = len(tasks_list)
            completed = sum(1 for t in tasks_list if t.get("progress", 0) == 100)
            pending = sum(1 for t in tasks_list if t.get("progress", 0) == 0)
            avg = sum(t.get("progress", 0) for t in tasks_list) // total if total > 0 else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Tasks", total)
            c2.metric("Completed", completed)
            c3.metric("Pending", pending)
            c4.metric("Avg Progress", f"{avg}%")
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
                    save_data(data)
                    st.success("Task added successfully!")
                    st.rerun()

    # Project Master, Engineer Master, Manager Master, Change Password tabs (same as before)
    with tab3:
        st.title("Project Master")
        for i, proj in enumerate(data["projects"]):
            col1, col2, col3 = st.columns([3,1.5,1])
            status = "🟢 Active" if proj.get("active", True) else "🔴 Ended"
            col1.write(f"**{proj['name']}** — {status}")
            if col2.button("Mark Ended", key=f"end_{i}"):
                data["projects"][i]["active"] = False
                save_data(data)
                st.success(f"{proj['name']} marked Ended")
                st.rerun()
            if col3.button("Delete", key=f"delp_{i}"):
                st.session_state[f"confp_{i}"] = True
                st.rerun()
            if st.session_state.get(f"confp_{i}", False):
                st.warning("Delete permanently?")
                if st.button("Yes Delete", key=f"yesdelp_{i}"):
                    del data["projects"][i]
                    save_data(data)
                    st.success("Deleted")
                    del st.session_state[f"confp_{i}"]
                    st.rerun()

        new_p = st.text_input("New Project Name")
        if st.button("Add Project"):
            if new_p.strip():
                data["projects"].append({"name": new_p.strip(), "active": True})
                save_data(data)
                st.success("Project added")
                st.rerun()

    with tab4:
        st.title("Engineer Master")
        for i, eng in enumerate(data["engineers"]):
            col1, col2 = st.columns([4,1])
            col1.write(f"• {eng}")
            if col2.button("Delete", key=f"dele_{i}"):
                st.session_state[f"confe_{i}"] = True
                st.rerun()
            if st.session_state.get(f"confe_{i}", False):
                st.warning("Delete permanently?")
                if st.button("Yes Delete", key=f"yesdele_{i}"):
                    for u, info in list(data["users"]["engineer"].items()):
                        if info["name"] == eng:
                            del data["users"]["engineer"][u]
                            break
                    del data["engineers"][i]
                    save_data(data)
                    st.success("Engineer deleted")
                    del st.session_state[f"confe_{i}"]
                    st.rerun()

        st.subheader("Add New Engineer")
        with st.form("add_eng", clear_on_submit=True):
            fname = st.text_input("Full Name")
            uname = st.text_input("Username (lowercase)")
            passw = st.text_input("Default Password", value="123456", type="password")
            if st.form_submit_button("Add Engineer"):
                if fname and uname:
                    u = uname.lower().strip()
                    if u not in data["users"]["engineer"] and u not in data["users"]["manager"]:
                        data["engineers"].append(fname.strip())
                        data["users"]["engineer"][u] = {"password": passw, "role": "engineer", "name": fname.strip()}
                        save_data(data)
                        st.success(f"Engineer added! Username: {u}")
                        st.rerun()

    with tab5:
        st.title("Manager Master")
        st.subheader("Current Managers")
        for u, info in data["users"]["manager"].items():
            st.write(f"• {info['name']} (Username: {u})")

        st.subheader("Add New Manager")
        with st.form("add_mgr", clear_on_submit=True):
            mname = st.text_input("Full Name")
            muser = st.text_input("Username")
            mpass = st.text_input("Password", value="manager123", type="password")
            if st.form_submit_button("Add Manager"):
                if mname and muser:
                    mu = muser.lower().strip()
                    if mu not in data["users"]["manager"] and mu not in data["users"]["engineer"]:
                        data["users"]["manager"][mu] = {"password": mpass, "role": "manager", "name": mname.strip()}
                        save_data(data)
                        st.success("New Manager added!")
                        st.rerun()

    with tab6:
        st.title("Change Password")
        np = st.text_input("New Password", type="password")
        cp = st.text_input("Confirm Password", type="password")
        if st.button("Change Password"):
            if np == cp and np:
                if st.session_state.role == "manager":
                    data["users"]["manager"][st.session_state.username]["password"] = np
                else:
                    data["users"]["engineer"][st.session_state.username]["password"] = np
                save_data(data)
                st.success("Password updated successfully!")
            else:
                st.error("Passwords don't match")

# ===================== ENGINEER VIEW (Improved) =====================
else:
    st.title(f"👷 My Daily Tasks - {st.session_state.full_name}")

    my_tasks = [t for t in data.get("tasks", []) if t.get("assigned") == st.session_state.full_name]

    if my_tasks:
        for task in my_tasks:
            status_color = "🟢 Completed" if task.get("progress", 0) == 100 else "🟠 In Progress" if task.get("progress", 0) > 0 else "🔴 Pending"
            
            with st.expander(f"{task.get('date','')} | {task['project']} | {status_color} | {task['description'][:50]}...", expanded=True):
                st.write(f"**Current Progress:** {task.get('progress', 0)}%")
                
                new_progress = st.slider("Update Progress", 0, 100, task.get("progress", 0), key=f"prog_{task['id']}")
                new_notes = st.text_area("Update Note (What you did today)", value=task.get("notes", ""), key=f"note_{task['id']}")
                
                if st.button("💾 Save Update", key=f"save_{task['id']}"):
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
        st.info("You have no tasks assigned yet.")

st.caption("DailyForge • Engineer view with clear status colors & success messages")
