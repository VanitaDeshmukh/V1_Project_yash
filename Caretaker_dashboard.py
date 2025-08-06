import streamlit as st
import json
import os
import datetime

# ---------- Setup ----------
st.set_page_config(page_title="Caretaker Dashboard", layout="wide")
st.title("🧑‍⚕️ Caretaker Dashboard")

# ---------- JSON Utilities ----------
def load_json(file):
    return json.load(open(file)) if os.path.exists(file) else []

def save_json(file, data):
    json.dump(data, open(file, "w"), indent=2)

def clean_skills(s):
    return [i.strip() for i in s.split(",")] if isinstance(s, str) else s


# ---------- User Check ----------
user = st.session_state.get("user")
if not user or not isinstance(user, dict) or user.get("role") != "Caretaker":
    st.warning("🚫 Only Caretakers allowed here.")
    st.stop()

# ---------- Load Data ----------
users = load_json("users.json")
caregivers = [u for u in users if u.get("role") == "Caregiver"]
assignments = load_json("assignments.json")
tasks = load_json("assigned_tasks.json")
chat = load_json("chat.json")
payments = load_json("payments.json")


# ---------- Skill Fees ----------
skill_fees = {
    "Bathing": 100,
    "Feeding": 80,
    "Cleaning": 90,
    "Toilet Cleaning": 110,
    "Hair Cutting": 120,
    "Medication Reminders": 95,
    "Dressing Support": 85,
    "Mobility Assistance": 130
}


# ---------- Assign Caregiver ----------
st.subheader("📌 Assign a Caregiver")

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    location_filter = st.selectbox(
        "📍 Filter by Location",
        ["Any"] + sorted({c.get("location", "") for c in caregivers if c.get("location")})
    )
with filter_col2:
    all_skills = {skill for cg in caregivers for skill in clean_skills(cg.get("skills", []))}
    required_skills = st.multiselect("🛠 Required Skills", sorted(all_skills))


matched = []
for cg in caregivers:
    cg_skills = clean_skills(cg.get("skills", []))
    if all(skill in cg_skills for skill in required_skills):
        if location_filter == "Any" or cg.get("location") == location_filter:
            matched.append(cg)


if not matched:
    st.info("No caregiver matches the selected filters.")
else:
    for cg in matched:
        with st.expander(f"👤 {cg['username']} ({', '.join(cg_skills[:3])}{'...' if len(cg_skills) > 3 else ''})"):
            st.markdown(f"- 📍 Location: **{cg.get('location', 'N/A')}**")
            st.markdown(f"- 📞 Contact: **{cg.get('contact', 'N/A')}**")
            st.markdown(f"- 🔧 Skills: {', '.join(cg_skills)}")

            with st.form(key=f"assign_form_{cg['username']}"):
                duration = st.selectbox("🕒 Duration", ["15 Days", "1 Month", "3 Months"], key=f"duration_{cg['username']}")
                joining_date = st.date_input(
                    "📅 Joining Date",
                    value=datetime.datetime.today().date(),
                    key=f"join_{cg['username']}"
                )
                submitted = st.form_submit_button(f"✅ Assign {cg['username']}")

                if submitted:
                    duration_days_map = {
                        "15 Days": 15,
                        "1 Month": 30,
                        "3 Months": 90
                    }
                    ending_date = joining_date + datetime.timedelta(days=duration_days_map.get(duration, 0))
                    assignments.append({
                        "caretaker": user["username"],
                        "caregiver": cg["username"],
                        "contact": cg.get("contact", ""),
                        "duration": duration,
                        "status": "Active",
                        "joining_date": joining_date.isoformat(),
                        "ending_date": ending_date.isoformat()
                    })
                    save_json("assignments.json", assignments)
                    st.success(f"✅ Assigned {cg['username']} successfully!")
                    st.rerun()


# ---------- Manage Caregivers ----------
st.subheader("📝 Manage Caregivers")
assigned = [a for a in assignments if a.get("caretaker") == user["username"]]

if not assigned:
    st.info("No caregivers assigned yet.")
else:
    for i, a in enumerate(assigned):
        cg_data = next((u for u in users if u["username"] == a["caregiver"]), None)
        if not cg_data:
            continue
        with st.expander(f"👤 {cg_data['username']} - {cg_data.get('name', '')}"):
            st.markdown(f"- 📞 Contact: **{cg_data.get('contact', 'N/A')}**")
            skills = clean_skills(cg_data.get("skills", []))
            st.markdown(f"- 🔧 Skills: {', '.join(skills)}")

            st.markdown("### ➕ Assign Tasks")
            with st.form(key=f"assign_task_form_{cg_data['username']}_{i}"):
                if skills:
                    selected_skill = st.selectbox("Task: Select Skill", skills, key=f"skill_{cg_data['username']}_{i}_task")
                else:
                    st.info("No skills available for this caregiver.")
                    selected_skill = None
                task_time = st.time_input("Schedule Time", key=f"time_{cg_data['username']}_{i}_task")
                task_submitted = st.form_submit_button("Assign")

                if task_submitted and selected_skill:
                    tasks.append({
                        "caretaker": user["username"],
                        "caregiver": cg_data["username"],
                        "task": selected_skill,
                        "skill": selected_skill,
                        "time": task_time.strftime("%I:%M %p"),
                        "status": "Pending",
                        "reason": "",
                        "created_at": datetime.datetime.now().isoformat()
                    })
                    save_json("assigned_tasks.json", tasks)
                    st.success("✅ Task assigned successfully.")
                    st.rerun()

            st.markdown("### 📋 Current Task Status")
            cg_tasks = [t for t in tasks if t["caregiver"] == cg_data["username"]]
            if not cg_tasks:
                st.info("No tasks yet.")
            else:
                for t in cg_tasks:
                    reason_text = f"**💬 Reason:** {t['reason']}" if t['status'] == "Missed" else ""
                    st.markdown(f"""
                        **🧾 Task:** {t['task']}  
                        **⏲ Time:** {t['time']}  
                        **📌 Status:** `{t['status']}`  
                        {reason_text}
                    """)

# ---------- Chat Interface ----------
st.subheader("💬 Chat with Caregiver")

active_caregivers = sorted(set(a["caregiver"] for a in assigned))
options = ["-- Select a Caregiver --"] + active_caregivers

selected_chat_user = st.selectbox("Select Caregiver", options, key="chat_selectbox")

if selected_chat_user != "-- Select a Caregiver --":
    chat_history = [
        c for c in chat
        if (c.get("from") == user["username"] and c.get("to") == selected_chat_user)
        or (c.get("from") == selected_chat_user and c.get("to") == user["username"])
    ]

    for c in chat_history:
        if c["from"] == user["username"]:
            st.markdown(
                f"<div style='text-align: right; background-color: #DCF8C6; margin: 5px; padding:10px; border-radius:10px;'>**You:** {c['message']}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='text-align: left; background-color: #F1F0F0; margin: 5px; padding:10px; border-radius:10px;'>**{c['from']}:** {c['message']}</div>",
                unsafe_allow_html=True,
            )

    new_msg = st.text_input("Write a message", key="chat_input")
    if st.button("Send", key="chat_send") and new_msg.strip():
        chat.append({
            "from": user["username"],
            "to": selected_chat_user,
            "message": new_msg.strip(),
            "timestamp": datetime.datetime.now().isoformat()
        })
        save_json("chat.json", chat)
        st.rerun()
else:
    st.info("Please select a caregiver to start chatting.")


# ---------- Caretaker Skill Payment Calculator ----------
st.title("🧑‍⚕️ Caregiver Payment Calculator")


def load_json_safe(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return []

users = load_json_safe("users.json")
assignments = load_json_safe("assignments.json")

current_user = user["username"]

assigned = [a for a in assignments if a.get("caretaker") == current_user]
cg_usernames = [a["caregiver"] for a in assigned]

cg_names = {u["username"]: u.get("name", u["username"]) for u in users if u["username"] in cg_usernames}
cg_options = {cg_names[u]: u for u in cg_usernames if u in cg_names}

if not cg_options:
    st.info("No caregivers assigned to you yet.")
    st.stop()

selected_name = st.selectbox("Select Caregiver", options=list(cg_options.keys()))
selected_cg = cg_options.get(selected_name)

joining_str = next(
    (a.get("joining_date") for a in assigned if a.get("caregiver") == selected_cg),
    datetime.date.today().isoformat()
)

try:
    start_date = datetime.date.fromisoformat(joining_str)
except Exception:
    start_date = datetime.date.today()

st.markdown(f"📅 **Joining Date:** {start_date}")

end_date = st.date_input("Select End Date", value=start_date + datetime.timedelta(days=1))

if end_date < start_date:
    st.error("End Date cannot be earlier than Joining Date.")
    st.stop()

total_days = max((end_date - start_date).days, 1)

skill_fees = {
    "Bathing": 100,
    "Feeding": 80,
    "Cleaning": 90,
    "Toilet Cleaning": 110,
    "Hair Cutting": 120,
    "Medication Reminders": 95,
    "Dressing Support": 85,
    "Mobility Assistance": 130
}

selected_skills = st.multiselect("Select Skills", options=list(skill_fees.keys()))

fee_breakdown = {skill: skill_fees[skill] for skill in selected_skills}
per_day_fee = sum(fee_breakdown.values())
total_fees = per_day_fee * total_days

if selected_skills:
    st.subheader("📊 Skill Fee Breakdown (Per Day)")
    for skill, fee in fee_breakdown.items():
        st.markdown(f"- **{skill}: ₹{fee}**")

    st.markdown(f"👤 **Caregiver:** {selected_name}")
    st.markdown(f"📅 **Total Duration:** {total_days} days")
    st.markdown(f"💰 **Total Fee:** ₹{total_fees:.2f}")
else:
    st.info("Select at least one skill to see the fee details.")

# Save payment record
if st.button("💾 Save Payment Record", key=f"save_payment_{selected_cg}"):
    payment_entry = {
        "caretaker": current_user,
        "caregiver": selected_cg,
        "caregiver_name": selected_name,
        "skills": selected_skills,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_days": total_days,
        "daily_fee": per_day_fee,
        "total_fee": total_fees,
        "timestamp": datetime.datetime.now().isoformat()
    }
    try:
        if os.path.exists("payments.json"):
            with open("payments.json", "r") as f:
                payments = json.load(f)
        else:
            payments = []

        payments.append(payment_entry)

        with open("payments.json", "w") as f:
            json.dump(payments, f, indent=2)

        st.success("✅ Payment record saved successfully!")
    except Exception as e:
        st.error(f"Error saving payment record: {e}")

# ---------- Navigation ----------
st.markdown("---")
if st.button("🏠 Back to Home"):
    st.switch_page("home")

if st.button("🔓 Logout"):
    for key in ["user", "logged_in", "preferred_role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.switch_page("home.py")
