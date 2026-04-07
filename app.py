import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# ===================== CONFIG =====================
DATA_FILE = "daily_tasks.json"

st.set_page_config(page_title="DailyForge", page_icon="🔥", layout="wide")

# ===================== LOAD / SAVE =====================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # Default data
    return {
        "tasks": [],
        "projects": ["Mobile Banking App", "E-commerce Platform", "Internal CRM", "Payment Gateway"],
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

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

data = load_data()

# ===================== SESSION STATE =====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.full_name = None

# ===================== LOGIN PAGE =====================
if not st.session_state.logged_in:
    st.title("🔥 DailyForge - Login")
    st.markdown("**Project Task Dashboard**")

    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("Username", placeholder="pranav / alice / rahul ...")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            # Check Manager
            if username in data["users"]["manager"] and data["users"]["manager"][username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = "manager"
                st.session_state.full_name = data["users"]["manager"][username]["name"]
                st.rerun()
            
            # Check Engineer
            elif username in data["users"]["engineer"] and data["users"]["engineer"][username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = "engineer"
                st.session_state.full_name = data["users"]["engineer"][username]["name"]
                st.rerun()
            else:
                st.error("Invalid username or password")
    st.caption("Manager: pranav / manager123   |   Engineers: alice / alice123 etc.")
    st.stop()

# ===================== LOGGED IN DASHBOARD =====================
st.sidebar.image("https://img.icons8.com/fluency/96/fire.png", width=70)
st.sidebar.title(f"🔥 DailyForge")
st.sidebar.markdown(f"**{st.session_state.full_name}** ({st.session_state.role.upper()})")

current_date = st.sidebar.date_input("Select Date", datetime.now().date())
current_date_str = current_date.strftime("%Y-%m-%d")

if st.sidebar.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Filter tasks
tasks_today = [t for t in data.get("tasks", []) if t["date"] == current_date_str]

# ===================== MANAGER INTERFACE =====================
if st.session_state.role == "manager":
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Add Task", "📋 Project Master", "👷 Engineer Master"])

    # TAB 1: Dashboard
    with tab1:
        st.title(f"Dashboard - {current_date_str}")
        col1, col2, col3, col4 = st.columns(4)
        total = len(tasks_today)
        completed = sum(1 for t in tasks_today if t.get("progress", 0) == 100)
        avg = sum(t.get("progress", 0) for t in tasks_today) // total if total else 0

        col1.metric("Total Tasks", total)
        col2.metric("Completed", completed)
        col3.metric("In Progress", total - completed)
        col4.metric("Overall Progress", f"{avg}%")

        st.subheader("Today's Tasks")
        if tasks_today:
            df = pd.DataFrame(tasks_today)
            df["Progress"] = df["progress"].apply(lambda x: f"{x}%")
            df["Status"] = df["progress"].apply(lambda x: "✅ Completed" if x == 100 else "🔄 In Progress" if x > 0 else "⏳ Pending")
            st.dataframe(df[["project", "description", "assigned", "Progress", "Status", "last_updated", "notes"]], 
                        use_container_width=True, hide_index=True)
        else:
            st.info("No tasks for this date yet.")

    # TAB 2: Add Task
    with tab2:
        st.title("Add New Task Target")
        with st.form("add_task_form", clear_on_submit=True):
            project = st.selectbox("Project", data["projects"])
            description = st.text_area("Task Description")
            assigned = st.selectbox("Assign to Engineer", data["engineers"])
            
            submitted = st.form_submit_button("✅ Add Task Target")
            if submitted:
                if description.strip():
                    new_task = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "date": current_date_str,
                        "project": project,
                        "description": description.strip(),
                        "assigned": assigned,
                        "progress": 0,
                        "notes": "",
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    data["tasks"].append(new_task)
                    save_data(data)
                    st.success("Task added successfully! Form cleared.")
                    st.rerun()
                else:
                    st.error("Please enter task description")

    # TAB 3: Project Master
    with tab3:
        st.title("Project Master")
        st.subheader("Current Projects")
        for p in data["projects"]:
            st.write(f"• {p}")
        
        new_project = st.text_input("Add New Project")
        if st.button("Add Project"):
            if new_project.strip() and new_project not in data["projects"]:
                data["projects"].append(new_project.strip())
                save_data(data)
                st.success("Project added")
                st.rerun()

    # TAB 4: Engineer Master
    with tab4:
        st.title("Engineer Master")
        st.subheader("Current Engineers")
        for e in data["engineers"]:
            st.write(f"• {e}")
        
        new_engineer = st.text_input("Add New Engineer (Full Name)")
        if st.button("Add Engineer"):
            if new_engineer.strip() and new_engineer not in data["engineers"]:
                data["engineers"].append(new_engineer.strip())
                save_data(data)
                st.success("Engineer added")
                st.rerun()

# ===================== ENGINEER INTERFACE =====================
else:  # Engineer role
    st.title(f"👷 My Tasks - {current_date_str}")
    
    my_tasks = [t for t in tasks_today if t["assigned"] == st.session_state.full_name]
    
    if my_tasks:
        for task in my_tasks:
            with st.expander(f"{task['project']} - {task['description'][:60]}...", expanded=True):
                st.write(f"**Progress:** {task.get('progress', 0)}%")
                new_progress = st.slider("Update Progress", 0, 100, task.get("progress", 0), key=task["id"])
                new_notes = st.text_area("Brief Update Note (What you did today)", 
                                       value=task.get("notes", ""), key=f"note_{task['id']}")
                
                if st.button("Save Update", key=f"save_{task['id']}"):
                    for t in data["tasks"]:
                        if t["id"] == task["id"]:
                            t["progress"] = new_progress
                            t["notes"] = new_notes.strip()
                            t["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            break
                    save_data(data)
                    st.success("Updated successfully!")
                    st.rerun()
    else:
        st.info("You have no tasks assigned for this date.")

# ===================== FOOTER =====================
st.caption(f"DailyForge • Logged in as {st.session_state.full_name} • Data saved in daily_tasks.json")
