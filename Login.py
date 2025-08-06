import streamlit as st
import json
import os

# ----- Setup -----
st.set_page_config(page_title="Login Portal", layout="centered")

st.markdown(
    "<h1 style='text-align:center; color:#2E86C1; margin-bottom: 0.5em;'>🔐 Login Portal</h1>", 
    unsafe_allow_html=True
)

file_path = "users.json"

def load_users():
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

# ----- Role Selection -----
default_role = st.session_state.get("preferred_role", "Caretaker")
role = st.radio(
    "Select your role:",
    ["Caretaker", "Caregiver"],
    index=["Caretaker", "Caregiver"].index(default_role),
    horizontal=True,
    key="role_radio"
)
st.session_state["preferred_role"] = role  # Persist selection

st.markdown("---")

# ----- Login Inputs -----
with st.form(key="login_form"):
    st.write("### Login Credentials")

    username = st.text_input("🧑 Username", max_chars=30, placeholder="Enter your username")
    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")

    st.markdown("")

    login_btn = st.form_submit_button("Login")

if login_btn:
    users = load_users()
    matched = next(
        (user
            for user in users
            if user["username"] == username and user["password"] == password and user["role"] == role
        ),
        None,
    )

    if matched:
        st.success(f"✅ Welcome back, {matched.get('name', matched['username'])}!")
        st.session_state["user"] = matched
        st.session_state["logged_in"] = True

        # Clear query parameters before switching page
        st.query_params.clear()

        # Redirect to dashboard based on role
        if role == "Caretaker":
            st.switch_page("pages/Caretaker_dashboard.py")
        else:
            st.switch_page("pages/Caregiver_dashboard.py")

    else:
        st.error("❌ Invalid credentials or role mismatch.")

st.markdown("---")

# ----- Registration Prompt -----
st.write(f"### Not registered as a {role}?")
if st.button("📝 Register Here"):
    st.session_state["preferred_role"] = role  # Pass role to registration
    if role == "Caretaker":
        st.switch_page("pages/CaretakerRegister.py")
    else:
        st.switch_page("pages/CaregiverRegister.py")

st.markdown("---")

# ----- Back to Home Button -----
if st.button("🏠 Back to Home"):
    st.switch_page("home.py")