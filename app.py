import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

DATA_FILE = "daily_tasks.json"

st.set_page_config(page_title="DailyForge", page_icon="🔥", layout="wide")

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
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
            if username in data["users"]["manager"] and data["users"]["manager"][username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = "manager"
                st.session_state.full_name = data["users"]["manager"][username]["name"]
                st.rerun()
            elif username in data["users"]["engineer"] and data["users"]["engineer"][username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = "engineer"
                st.session_state.full_name = data["users"]["engineer"][username]["name"]
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.caption("Manager: pranav / manager123")
    st.stop()

# ===================== MAIN APP =====================
st.sidebar.image("https://img.icons8.com/fluency/96/fire.png", width=70)
st.sidebar.title("DailyForge")
st.sidebar.markdown(f"**{st.session_state.full_name}** ({st.session_state.role.upper()})")

current_date = st.sidebar.date_input("Select Date", datetime.now().date())
current_date_str = current_date.strftime("%Y-%m-%d")

if st.sidebar.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

active_projects = [p["name"] for p in data["projects"] if p.get("active", True)]

if st.session_state.role == "manager":
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "➕ Add Task", "📋 Project Master", "👷 Engineer Master", "🔑 Change Password"])

    with tab1:
        st.title(f"Dashboard - {current_date_str}")
        tasks_today = [t for t in data.get("tasks", []) if t.get("date") == current_date_str]
        total = len(tasks_today)
        completed = sum(1 for t in tasks_today if t.get("progress", 0) == 100)
        avg = sum(t.get("progress", 0) for t in tasks_today) // total if total else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Tasks", total)
        c2.metric("Completed", completed)
        c3.metric("In Progress", total - completed)
        c4.metric("Overall Progress", f"{avg}%")

        if tasks_today:
            df = pd.DataFrame(tasks_today)
            df["Progress"] = df["progress"].apply(lambda x: f"{x}%")
            df["Status"] = df["progress"].apply(lambda x: "✅ Completed" if x == 100 else "🔄 In Progress" if x > 0 else "⏳ Pending")
            st.dataframe(df[["project", "description", "assigned", "Progress", "Status", "last_updated", "notes"]], 
                        use_container_width=True, hide_index=True)

    with tab2:
        st.title("Add New Task Target")
        with st.form("add_task_form", clear_on_submit=True):
            project = st.selectbox("Project", active_projects if active_projects else ["No active projects"])
            description = st.text_area("Task Description")
            assigned = st.selectbox("Assign to Engineer", data["engineers"])
            
            if st.form_submit_button("✅ Add Task Target"):
                if description.strip() and active_projects:
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
                    st.success("Task added successfully!")
                    st.rerun()

    with tab3:  # Project Master (unchanged)
        st.title("Project Master")
        st.subheader("All Projects")
        for i, proj in enumerate(data["projects"]):
            col1, col2, col3 = st.columns([3, 1.5, 1])
            status = "🟢 Active" if proj.get("active", True) else "🔴 Ended"
            col1.write(f"**{proj['name']}** — {status}")

            if col2.button("Mark as Ended", key=f"end_proj_{i}"):
                data["projects"][i]["active"] = False
                save_data(data)
                st.success(f"{proj['name']} marked as Ended")
                st.rerun()

            if col3.button("🗑️ Delete", key=f"del_btn_proj_{i}"):
                st.session_state[f"confirm_delete_proj_{i}"] = True
                st.rerun()

            if st.session_state.get(f"confirm_delete_proj_{i}", False):
                st.warning(f"Are you sure you want to permanently delete '{proj['name']}'?")
                col_yes, col_no = st.columns(2)
                if col_yes.button("✅ Yes, Delete Permanently", key=f"yes_del_proj_{i}"):
                    del data["projects"][i]
                    save_data(data)
                    st.success("Project deleted!")
                    del st.session_state[f"confirm_delete_proj_{i}"]
                    st.rerun()
                if col_no.button("Cancel", key=f"cancel_del_proj_{i}"):
                    del st.session_state[f"confirm_delete_proj_{i}"]
                    st.rerun()

        new_project = st.text_input("Add New Project")
        if st.button("Add Project"):
            if new_project.strip():
                data["projects"].append({"name": new_project.strip(), "active": True})
                save_data(data)
                st.success("Project added")
                st.rerun()

    # ==================== IMPROVED ENGINEER MASTER ====================
    with tab4:
        st.title("👷 Engineer Master")
        st.subheader("Current Engineers")

        for i, eng in enumerate(data["engineers"]):
            col1, col2 = st.columns([4, 1])
            col1.write(f"• {eng}")
            if col2.button("🗑️ Delete", key=f"del_btn_eng_{i}"):
                st.session_state[f"confirm_delete_eng_{i}"] = True
                st.rerun()

            if st.session_state.get(f"confirm_delete_eng_{i}", False):
                st.warning(f"Are you sure you want to permanently delete '{eng}'?")
                col_yes, col_no = st.columns(2)
                if col_yes.button("✅ Yes, Delete", key=f"yes_del_eng_{i}"):
                    # Also remove from users if exists
                    for uname, info in list(data["users"]["engineer"].items()):
                        if info["name"] == eng:
                            del data["users"]["engineer"][uname]
                            break
                    del data["engineers"][i]
                    save_data(data)
                    st.success("Engineer deleted!")
                    del st.session_state[f"confirm_delete_eng_{i}"]
                    st.rerun()
                if col_no.button("Cancel", key=f"cancel_del_eng_{i}"):
                    del st.session_state[f"confirm_delete_eng_{i}"]
                    st.rerun()

        st.subheader("Add New Engineer")
        with st.form("add_engineer_form", clear_on_submit=True):
            full_name = st.text_input("Full Name (e.g. Sneha Patil)")
            username = st.text_input("Login Username (e.g. sneha - lowercase recommended)")
            default_password = st.text_input("Default Password", value="123456", type="password")
            
            if st.form_submit_button("✅ Add Engineer"):
                if full_name.strip() and username.strip():
                    username = username.lower().strip()
                    if username in data["users"]["engineer"]:
                        st.error("This username already exists!")
                    elif full_name in data["engineers"]:
                        st.error("This engineer name already exists!")
                    else:
                        # Add to engineers list
                        data["engineers"].append(full_name.strip())
                        # Create login
                        data["users"]["engineer"][username] = {
                            "password": default_password,
                            "role": "engineer",
                            "name": full_name.strip()
                        }
                        save_data(data)
                        st.success(f"Engineer **{full_name}** added successfully!\n\nUsername: **{username}**\nDefault Password: **{default_password}**")
                        st.rerun()
                else:
                    st.error("Full Name and Username are required")

    with tab5:
        st.title("Change Password")
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm New Password", type="password")
        if st.button("Update Password"):
            if new_pass == confirm_pass and new_pass:
                if st.session_state.role == "manager":
                    data["users"]["manager"][st.session_state.username]["password"] = new_pass
                else:
                    data["users"]["engineer"][st.session_state.username]["password"] = new_pass
                save_data(data)
                st.success("Password changed successfully!")
            else:
                st.error("Passwords do not match")

else:  # Engineer View
    st.title(f"👷 My Tasks - {current_date_str}")
    my_tasks = [t for t in data.get("tasks", []) if t.get("date") == current_date_str and t.get("assigned") == st.session_state.full_name]
    
    if my_tasks:
        for task in my_tasks:
            with st.expander(f"{task['project']} — {task['description'][:60]}...", expanded=False):
                new_progress = st.slider("Progress (%)", 0, 100, task.get("progress", 0), key=f"prog_{task['id']}")
                new_notes = st.text_area("Brief Update Note", value=task.get("notes", ""), key=f"note_{task['id']}")
                
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
        st.info("No tasks assigned to you on this date.")

st.caption("DailyForge • New engineers now get login credentials automatically")
