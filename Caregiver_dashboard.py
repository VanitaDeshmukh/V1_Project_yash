
import streamlit as st
import json
import os
import datetime

# ---------- Setup ----------
st.set_page_config(page_title="Caregiver Dashboard", layout="wide")
st.title("👤 Caregiver Dashboard")

# ---------- JSON Utilities ----------
def load_json(file):
    return json.load(open(file)) if os.path.exists(file) else []

def save_json(file, data):
    json.dump(data, open(file, "w"), indent=2)

def clean_skills(s):
    return [i.strip() for i in s.split(",")] if isinstance(s, str) else s

# ---------- Session & Role Check ----------
user = st.session_state.get("user", {})
if not user or user.get("role") != "Caregiver":
    st.warning("🚫 Only Caregivers can view this page.")
    st.stop()

# ---------- Load Data ----------
tasks = load_json("assigned_tasks.json")
assignments = load_json("assignments.json")
users = load_json("users.json")
chat = load_json("chat.json")

# ---------- Get Assigned Caretaker Info ----------
my_assignment = next(
    (a for a in assignments if a.get("caregiver") == user.get("username") and a.get("caretaker")), None
)
if not my_assignment:
    st.info("❌ You have not been assigned a caretaker yet.")
else:
    caretaker_username = my_assignment.get("caretaker")
    caretaker_user = None
    if caretaker_username:
        caretaker_user = next((u for u in users if u.get("username") == caretaker_username), None)

    if caretaker_user:
        caretaker_name = caretaker_user.get("name", caretaker_username)
        caretaker_contact = caretaker_user.get("contact", "Not Provided")
        caretaker_location = caretaker_user.get("location", "Unknown")
    else:
        caretaker_name = caretaker_username or "Unknown"
        caretaker_contact = "Not Provided"
        caretaker_location = "Unknown"

    # --- Display Assigned Caretaker Info ---
    st.subheader("🧑‍⚕️ Assigned Caretaker")
    st.markdown(f"- 👤 Name: **{caretaker_name}**")
    st.markdown(f"- 📞 Contact: **{caretaker_contact}**")
    st.markdown(f"- 📍 Location: **{caretaker_location}**")

    # --- View & Update Assigned Tasks ---
    st.subheader("📝 Your Assigned Tasks")

    my_tasks = [t for t in tasks if t.get("caregiver") == user.get("username")]
    if not my_tasks:
        st.info("You have no assigned tasks.")
    else:
        for t in my_tasks:
            st.markdown(f"""
            **🧾 Task:** {t.get('task', 'N/A')}  
            **⏰ Time:** {t.get('time', 'N/A')}  
            **📌 Status:** `{t.get('status', 'Pending')}`
            """)
            new_status = st.selectbox(
                "Update Status",
                ["Pending", "Completed", "Missed"],
                index=["Pending", "Completed", "Missed"].index(t.get("status", "Pending")),
                key=f"status_{t.get('task')}"
            )

            reason = ""
            if new_status == "Missed":
                reason = st.text_input("Reason for missing this task", key=f"reason_{t.get('task')}")

            if st.button("🔁 Update", key=f"update_{t.get('task')}"):
                for i in tasks:
                    if i == t:
                        i["status"] = new_status
                        i["reason"] = reason if new_status == "Missed" else ""
                        break
                save_json("assigned_tasks.json", tasks)
                st.success("✅ Task status updated.")
                st.rerun()


    # --- Chat with Caretaker (only assigned) ---
    st.subheader("💬 Chat with Your Caretaker")

    chat_history = [
        c for c in chat
        if (c.get("from") == user.get("username") and c.get("to") == caretaker_username)
        or (c.get("from") == caretaker_username and c.get("to") == user.get("username"))
    ]

    for c in chat_history:
        sender = "👤 You" if c.get("from") == user.get("username") else f"🧑‍⚕️ {caretaker_name}"
        # Style chat bubbles
        if sender == "👤 You":
            st.markdown(
                f"<div style='text-align: right; background-color: #DCF8C6; padding: 10px; margin: 5px; border-radius: 10px; max-width: 70%; margin-left: auto;'>"
                f"**{sender}:** {c.get('message', '')}</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='text-align: left; background-color: #F1F0F0; padding: 10px; margin: 5px; border-radius: 10px; max-width: 70%; margin-right: auto;'>"
                f"**{sender}:** {c.get('message', '')}</div>", unsafe_allow_html=True)

    # Chat input and send button
    new_msg = st.text_input("Write a message to your Caretaker", key="new_chat_message")
    if st.button("Send Message") and new_msg.strip():
        chat.append({
            "from": user.get("username"),
            "to": caretaker_username,
            "message": new_msg.strip(),
            "timestamp": datetime.datetime.now().isoformat()
            
        })
        save_json("chat.json", chat)
        st.rerun()


# --- Navigation buttons (always visible) ---
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🏠 Back to Home"):
        st.switch_page("home.py")

with col2:
    if st.button("🔓 Logout"):
        for key in ["user", "logged_in", "preferred_role"]:
            if key in st.session_state:
                del st.session_state[key]
        st.switch_page("home.py")
