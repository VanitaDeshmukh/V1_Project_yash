
import streamlit as st

st.set_page_config(page_title="Senior Hygiene Caretaker", layout="wide")

if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

header_cols = st.columns([8, 40, 6])

with header_cols[0]:
    st.image("assets/logo..png", width=150)

with header_cols[1]:
    st.markdown(
        """
        <div style="text-align: center; line-height: 1.2;">
            <h2 style="color: #007BFF; margin-bottom: 0; font-size: 36px;">
                👵🛁 Senior Hygiene Caretaker
            </h2>
            <p style="font-size: 15px; margin-top: 4px; color: black;">
                Your trusted partner for hygiene, dignity,<br> and coordinated elder care at home.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.image("assets/banner3.jpg", use_container_width=True)

with header_cols[2]:
    if st.button("🔐 Login"):
        st.switch_page("pages/Login.py")

st.markdown("---")

# Compassion message
st.markdown("<h3 style='color:#007BFF; font-size:20px;'>💙 Care with Compassion for Our Elderly</h3>", unsafe_allow_html=True)

st.write("""
We believe care isn't just a task — it's a bond. Every bath, reminder, or smile fosters dignity and connection. With simple tools and genuine heart, we restore joy and hygiene for those who shaped our lives.
""")


# Why Choose Us section
st.subheader("🌟 Why Choose Us?")
st.write("""
- 🧼 Trusted daily hygiene management  
- 👩‍⚕️ Verified caregivers with skill and empathy  
- 📊 Smart contracts and payment tracking   
- 📅 Flexible care periods and options  
""")

# Services Offered section
st.markdown("### 🧰 Types of Services We Offer for Elderly Care")

row1 = st.columns(3)
with row1[0]:
    st.markdown("#### 🛁 Bathing Assistance")
    st.write("Gentle support with privacy and dignity.")
with row1[1]:
    st.markdown("#### 💇 Grooming Help")
    st.write("Hair care, nail trimming, and neat presentation.")
with row1[2]:
    st.markdown("#### 🦷 Oral Hygiene")
    st.write("Regular dental routines and comfort checks.")

row2 = st.columns(3)
with row2[0]:
    st.markdown("#### 💊 Medication Reminders")
    st.write("Timely reminders and care tracking.")
with row2[1]:
    st.markdown("#### 🛏️ Bed Hygiene")
    st.write("Support with cleanliness and comfort.")
with row2[2]:
    st.markdown("#### 🧼 Dressing & Mobility")
    st.write("Gentle aid with clothing and movement.")

