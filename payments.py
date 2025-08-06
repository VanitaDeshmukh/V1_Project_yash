import streamlit as st
import json
import os
from datetime import datetime

st.title("💸 Payment Records")


def load_json(file):
    return json.load(open(file)) if os.path.exists(file) else []


# User session: assuming caretaker/caregiver login logic already handled and sets st.session_state["user"]
user = st.session_state.get("user")

if not user or not isinstance(user, dict) or user.get("role") not in ["Caretaker", "Caregiver"]:
    st.warning("🚫 Only Caretakers and Caregivers allowed here.")
    st.stop()

payments = load_json("payments.json")

# Filter payments based on user role
if user["role"] == "Caretaker":
    filtered_payments = [p for p in payments if p.get("caretaker") == user["username"]]
elif user["role"] == "Caregiver":
    filtered_payments = [p for p in payments if p.get("caregiver") == user["username"]]
else:
    filtered_payments = []

if not filtered_payments:
    st.info("No payments recorded yet.")
else:
    # Show payments in reverse chronological order (latest first)
    for p in reversed(filtered_payments):
        with st.expander(f"👤 {p['caregiver_name']} | ₹{p['total_fee']} | {p['start_date']} to {p['end_date']}"):
            st.markdown(f"- **Skills:** {', '.join(p['skills'])}")
            st.markdown(f"- **Total Days:** {p['total_days']}")
            st.markdown(f"- **Daily Fee:** ₹{p['daily_fee']}")
            st.markdown(f"- **Total Fee:** ₹{p['total_fee']}")
            st.markdown(f"- **Saved At:** {p['timestamp']}")

    # Optional: Show as a simple table without pandas
    st.subheader("All Payments (Table View)")

    # Prepare table data for st.table (list of lists or list of dicts)
    table_data = []
    headers = ["Caregiver", "Caretaker", "Skills", "Start Date", "End Date", "Total Days", "Daily Fee", "Total Fee", "Saved At"]

    for p in filtered_payments:
        row = [
            p.get("caregiver_name", p.get("caregiver", "")),
            p.get("caretaker", ""),
            ", ".join(p.get("skills", [])),
            p.get("start_date", ""),
            p.get("end_date", ""),
            p.get("total_days", ""),
            f"₹{p.get('daily_fee', '')}",
            f"₹{p.get('total_fee', '')}",
            p.get("timestamp", "")
        ]
        table_data.append(row)

    st.table([headers] + table_data)

st.markdown("---")
if st.button("🏠 Back to Home"):
    st.switch_page("home.py")
