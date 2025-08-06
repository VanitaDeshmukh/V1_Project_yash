

import streamlit as st
import json
import os
import re

st.set_page_config(page_title="Caregiver Registration", layout="centered")

file_path = "users.json"


# ---------- Utility functions ----------
def load_users():
    return json.load(open(file_path)) if os.path.exists(file_path) else []


def save_users(data):
    json.dump(data, open(file_path, "w"), indent=4)


def is_valid_password(password):
    """Check password: min 8 chars, 1 uppercase, 1 lowercase, and 1 digit"""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


def clean_digits(text):
    return "".join(filter(str.isdigit, text))


def format_phone_number(digits):
    cleaned = digits[:10]  # limit to 10 digits max
    length = len(cleaned)
    if length <= 3:
        return cleaned
    elif length <= 6:
        return f"{cleaned[:3]} {cleaned[3:]}"
    else:
        return f"{cleaned[:3]} {cleaned[3:6]} {cleaned[6:]}"

# ---------- Initialize session state ----------
if "contact_input" not in st.session_state:
    st.session_state["contact_input"] = ""

# ---------- Page Title ----------
st.markdown("<h1 style='text-align:center; color:#2E86C1;'>📝 Caregiver Registration</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---------- Registration Form ----------
with st.form(key="registration_form"):
    left_col, right_col = st.columns(2)

    with left_col:
        username = st.text_input("🧑 Username", max_chars=20, placeholder="Create a unique username")
        password = st.text_input("🔒 Password", type="password",
                                 placeholder="Min 8 chars, uppercase, lowercase & digit")
        location = st.text_input("📍 Location", max_chars=50, placeholder="Your city or area")

    with right_col:
        name = st.text_input("📛 Full Name", max_chars=50)

        contact_raw = st.text_input(
            "📞 Contact Number (10 digits)",
            value=st.session_state["contact_input"],
            max_chars=15,
            placeholder="Enter 10-digit number"
        )
        cleaned_contact = clean_digits(contact_raw)
        formatted_contact = format_phone_number(cleaned_contact)

        if formatted_contact != contact_raw:
            st.session_state["contact_input"] = formatted_contact

        # Skills multiselect
        skill_options = [
            "Bathing", "Feeding", "Cleaning", "Toilet Cleaning",
            "Hair Cutting", "Medication Reminders", "Dressing Support", "Mobility Assistance"
        ]
        selected_skills = st.multiselect("✅ Select Your Skills", options=skill_options)

    submitted = st.form_submit_button("✅ Register")

# ---------- Form Submission Logic ----------
if submitted:
    users = load_users()
    errors = []

    # Username uniqueness check
    if any(u["username"] == username for u in users):
        errors.append("🚫 Username already exists.")

    # Required fields
    if not username or not password or not name or not cleaned_contact or not selected_skills:
        errors.append("⚠️ Please fill in all required fields and select at least one skill.")

    # Password complexity
    if password and not is_valid_password(password):
        errors.append(
            "⚠️ Password must be at least 8 characters long and include at least "
            "1 uppercase letter, 1 lowercase letter, and 1 digit."
        )

    # Contact number validations
    if cleaned_contact != clean_digits(contact_raw):
        errors.append("⚠️ Contact number should contain digits only. Non-digit characters were removed automatically.")

    if len(cleaned_contact) != 10:
        errors.append("⚠️ Contact number must be exactly 10 digits.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        skills_str = ", ".join(selected_skills)
        users.append({
            "username": username,
            "password": password,
            "role": "Caregiver",
            "location": location,
            "contact": cleaned_contact,
            "skills": skills_str,
            "name": name
        })
        save_users(users)
        st.success("✅ Caregiver registered successfully! Redirecting to login...")
        st.session_state["preferred_role"] = "Caregiver"
        st.switch_page("pages/Login.py")  # Redirect immediately

# ---------- Navigation ----------
st.markdown("---")
if st.button("🏠 Back to Home"):
    st.switch_page("home.py")
