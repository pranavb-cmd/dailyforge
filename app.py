import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# ===================== CONFIG =====================
DATA_FILE = "daily_tasks.json"
ENGINEERS = ["Alice Sharma", "Rahul Verma", "Priya Patel", "Arjun Rao", "Neha Gupta", "Vikram Singh"]

st.set_page_config(page_title="DailyForge", page_icon="🔥", layout="wide")

# ===================== LOAD / SAVE DATA =====================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"tasks": []}
    return {"tasks": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

data = load_data()

# ===================== SIDEBAR =====================
st.sidebar.image("https://img.icons8.com/fluency/96/000000/fire.png", width=80)
st.sidebar.title("🔥 DailyForge")
st.sidebar.markdown("**Project Task Dashboard**")

current_date = st.sidebar.date_input("Select Date", datetime.now().date())
current_date_str = current_date.strftime("%Y-%m-%d")

role = st.sidebar.radio("Your Role", ["Manager", "Engineer"])

st.sidebar.markdown("---")
st.sidebar.caption("Data is saved automatically in JSON file")

# ===================== FILTER TASKS =====================
def get_filtered_tasks():
    return [t for t in data.get("tasks", []) if t["date"] == current_date_str]

tasks_today = get_filtered_tasks()

# ===================== MAIN DASHBOARD =====================
st.title(f"DailyForge Dashboard - {current_date_str}")

# Stats
col1, col2, col3, col4 = st.columns(4)

total = len(tasks_today)
completed = sum(1 for t in tasks_today if t.get("progress", 0) == 100)
in_progress = sum(1 for t in tasks_today if 0 < t.get("progress", 0) < 100)
avg_progress = sum(t.get("progress", 0) for t in tasks_today) // total if total > 0 else 0

col1.metric("Total Tasks", total)
col2.metric("Completed", completed, f"{round((completed/total)*100) if total else 0}%")
col3.metric("In Progress", in_progress)
col4.metric("Overall Progress", f"{avg_progress}%")

# Add New Task (Manager only)
if role == "Manager":
    with st.expander("➕ Add New Daily Target", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            project = st.text_input("Project Name")
            description = st.text_area("Task Description")
        with col_b:
            assigned = st.selectbox("Assign to Engineer", ENGINEERS)
            target = st.number_input("Target Progress (%)", min_value=0, max_value=100, value=100)

        if st.button("Add Task Target"):
            if project and description and assigned:
                new_task = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "date": current_date_str,
                    "project": project,
                    "description": description,
                    "assigned": assigned,
                    "progress": 0,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                data.setdefault("tasks", []).append(new_task)
                save_data(data)
                st.success("Task added successfully!")
                st.rerun()
            else:
                st.error("Please fill all fields")

# Tasks Table
st.subheader("Today's Tasks")

if tasks_today:
    df = pd.DataFrame(tasks_today)
    df["Progress"] = df["progress"].apply(lambda x: f"{x}%")
    df["Status"] = df["progress"].apply(lambda x: "✅ Completed" if x == 100 else "🔄 In Progress" if x > 0 else "⏳ Pending")
    df = df[["project", "description", "assigned", "Progress", "Status", "last_updated"]]
    df.columns = ["Project", "Task", "Engineer", "Progress", "Status", "Last Updated"]

    st.dataframe(df, use_container_width=True, hide_index=True)

    # Update Task Section
    st.subheader("Update Task Progress")
    task_to_update = st.selectbox("Select Task to Update", 
                                  options=[f"{t['project']} - {t['description'][:50]}" for t in tasks_today],
                                  key="update_select")

    selected_task = next((t for t in tasks_today if f"{t['project']} - {t['description'][:50]}" == task_to_update), None)

    if selected_task:
        new_progress = st.slider("Update Progress (%)", 0, 100, selected_task.get("progress", 0))
        if st.button("Save Progress Update"):
            for t in data["tasks"]:
                if t["id"] == selected_task["id"]:
                    t["progress"] = new_progress
                    t["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    break
            save_data(data)
            st.success("Progress updated!")
            st.rerun()
else:
    st.info("No tasks found for this date. Add some using the expander above (Manager).")

# Team Performance
st.subheader("Team Performance")
for eng in ENGINEERS:
    eng_tasks = [t for t in tasks_today if t.get("assigned") == eng]
    if eng_tasks:
        avg = sum(t.get("progress", 0) for t in eng_tasks) // len(eng_tasks)
        done = sum(1 for t in eng_tasks if t.get("progress", 0) == 100)
        st.progress(avg / 100, text=f"{eng}: {avg}%  |  {done}/{len(eng_tasks)} completed")

# Footer
st.caption("DailyForge • Built with Streamlit • Data stored in daily_tasks.json")