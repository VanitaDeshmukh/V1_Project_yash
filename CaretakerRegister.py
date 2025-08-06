import streamlit as st
import json
import os
import re

st.set_page_config(page_title="Caretaker Registration", layout="centered")

# ---------- Utility functions ----------
file_path = "users.json"

def load_users():
    return json.load(open(file_path)) if os.path.exists(file_path) else []

def save_users(data):
    json.dump(data, open(file_path, "w"), indent=4)

def is_valid_password(password):
    """Check password for length and character requirements."""
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
    cleaned = digits[:10]  # max 10 digits only
    length = len(cleaned)
    if length <= 3:
        return cleaned
    elif length <= 6:
        return f"{cleaned[:3]} {cleaned[3:]}"
    else:
        return f"{cleaned[:3]} {cleaned[3:6]} {cleaned[6:]}"


# ---------- Initialize session state for contact input ----------
if "contact_input" not in st.session_state:
    st.session_state["contact_input"] = ""


# ---------- Page Title ----------
st.markdown("<h1 style='text-align:center; color:#2E86C1;'>📝 Caretaker Registration</h1>", unsafe_allow_html=True)
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
        age = st.number_input("🎂 Age", min_value=18, max_value=120, help="Must be 18 or older")

        # Controlled contact input with live formatting
        contact_raw = st.text_input(
            "📞 Contact Number (10 digits)",
            value=st.session_state["contact_input"],
            max_chars=15,
            placeholder="Enter 10-digit number"
        )

        # Clean and format contact number
        cleaned_contact = clean_digits(contact_raw)
        formatted_contact = format_phone_number(cleaned_contact)

        # Update session state to maintain formatted input in the textbox
        if formatted_contact != contact_raw:
            st.session_state["contact_input"] = formatted_contact

        # Optional: Live validation if desired (comment this if you want warnings only on submit)
        if cleaned_contact and len(cleaned_contact) != 10:
            st.error("⚠️ Contact number must be exactly 10 digits.")

    submitted = st.form_submit_button("✅ Register")


# ---------- Form Submission Logic ----------
if submitted:
    users = load_users()
    errors = []

    # Username must be unique
    if any(u["username"] == username for u in users):
        errors.append("🚫 Username already exists.")

    # Check that all required fields are filled
    if not username or not password or not name or not cleaned_contact:
        errors.append("⚠️ Please fill in all required fields.")

    # Password complexity
    if password and not is_valid_password(password):
        errors.append(
            "⚠️ Password must be at least 8 characters long and include at least "
            "1 uppercase letter, 1 lowercase letter, and 1 digit."
        )

    # Check for non-digit characters in user input (only after submit)
    if cleaned_contact != clean_digits(contact_raw):
        errors.append(
            "⚠️ Contact number should contain digits only. Non-digit characters were removed automatically."
        )

    # Contact length check
    if len(cleaned_contact) != 10:
        errors.append("⚠️ Contact number must be exactly 10 digits.")

    # Show all errors if any
    if errors:
        for err in errors:
            st.error(err)
    else:
        # Save new user
        users.append({
            "username": username,
            "password": password,
            "contact": cleaned_contact,
            "role": "Caretaker",
            "location": location,
            "skills": "",
            "name": name,
            "age": age
        })
        save_users(users)
        st.success("✅ Registration successful! Redirecting to login...")
        st.session_state["preferred_role"] = "Caretaker"
        st.switch_page("pages/Login.py")  # Redirect immediately


# ---------- Navigation button ----------
st.markdown("---")
if st.button("🏠 Back to Home"):
    st.switch_page("home.py")

