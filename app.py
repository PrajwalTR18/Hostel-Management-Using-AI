"""
Advanced AI-Based Hostel Management System - Streamlit Dashboard & Web Application
Features Dedicated Admin & Student Authentication Portals, Role-Based Views, and Intelligent Services.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import random
import os
import json

import database as db
import ai_engine as ai

# Page configuration
st.set_page_config(
    page_title="SmartHostel AI Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db.init_database()

# Custom Modern Glassmorphism & Dashboard CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4 {
        font-family: 'Outfit', 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
        padding: 24px 30px;
        border-radius: 18px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .auth-hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%);
        border-radius: 20px;
        padding: 30px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 12px 35px rgba(15, 23, 42, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .auth-card {
        background: white;
        border-radius: 18px;
        padding: 26px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
    }

    .feature-pill-card {
        background: white;
        border-radius: 14px;
        padding: 18px;
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .feature-pill-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.09);
    }

    .badge-urgent {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-high {
        background-color: #ffedd5;
        color: #9a3412;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-success {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-info {
        background-color: #e0f2fe;
        color: #075985;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-admin {
        background-color: #f3e8ff;
        color: #6b21a8;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }

    .gate-pass-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #334155;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }

    .ai-bubble {
        background: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 14px 18px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 12px;
        color: #14532d;
    }

    .ai-bubble-blue {
        background: #f0f9ff;
        border-left: 4px solid #0284c7;
        padding: 14px 18px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 12px;
        color: #0c4a6e;
    }

    .profile-card {
        background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 14px;
    }

    /* Voice Assistant Hologram & Studio Styling */
    .voice-studio-container {
        background: linear-gradient(135deg, #090d16 0%, #0f172a 50%, #1e1b4b 100%);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 24px;
        padding: 32px 24px;
        color: white;
        text-align: center;
        box-shadow: 0 20px 50px rgba(15, 23, 42, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .voice-studio-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.12) 0%, transparent 60%);
        pointer-events: none;
    }
    .voice-orb-wrapper {
        position: relative;
        width: 140px;
        height: 140px;
        margin: 0 auto 20px auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .voice-orb {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: radial-gradient(circle, #6366f1 0%, #3b82f6 50%, #1e1b4b 100%);
        box-shadow: 0 0 35px rgba(99, 102, 241, 0.6), inset 0 0 20px rgba(255, 255, 255, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.2rem;
        cursor: pointer;
        transition: transform 0.3s, box-shadow 0.3s;
        z-index: 2;
    }
    .voice-orb:hover {
        transform: scale(1.08);
        box-shadow: 0 0 50px rgba(99, 102, 241, 0.9), inset 0 0 25px rgba(255, 255, 255, 0.6);
    }
    .voice-pulse-ring {
        position: absolute;
        width: 130px;
        height: 130px;
        border-radius: 50%;
        border: 2px solid rgba(99, 102, 241, 0.4);
        animation: orb-pulse 2.2s infinite ease-out;
        z-index: 1;
    }
    .voice-pulse-ring-2 {
        position: absolute;
        width: 160px;
        height: 160px;
        border-radius: 50%;
        border: 1px dashed rgba(56, 189, 248, 0.3);
        animation: orb-rotate 8s infinite linear;
        z-index: 0;
    }
    @keyframes orb-pulse {
        0% { transform: scale(0.7); opacity: 0.8; }
        50% { opacity: 0.4; }
        100% { transform: scale(1.3); opacity: 0; }
    }
    @keyframes orb-rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .sound-equalizer {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        height: 28px;
        margin: 12px auto;
    }
    .sound-bar {
        width: 4px;
        height: 8px;
        background: #38bdf8;
        border-radius: 2px;
        animation: sound-bounce 1.2s infinite ease-in-out;
    }
    .sound-bar:nth-child(2) { animation-delay: 0.2s; height: 16px; background: #6366f1; }
    .sound-bar:nth-child(3) { animation-delay: 0.4s; height: 24px; background: #a855f7; }
    .sound-bar:nth-child(4) { animation-delay: 0.6s; height: 18px; background: #38bdf8; }
    .sound-bar:nth-child(5) { animation-delay: 0.8s; height: 10px; background: #6366f1; }
    @keyframes sound-bounce {
        0%, 100% { transform: scaleY(0.4); }
        50% { transform: scaleY(1.4); }
    }
    .voice-intent-badge {
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 8px;
    }
    .spoken-bubble {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #38bdf8;
        border-radius: 0 12px 12px 0;
        padding: 14px 18px;
        margin: 12px 0;
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.5;
        text-align: left;
    }
    .sustainability-card {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #047857 100%);
        color: white;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #10b981;
        box-shadow: 0 10px 25px rgba(6, 78, 59, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# Session State Initialization
# --------------------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""
if "logged_user" not in st.session_state:
    st.session_state["logged_user"] = ""
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {}
if "student_profile" not in st.session_state:
    st.session_state["student_profile"] = {}
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "👋 Hello! I am your **AI Hostel Assistant**. Ask me anything about room allotments, leave policies, mess menus, curfew hours, or maintenance status!"}
    ]
if "voice_history" not in st.session_state:
    st.session_state["voice_history"] = []
if "voice_auto_speak" not in st.session_state:
    st.session_state["voice_auto_speak"] = True
if "voice_accent" not in st.session_state:
    st.session_state["voice_accent"] = "en-IN"
if "last_voice_result" not in st.session_state:
    st.session_state["last_voice_result"] = None
if "emergency_sos_alert" not in st.session_state:
    st.session_state["emergency_sos_alert"] = False


def logout_user():
    """Logs out the current active session."""
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = ""
    st.session_state["logged_user"] = ""
    st.session_state["user_data"] = {}
    st.session_state["student_profile"] = {}
    st.session_state["last_voice_result"] = None
    st.session_state["emergency_sos_alert"] = False
    st.rerun()


# ======================================================================================
# AUTHENTICATION GATEWAY (LOGIN & REGISTRATION PORTAL)
# ======================================================================================
if not st.session_state["authenticated"]:

    # Sidebar Login Info & Demo Switcher
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 10px 0 16px 0;">
            <h2 style="margin: 0; color: #1e3c72; font-size: 1.5rem;">🏢 SmartHostel AI</h2>
            <span style="font-size: 0.8rem; color: #64748b; font-weight: 500;">SECURE ACCESS PORTAL</span>
        </div>
        """, unsafe_allow_html=True)

        st.info("🔐 **Access Portals Available:**\n- **Admin & Staff Portal**: For Chief Admin, Wardens, Security.\n- **Student Portal**: For residents with ID / roll code.\n- **Sign-Up**: Self-registration for new students.")
        
        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.8rem; color: #475569; background: #f8fafc; padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
            <strong>📌 Demo Quick Credentials:</strong><br><br>
            <strong>Chief Admin:</strong> <code>admin</code> / <code>admin123</code><br>
            <strong>Boys Warden:</strong> <code>warden_rajesh</code> / <code>warden123</code><br>
            <strong>Student 1:</strong> <code>STU-1001</code> / <code>student123</code><br>
            <strong>Student 2:</strong> <code>STU-1006</code> / <code>student123</code><br>
            <strong>Security:</strong> <code>security_gate</code> / <code>security123</code>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.75rem; color: #94a3b8; text-align: center;">
            SmartHostel AI v2.4 • Campus Safety & Housing Engine<br>
            24/7 Security Helpline: +91 98765 00000
        </div>
        """, unsafe_allow_html=True)

    # Hero Banner
    st.markdown("""
    <div class="auth-hero-banner">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
                <span class="badge-admin" style="background: rgba(255,255,255,0.15); color: #93c5fd; font-size: 0.85rem; padding: 6px 14px; margin-bottom: 10px;">
                    ✨ AI-Powered Smart Campus Living
                </span>
                <h1 style="margin: 8px 0 6px 0; font-size: 2.2rem; font-weight: 800; color: white;">SmartHostel AI Management Portal</h1>
                <p style="margin: 0; opacity: 0.9; font-size: 1rem; max-width: 680px; line-height: 1.5;">
                    Intelligent Room Allocation, Real-time NLP Maintenance Triage, Digital QR Gate Passes, and Automated Curfew & Dining Analytics.
                </p>
            </div>
            <div style="text-align: right; background: rgba(255,255,255,0.08); padding: 14px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.15);">
                <div style="font-size: 1.1rem; font-weight: 700; color: #4ade80;">🟢 SYSTEM ONLINE</div>
                <div style="font-size: 0.8rem; color: #cbd5e1;">Spring Boot & AI Engine Linked</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main Grid: Left Column = Tabs (Admin Login, Student Login, Register), Right Column = Highlights
    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        auth_tab_admin, auth_tab_student, auth_tab_register = st.tabs([
            "🛡️ Admin & Staff Login",
            "🎓 Student Resident Login",
            "✍️ Student Self-Registration"
        ])

        # ------------------------------------------------------------------------------
        # TAB 1: ADMIN & STAFF LOGIN
        # ------------------------------------------------------------------------------
        with auth_tab_admin:
            st.subheader("🛡️ Administrative & Staff Access")
            st.caption("Sign in with administrative, warden, or security credentials.")

            with st.form("admin_login_form"):
                admin_user_input = st.text_input("Username or Staff Email", placeholder="e.g. admin or warden_rajesh")
                admin_pass_input = st.text_input("Password", type="password", placeholder="Enter your password")
                
                admin_submit = st.form_submit_button("🔐 Sign In as Administrator / Staff", use_container_width=True)

                if admin_submit:
                    success, user, profile = db.authenticate_user(
                        admin_user_input, 
                        admin_pass_input, 
                        allowed_roles=["ADMIN", "WARDEN", "SECURITY"]
                    )
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_role"] = user["role"]
                        st.session_state["logged_user"] = user["full_name"]
                        st.session_state["user_data"] = user
                        st.session_state["student_profile"] = profile or {}
                        st.success(f"Welcome back, {user['full_name']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {user}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**⚡ 1-Click Quick Demo Login (Staff Roles):**")
            d_col1, d_col2, d_col3, d_col4 = st.columns(4)

            with d_col1:
                if st.button("👑 Chief Admin", key="demo_admin"):
                    success, user, profile = db.authenticate_user("admin", "admin123")
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_role"] = user["role"]
                        st.session_state["logged_user"] = user["full_name"]
                        st.session_state["user_data"] = user
                        st.rerun()

            with d_col2:
                if st.button("🏢 Boys Warden", key="demo_warden_b"):
                    success, user, profile = db.authenticate_user("warden_rajesh", "warden123")
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_role"] = user["role"]
                        st.session_state["logged_user"] = user["full_name"]
                        st.session_state["user_data"] = user
                        st.rerun()

            with d_col3:
                if st.button("🌸 Girls Warden", key="demo_warden_g"):
                    success, user, profile = db.authenticate_user("warden_sunita", "warden123")
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_role"] = user["role"]
                        st.session_state["logged_user"] = user["full_name"]
                        st.session_state["user_data"] = user
                        st.rerun()

            with d_col4:
                if st.button("🛡️ Security Post", key="demo_sec"):
                    success, user, profile = db.authenticate_user("security_gate", "security123")
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_role"] = user["role"]
                        st.session_state["logged_user"] = user["full_name"]
                        st.session_state["user_data"] = user
                        st.rerun()

        # ------------------------------------------------------------------------------
        # TAB 2: STUDENT RESIDENT LOGIN
        # ------------------------------------------------------------------------------
        with auth_tab_student:
            st.subheader("🎓 Student Resident Portal")
            st.caption("Sign in with your Student ID Code (e.g. STU-1001) or Username.")

            with st.form("student_login_form"):
                stu_id_input = st.text_input("Student ID Code or Username", placeholder="e.g. STU-1001 or aarav")
                stu_pass_input = st.text_input("Student Password", type="password", placeholder="Enter student password")

                stu_submit = st.form_submit_button("🎓 Sign In to Student Portal", use_container_width=True)

                if stu_submit:
                    success, user, profile = db.authenticate_user(
                        stu_id_input, 
                        stu_pass_input, 
                        allowed_roles="STUDENT"
                    )
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_role"] = user["role"]
                        st.session_state["logged_user"] = user["full_name"]
                        st.session_state["user_data"] = user
                        st.session_state["student_profile"] = profile or {}
                        st.success(f"Welcome back, {user['full_name']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {user}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**⚡ 1-Click Quick Demo Login (Student Residents):**")
            s_d1, s_d2, s_d3, s_d4 = st.columns(4)

            with s_d1:
                if st.button("👨‍🎓 Aarav (STU-1001)", key="demo_stu_aarav"):
                    success, user, profile = db.authenticate_user("STU-1001", "student123")
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_role"] = user["role"]
                        st.session_state["logged_user"] = user["full_name"]
                        st.session_state["user_data"] = user
                        st.session_state["student_profile"] = profile
                        st.rerun()

            with s_d2:
                if st.button("👩‍🎓 Ananya (STU-1006)", key="demo_stu_ananya"):
                    success, user, profile = db.authenticate_user("STU-1006", "student123")
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_role"] = user["role"]
                        st.session_state["logged_user"] = user["full_name"]
                        st.session_state["user_data"] = user
                        st.session_state["student_profile"] = profile
                        st.rerun()

            with s_d3:
                if st.button("👨‍🎓 Vikram (STU-1002)", key="demo_stu_vikram"):
                    success, user, profile = db.authenticate_user("STU-1002", "student123")
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_role"] = user["role"]
                        st.session_state["logged_user"] = user["full_name"]
                        st.session_state["user_data"] = user
                        st.session_state["student_profile"] = profile
                        st.rerun()

            with s_d4:
                if st.button("👩‍🎓 Pooja (STU-1007)", key="demo_stu_pooja"):
                    success, user, profile = db.authenticate_user("STU-1007", "student123")
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_role"] = user["role"]
                        st.session_state["logged_user"] = user["full_name"]
                        st.session_state["user_data"] = user
                        st.session_state["student_profile"] = profile
                        st.rerun()

        # ------------------------------------------------------------------------------
        # TAB 3: STUDENT REGISTRATION / ACCOUNT ACTIVATION
        # ------------------------------------------------------------------------------
        with auth_tab_register:
            st.subheader("✍️ Resident Onboarding & Account Activation")
            st.caption("Newly admitted students can register their profile to generate credentials.")

            with st.form("student_registration_form"):
                all_stus_cnt = len(db.fetch_all("SELECT id FROM students"))
                default_code = f"STU-{1000 + all_stus_cnt + 1}"

                r_c1, r_c2 = st.columns(2)
                with r_c1:
                    reg_code = st.text_input("Assigned Student ID Code", value=default_code)
                    reg_name = st.text_input("Full Name", placeholder="e.g. Siddharth Verma")
                    reg_email = st.text_input("Campus Email", placeholder="e.g. siddharth.v@campus.edu")
                    reg_phone = st.text_input("Mobile Number", value="+91 91234 56700")
                    reg_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                    reg_dept = st.selectbox("Department", [
                        "Computer Science", "Information Science", "Electronics & Comm", 
                        "Mechanical Eng", "Biotechnology", "Electrical Eng", "Civil Engineering", 
                        "Artificial Intelligence"
                    ])
                
                with r_c2:
                    reg_year = st.selectbox("Academic Year", [1, 2, 3, 4])
                    reg_diet = st.selectbox("Dietary Preference", ["Veg", "Non-Veg", "Eggetarian"])
                    reg_sleep = st.selectbox("Sleep Habit", ["Early Bird", "Night Owl", "Flexible"])
                    reg_study = st.selectbox("Study Style", ["Silent / Intensive", "Group / Music", "Moderate"])
                    reg_clean = st.selectbox("Cleanliness Standard", ["Very High", "High", "Moderate"])
                    reg_password = st.text_input("Create Account Password", type="password", value="student123")

                reg_submit = st.form_submit_button("🚀 Activate Student Account & Sign In", use_container_width=True)

                if reg_submit:
                    s_data = {
                        "student_id_code": reg_code,
                        "username": reg_code.lower().replace("-", ""),
                        "name": reg_name,
                        "email": reg_email,
                        "phone": reg_phone,
                        "gender": reg_gender,
                        "department": reg_dept,
                        "year": reg_year,
                        "dietary_pref": reg_diet,
                        "sleep_habit": reg_sleep,
                        "study_habit": reg_study,
                        "cleanliness": reg_clean
                    }
                    ok, msg, res_data = db.register_student_account(s_data, reg_password)
                    if ok:
                        st.success("🎉 Account successfully registered and activated!")
                        st.session_state["authenticated"] = True
                        st.session_state["user_role"] = "STUDENT"
                        st.session_state["logged_user"] = res_data["user"]["full_name"]
                        st.session_state["user_data"] = res_data["user"]
                        st.session_state["student_profile"] = res_data["student"]
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        st.markdown('</div>', unsafe_allow_html=True)

    # Right Column: Platform Capabilities Spotlight
    with right_col:
        st.markdown("""
        <div class="feature-pill-card">
            <h3 style="margin: 0 0 6px 0; color: #1e3c72; font-size: 1.15rem;">🎯 AI Compatibility Room Allocation</h3>
            <p style="margin: 0; color: #475569; font-size: 0.88rem; line-height: 1.5;">
                Matches unallocated students and roommate candidates with multi-factor psychological, study style, sleep rhythm, and cleanliness synergy scoring.
            </p>
        </div>

        <div class="feature-pill-card">
            <h3 style="margin: 0 0 6px 0; color: #0284c7; font-size: 1.15rem;">🛠️ Zero-Delay NLP Maintenance Triage</h3>
            <p style="margin: 0; color: #475569; font-size: 0.88rem; line-height: 1.5;">
                Students describe complaints in natural language. The AI instantly parses department routing, severity SLA, sentiment, and technician action items.
            </p>
        </div>

        <div class="feature-pill-card">
            <h3 style="margin: 0 0 6px 0; color: #16a34a; font-size: 1.15rem;">✈️ Digital QR Gate Passes & Curfew</h3>
            <p style="margin: 0; color: #475569; font-size: 0.88rem; line-height: 1.5;">
                Paperless outstation leave applications, Warden electronic approvals, and encrypted QR turnstile verification for campus gate security.
            </p>
        </div>

        <div class="feature-pill-card">
            <h3 style="margin: 0 0 6px 0; color: #9333ea; font-size: 1.15rem;">🍲 Predictive Dining Waste Analytics</h3>
            <p style="margin: 0; color: #475569; font-size: 0.88rem; line-height: 1.5;">
                Real-time active student headcount and leave forecaster optimizing daily raw material preparation batches and curbing food waste by 25%+.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# ======================================================================================
# AUTHENTICATED DASHBOARD & NAVIGATION
# ======================================================================================

# Refresh student profile if student
if st.session_state.get("user_role") == "STUDENT" and st.session_state.get("user_data", {}).get("student_id"):
    st.session_state["student_profile"] = db.get_student_profile(st.session_state["user_data"]["student_id"])

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 6px 0 16px 0;">
        <h2 style="margin: 0; color: #1e3c72; font-size: 1.45rem;">🏢 SmartHostel AI</h2>
        <span style="font-size: 0.75rem; color: #64748b; font-weight: 600; letter-spacing: 0.5px;">CAMPUS INTELLIGENCE</span>
    </div>
    """, unsafe_allow_html=True)

    # Active User Profile Card
    u_role = st.session_state.get("user_role", "STUDENT")
    role_badge_class = {
        "ADMIN": "badge-admin",
        "WARDEN": "badge-urgent",
        "STUDENT": "badge-success",
        "SECURITY": "badge-high"
    }.get(u_role, "badge-info")

    stu_info_snippet = ""
    if u_role == "STUDENT":
        sp = st.session_state.get("student_profile", {})
        r_num = sp.get("room_details", {}).get("room_number") if sp.get("room_details") else "Unassigned"
        stu_code = sp.get("student_id_code", "STU")
        dept = sp.get("department", "")
        stu_info_snippet = f"<br>🆔 <code>{stu_code}</code> • 🚪 Room {r_num}<br>📚 {dept} (Yr {sp.get('year', 1)})"

    st.markdown(f"""
    <div class="profile-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>👤 {st.session_state['logged_user']}</strong>
            <span class="{role_badge_class}">{u_role}</span>
        </div>
        <div style="font-size: 0.8rem; color: #475569; margin-top: 4px;">
            {stu_info_snippet}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Logout Button
    if st.button("🚪 Sign Out / Switch User", use_container_width=True):
        logout_user()

    st.markdown("---")

    # Dynamic Menu Options based on Active Role
    if u_role in ["ADMIN", "WARDEN"]:
        menu_options = [
            "📊 Dashboard Overview",
            "🎙️ Voice AI Command Center",
            "🏢 Hostel & Room Matrix",
            "🎯 AI Smart Room Allocation",
            "👨‍🎓 Student Directory",
            "🛠️ AI Complaints & Triage",
            "📅 Smart Attendance & Curfew",
            "✈️ Leave & Digital Gate Pass",
            "🍲 Mess & AI Waste Analytics",
            "💳 Fee & Risk Defaulters",
            "🛡️ Visitor Log & Gate Security",
            "📢 Notice Board & Broadcasts",
            "🤖 AI Hostel Assistant (Chatbot)"
        ]
    elif u_role == "STUDENT":
        menu_options = [
            "🏠 My Student Dashboard",
            "🎙️ Voice AI Command Center",
            "🚪 My Room & Roommates",
            "✈️ Apply Leave & Active Gate Pass",
            "🛠️ File & Track Complaints (AI Triage)",
            "🍲 Mess Menu & Daily Schedule",
            "💳 My Fee Status & Receipts",
            "📢 Campus Notices & Circulars",
            "🤖 AI Hostel Assistant (Chatbot)"
        ]
    elif u_role == "SECURITY":
        menu_options = [
            "🎫 Gate Pass QR Scanner & Verifier",
            "🎙️ Voice AI Command Center",
            "📅 Curfew & Night Check-In Log",
            "🛡️ Visitor Entry & Check-Out Registry",
            "📢 Campus Emergency Broadcasts",
            "🤖 AI Hostel Assistant (Chatbot)"
        ]
    else:
        menu_options = ["📊 Dashboard Overview", "🎙️ Voice AI Command Center", "🤖 AI Hostel Assistant (Chatbot)"]

    selected_menu = st.radio("Navigation", menu_options, label_visibility="collapsed")


# ======================================================================================
# 1. ADMIN / WARDEN: DASHBOARD OVERVIEW
# ======================================================================================
if selected_menu == "📊 Dashboard Overview":
    st.markdown("""
    <div class="main-header">
        <div>
            <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700;">Hostel Command & Intelligence Dashboard</h1>
            <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 0.95rem;">Real-time campus occupancy, AI maintenance status, and predictive analytics.</p>
        </div>
        <div style="text-align: right;">
            <span class="badge-success" style="font-size: 0.85rem; padding: 6px 14px;">🟢 System Live & Nominal</span><br>
            <span style="font-size: 0.8rem; opacity: 0.8;">Updated Just Now</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch live metrics
    students = db.fetch_all("SELECT * FROM students")
    rooms = db.fetch_all("SELECT * FROM rooms")
    complaints = db.fetch_all("SELECT * FROM complaints")
    leaves = db.fetch_all("SELECT * FROM leave_requests WHERE status = 'APPROVED'")
    unallocated = [s for s in students if not s["room_id"]]
    open_complaints = [c for c in complaints if c["status"] in ["OPEN", "IN_PROGRESS"]]
    urgent_complaints = [c for c in open_complaints if c["priority"] in ["URGENT", "HIGH"]]

    total_beds = sum(r["capacity"] for r in rooms)
    occupied_beds = sum(r["occupied_beds"] for r in rooms)
    occupancy_rate = (occupied_beds / max(1, total_beds)) * 100

    # Top KPI Metrics Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Total Residents</span>
            <h2 style="margin: 8px 0 4px 0; color: #0f172a; font-weight: 700;">{len(students)}</h2>
            <span style="font-size: 0.8rem; color: {'#e11d48' if len(unallocated) > 0 else '#16a34a'};">
                {len(unallocated)} pending room allocation
            </span>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Bed Occupancy</span>
            <h2 style="margin: 8px 0 4px 0; color: #2563eb; font-weight: 700;">{occupied_beds} / {total_beds}</h2>
            <span style="font-size: 0.8rem; color: #64748b;">
                <strong>{occupancy_rate:.1f}%</strong> total capacity
            </span>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Active Complaints</span>
            <h2 style="margin: 8px 0 4px 0; color: {'#e11d48' if len(urgent_complaints) > 0 else '#0f172a'}; font-weight: 700;">{len(open_complaints)}</h2>
            <span class="{'badge-urgent' if len(urgent_complaints) > 0 else 'badge-info'}">
                {len(urgent_complaints)} High / Urgent Priority
            </span>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Active Gate Passes</span>
            <h2 style="margin: 8px 0 4px 0; color: #16a34a; font-weight: 700;">{len(leaves)}</h2>
            <span style="font-size: 0.8rem; color: #64748b;">
                Students currently on leave
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.subheader("🏢 Block-Wise Room Occupancy Distribution")
        df_rooms = pd.DataFrame(rooms)
        if not df_rooms.empty:
            block_summary = df_rooms.groupby(['hostel_name', 'block_name']).agg(
                Occupied=('occupied_beds', 'sum'),
                Total=('capacity', 'sum')
            ).reset_index()
            block_summary['Vacant'] = block_summary['Total'] - block_summary['Occupied']

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=block_summary['block_name'], 
                y=block_summary['Occupied'], 
                name='Occupied Beds', 
                marker_color='#3b82f6'
            ))
            fig.add_trace(go.Bar(
                x=block_summary['block_name'], 
                y=block_summary['Vacant'], 
                name='Available Beds', 
                marker_color='#cbd5e1'
            ))
            fig.update_layout(
                barmode='stack',
                margin=dict(l=20, r=20, t=30, b=20),
                height=320,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🛠️ AI Complaint Category Matrix")
        df_complaints = pd.DataFrame(complaints)
        if not df_complaints.empty:
            cat_counts = df_complaints['category'].value_counts().reset_index()
            cat_counts.columns = ['Category', 'Count']
            fig_pie = px.pie(
                cat_counts, 
                values='Count', 
                names='Category', 
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=320)
            st.plotly_chart(fig_pie, use_container_width=True)

    # Recent Live Feeds
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("### 🚨 Urgent Attention & Open Complaints")
        if open_complaints:
            for c in open_complaints[:4]:
                badge_class = "badge-urgent" if c["priority"] in ["URGENT", "HIGH"] else "badge-info"
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; padding: 12px 16px; border-radius: 10px; margin-bottom: 8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong>{c['title']}</strong>
                        <span class="{badge_class}">{c['priority']}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">
                        Room {c['room_number']} • {c['student_name']} • <em>{c['department']}</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No open complaints. All maintenance requests are resolved!")

    with r2:
        st.markdown("### 📢 Active Campus Notices")
        notices = db.fetch_all("SELECT * FROM notices ORDER BY id DESC LIMIT 3")
        for n in notices:
            p_badge = "badge-urgent" if n["priority"] == "URGENT" else ("badge-high" if n["priority"] == "HIGH" else "badge-info")
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; padding: 12px 16px; border-radius: 10px; margin-bottom: 8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong>{n['title']}</strong>
                    <span class="{p_badge}">{n['category']}</span>
                </div>
                <p style="font-size: 0.85rem; color: #475569; margin: 6px 0 4px 0;">{n['content']}</p>
                <div style="font-size: 0.75rem; color: #94a3b8;">Posted by {n['posted_by']} • {n['posted_at']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ADVANCED AI SECTION: CAMPUS ENERGY & SUSTAINABILITY PREDICTOR
    st.markdown("---")
    st.markdown("### 🌿 AI Smart Campus Energy & Sustainability Intelligence")
    e_col1, e_col2 = st.columns([1, 1.4])
    with e_col1:
        st.markdown("""
        <div class="sustainability-card">
            <h4 style="margin:0 0 6px 0; color:#a7f3d0;">🌿 Autonomous Power & Carbon Optimizer</h4>
            <p style="margin:0 0 12px 0; font-size:0.88rem; opacity:0.95;">
                Simulates real-time HVAC loads, grid power consumption, and carbon emissions based on block occupancy and environmental factors.
            </p>
        </div>
        """, unsafe_allow_html=True)
        sim_temp = st.slider("Ambient Campus Temperature (°C)", min_value=16.0, max_value=42.0, value=29.0, step=0.5)
        energy_forecast = ai.predict_campus_energy_demand(
            total_students=len(students),
            occupancy_pct=occupancy_rate,
            avg_temp_c=sim_temp,
            day_name=datetime.now().strftime("%A")
        )
        st.info(energy_forecast["recommendation"])

    with e_col2:
        ek1, ek2, ek3 = st.columns(3)
        with ek1:
            st.metric("Total Daily Load", f"{energy_forecast['daily_total_kwh']} kWh", f"Peak: {energy_forecast['peak_kw']} kW")
        with ek2:
            st.metric("AC & HVAC Share", f"{energy_forecast['ac_hvac_kwh']} kWh", f"{int((energy_forecast['ac_hvac_kwh']/energy_forecast['daily_total_kwh'])*100)}% load")
        with ek3:
            st.metric("Campus Green Score", f"{energy_forecast['green_score']}/100", f"Carbon: {energy_forecast['carbon_kg']} kg")

        df_energy = pd.DataFrame(energy_forecast["hourly_curve"])
        fig_energy = px.area(df_energy, x="hour", y="kwh", title="24-Hour Projected Electricity Demand Curve (kWh)", color_discrete_sequence=["#10b981"])
        fig_energy.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=220)
        st.plotly_chart(fig_energy, use_container_width=True)


# ======================================================================================
# VOICE AI COMMAND CENTER (FULL SUITE FOR ADMIN, WARDEN, STUDENT & SECURITY)
# ======================================================================================
elif selected_menu == "🎙️ Voice AI Command Center":
    st.markdown("""
    <div class="voice-studio-container">
        <div class="voice-pulse-ring-2"></div>
        <div class="voice-pulse-ring"></div>
        <div class="voice-orb-wrapper">
            <div class="voice-orb">
                🎙️
            </div>
        </div>
        <h2 style="margin: 0 0 6px 0; font-size: 2rem; font-weight: 800; color: white; letter-spacing: -0.5px;">
            SmartHostel Advanced Voice AI Assistant
        </h2>
        <p style="margin: 0 auto; max-width: 650px; font-size: 0.95rem; opacity: 0.88; line-height: 1.5;">
            Zero-latency, dual-mode speech engine: Speak directly through your microphone, test high-speed voice command buttons, or trigger instant voice emergency SOS broadcasts.
        </p>
        <div class="sound-equalizer">
            <div class="sound-bar"></div>
            <div class="sound-bar"></div>
            <div class="sound-bar"></div>
            <div class="sound-bar"></div>
            <div class="sound-bar"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Voice Engine Settings Bar
    v_set1, v_set2, v_set3 = st.columns([1, 1, 1.2])
    with v_set1:
        st.session_state["voice_auto_speak"] = st.toggle("🔊 Auto-Play Spoken Response", value=st.session_state.get("voice_auto_speak", True))
    with v_set2:
        voice_lang = st.selectbox("🌐 Accent & Language", ["English (India) - en-IN", "English (US) - en-US", "English (UK) - en-GB"])
        lang_code = "en"
        tld_val = "co.in" if "India" in voice_lang else ("co.uk" if "UK" in voice_lang else "com")
    with v_set3:
        if st.button("🧹 Clear Voice Interaction Logs", use_container_width=True):
            st.session_state["voice_history"] = []
            st.session_state["last_voice_result"] = None
            st.rerun()

    st.markdown("---")

    voice_col_left, voice_col_right = st.columns([1.1, 1])

    with voice_col_left:
        st.subheader("🎙️ Mode 1: Live Voice Input")
        st.caption("Record your spoken request using your browser's microphone or enter a voice prompt.")

        # Streamlit Native Audio Input
        recorded_audio = st.audio_input("🔴 Press to Speak & Record Audio")
        
        recognized_voice_text = ""
        if recorded_audio is not None:
            audio_bytes = recorded_audio.read()
            if audio_bytes:
                with st.spinner("🎧 Transcribing your voice input with SpeechRecognition engine..."):
                    recognized_voice_text = ai.transcribe_audio_bytes(audio_bytes)
                if recognized_voice_text:
                    st.success(f"🗣️ Transcribed Voice: *\"{recognized_voice_text}\"*")
                else:
                    st.info("🎙️ Audio captured. If cloud STT is unavailable on local network, you can also use one-click voice command buttons below or enter spoken text:")

        # Fallback / Direct Spoken Prompt Input
        spoken_input = st.text_input(
            "Or Type a Spoken Command to Process with Voice AI:", 
            value=recognized_voice_text,
            placeholder="e.g. 'What is for dinner tonight?', 'Report issue: tap leaking in washroom', 'Emergency SOS'"
        )

        exec_c1, exec_c2 = st.columns([1, 1])
        with exec_c1:
            run_voice_btn = st.button("⚡ Execute Voice Intent", type="primary", use_container_width=True)
        with exec_c2:
            sos_voice_btn = st.button("🚨 TRIGGER VOICE SOS", type="secondary", use_container_width=True)

        user_ctx = {
            "user_role": st.session_state.get("user_role", "STUDENT"),
            "logged_user": st.session_state.get("logged_user", "Resident"),
            "student_profile": st.session_state.get("student_profile", {})
        }

        # Process input
        cmd_to_process = None
        if run_voice_btn and spoken_input.strip():
            cmd_to_process = spoken_input.strip()
        elif sos_voice_btn:
            cmd_to_process = "EMERGENCY SOS: Immediate security and medical dispatch required"

        if cmd_to_process:
            with st.spinner("🤖 Voice AI is parsing intent, executing database actions, and synthesizing speech..."):
                v_res = ai.parse_voice_command(cmd_to_process, user_context=user_ctx)
                st.session_state["last_voice_result"] = v_res
                st.session_state["voice_history"].insert(0, {
                    "query": cmd_to_process,
                    "result": v_res,
                    "timestamp": datetime.now().strftime("%I:%M:%S %p")
                })
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("⚡ Mode 2: Quick Spoken Scenarios (One-Click)")
        st.caption("Experience instantaneous voice response synthesis across everyday hostel routines:")

        qc1, qc2 = st.columns(2)
        with qc1:
            if st.button("🍲 'What's for dinner tonight?'", use_container_width=True):
                v_res = ai.parse_voice_command("What is for dinner tonight?", user_context=user_ctx)
                st.session_state["last_voice_result"] = v_res
                st.session_state["voice_history"].insert(0, {"query": "What is for dinner tonight?", "result": v_res, "timestamp": datetime.now().strftime("%I:%M:%S %p")})
                st.rerun()

            if st.button("🚪 'Who are my roommates?'", use_container_width=True):
                v_res = ai.parse_voice_command("Who are my roommates?", user_context=user_ctx)
                st.session_state["last_voice_result"] = v_res
                st.session_state["voice_history"].insert(0, {"query": "Who are my roommates?", "result": v_res, "timestamp": datetime.now().strftime("%I:%M:%S %p")})
                st.rerun()

            if st.button("🛠️ 'Report broken fan in room'", use_container_width=True):
                v_res = ai.parse_voice_command("Report issue: Ceiling fan is vibrating and making loud noise in room", user_context=user_ctx)
                st.session_state["last_voice_result"] = v_res
                st.session_state["voice_history"].insert(0, {"query": "Report issue: Ceiling fan broken", "result": v_res, "timestamp": datetime.now().strftime("%I:%M:%S %p")})
                st.rerun()

        with qc2:
            if st.button("🕒 'What are curfew timings?'", use_container_width=True):
                v_res = ai.parse_voice_command("What are the night curfew timings and gate close hours?", user_context=user_ctx)
                st.session_state["last_voice_result"] = v_res
                st.session_state["voice_history"].insert(0, {"query": "Curfew timings", "result": v_res, "timestamp": datetime.now().strftime("%I:%M:%S %p")})
                st.rerun()

            if st.button("💳 'Check my fee balance'", use_container_width=True):
                v_res = ai.parse_voice_command("Check my hostel fee balance and due amount", user_context=user_ctx)
                st.session_state["last_voice_result"] = v_res
                st.session_state["voice_history"].insert(0, {"query": "Check fee balance", "result": v_res, "timestamp": datetime.now().strftime("%I:%M:%S %p")})
                st.rerun()

            if st.button("📊 'Hostel operational stats'", use_container_width=True):
                v_res = ai.parse_voice_command("Give me the current hostel stats and occupancy", user_context=user_ctx)
                st.session_state["last_voice_result"] = v_res
                st.session_state["voice_history"].insert(0, {"query": "Operational stats", "result": v_res, "timestamp": datetime.now().strftime("%I:%M:%S %p")})
                st.rerun()

    with voice_col_right:
        st.subheader("🔊 Live Voice Response & Audio Player")
        
        last_res = st.session_state.get("last_voice_result")
        if last_res:
            intent_label = last_res.get("intent", "GENERAL")
            st.markdown(f"""
            <div style="background: white; border: 1px solid #cbd5e1; border-radius: 16px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <span class="voice-intent-badge">🎯 Intent: {intent_label}</span>
                        {'<span class="badge-urgent">⚡ Action Executed</span>' if last_res.get('action_taken') else '<span class="badge-info">ℹ️ Info Query</span>'}
                    </div>
                    <span style="font-size: 0.8rem; color: #64748b;">Grounded Live DB</span>
                </div>
                <div class="spoken-bubble">
                    <strong>🗣️ Spoken Voice Output:</strong><br>
                    "{last_res.get('spoken_text', '')}"
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Audio Player with Autoplay capability
            audio_b64 = last_res.get("audio_base64", "")
            if audio_b64:
                autoplay_attr = "autoplay" if st.session_state.get("voice_auto_speak", True) else ""
                audio_html = f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 12px; margin-bottom: 16px; text-align: center;">
                    <span style="font-size: 0.85rem; color: #475569; font-weight: 600; display: block; margin-bottom: 8px;">
                        🎧 High-Fidelity Voice Synthesis (gTTS Engine)
                    </span>
                    <audio controls {autoplay_attr} style="width: 100%;">
                        <source src="{audio_b64}" type="audio/mp3">
                        Your browser does not support the audio element.
                    </audio>
                </div>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
            else:
                st.info("Audio synthesis stream standby.")

            # Formatted Action/Markdown Card
            st.markdown(last_res.get("markdown_display", ""), unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style="background: white; border: 2px dashed #cbd5e1; border-radius: 16px; padding: 36px 20px; text-align: center; color: #64748b;">
                <div style="font-size: 2.8rem; margin-bottom: 12px;">🎙️</div>
                <h4 style="margin: 0 0 6px 0; color: #334155;">Voice Assistant Standby</h4>
                <p style="margin: 0; font-size: 0.88rem;">
                    Speak into the microphone or click any quick command on the left to hear real-time AI speech synthesis.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Voice Command History Timeline
    if st.session_state.get("voice_history"):
        st.markdown("---")
        st.subheader("📜 Voice Command Session History")
        for h in st.session_state["voice_history"][:5]:
            with st.expander(f"🕒 {h['timestamp']} — \"{h['query']}\" ({h['result']['intent']})"):
                st.markdown(f"**🗣️ Spoken Output:** {h['result']['spoken_text']}")
                st.markdown(h['result']['markdown_display'], unsafe_allow_html=True)



# ======================================================================================
# 2. ADMIN / WARDEN: HOSTEL & ROOM MATRIX
# ======================================================================================
elif selected_menu == "🏢 Hostel & Room Matrix":
    st.title("🏢 Hostel & Room Infrastructure Matrix")
    st.caption("Live digital twin of hostel buildings, blocks, floors, and bed occupancy states.")

    # Filter controls
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    hostels = db.fetch_all("SELECT DISTINCT hostel_name FROM rooms")
    hostel_opts = ["All Hostels"] + [h["hostel_name"] for h in hostels]
    
    with f_col1:
        sel_hostel = st.selectbox("Filter Hostel", hostel_opts)
    with f_col2:
        status_opts = ["All Statuses", "AVAILABLE", "PARTIALLY_OCCUPIED", "FULL", "MAINTENANCE"]
        sel_status = st.selectbox("Filter Status", status_opts)
    with f_col3:
        type_opts = ["All Types", "Single", "Double", "Triple", "Quad"]
        sel_type = st.selectbox("Room Type", type_opts)
    with f_col4:
        search_kw = st.text_input("🔍 Search Room / Bed No.", "")

    # Build query
    query = "SELECT * FROM rooms WHERE 1=1"
    params = []
    if sel_hostel != "All Hostels":
        query += " AND hostel_name = ?"
        params.append(sel_hostel)
    if sel_status != "All Statuses":
        query += " AND status = ?"
        params.append(sel_status)
    if sel_type != "All Types":
        query += " AND room_type = ?"
        params.append(sel_type)
    if search_kw:
        query += " AND (room_number LIKE ? OR amenities LIKE ?)"
        params.extend([f"%{search_kw}%", f"%{search_kw}%"])

    room_rows = db.fetch_all(query, params)

    st.markdown(f"**Found {len(room_rows)} matching rooms:**")
    
    cols = st.columns(3)
    for idx, r in enumerate(room_rows):
        with cols[idx % 3]:
            status_badge = {
                "AVAILABLE": "badge-success",
                "PARTIALLY_OCCUPIED": "badge-info",
                "FULL": "badge-urgent",
                "MAINTENANCE": "badge-high"
            }.get(r["status"], "badge-info")

            room_students = db.fetch_all("SELECT name, year, department FROM students WHERE room_id = ?", (r["id"],))
            occupants_str = ", ".join([s["name"].split()[0] for s in room_students]) if room_students else "None (Vacant)"

            st.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin: 0; color: #1e3c72; font-size: 1.2rem;">🚪 {r['room_number']}</h3>
                    <span class="{status_badge}">{r['status']}</span>
                </div>
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">
                    {r['hostel_name']} • {r['block_name']} • Floor {r['floor_number']}
                </div>
                <hr style="margin: 8px 0; border: none; border-top: 1px solid #f1f5f9;">
                <div style="font-size: 0.85rem; color: #334155; line-height: 1.5;">
                    🛏️ <strong>Beds:</strong> {r['occupied_beds']} / {r['capacity']} ({r['room_type']})<br>
                    💵 <strong>Rent:</strong> ₹{r['rent_per_month']:,.0f}/mo<br>
                    ✨ <strong>Amenities:</strong> {r['amenities'] or 'Standard'}<br>
                    👥 <strong>Residents:</strong> {occupants_str}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if st.session_state["user_role"] in ["ADMIN", "WARDEN"]:
        with st.expander("➕ Add New Room to Inventory"):
            with st.form("new_room_form"):
                nr_c1, nr_c2, nr_c3 = st.columns(3)
                with nr_c1:
                    new_hostel = st.selectbox("Hostel", [h["hostel_name"] for h in hostels])
                    new_block = st.text_input("Block Name", "Block A")
                with nr_c2:
                    new_floor = st.number_input("Floor Number", min_value=0, max_value=10, value=1)
                    new_room_no = st.text_input("Room Number", "A-301")
                with nr_c3:
                    new_type = st.selectbox("Room Type", ["Single", "Double", "Triple", "Quad"])
                    new_capacity = {"Single": 1, "Double": 2, "Triple": 3, "Quad": 4}[new_type]
                    new_rent = st.number_input("Monthly Rent (₹)", min_value=1000, value=6500, step=500)
                
                new_amenities = st.text_input("Amenities", "AC, Attached Bath, Study Table")
                submit_room = st.form_submit_button("Save New Room")

                if submit_room:
                    try:
                        db.execute_query("""
                        INSERT INTO rooms (hostel_name, block_name, floor_number, room_number, room_type, capacity, occupied_beds, status, rent_per_month, amenities)
                        VALUES (?, ?, ?, ?, ?, ?, 0, 'AVAILABLE', ?, ?)
                        """, (new_hostel, new_block, new_floor, new_room_no, new_type, new_capacity, new_rent, new_amenities))
                        st.success(f"Room {new_room_no} successfully added to inventory!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding room: {e}")


# ======================================================================================
# 3. ADMIN / WARDEN: AI SMART ROOM ALLOCATION
# ======================================================================================
elif selected_menu == "🎯 AI Smart Room Allocation":
    st.title("🎯 AI Smart Room Allocation & Compatibility Matcher")
    st.caption("Matches unallocated students or room swap candidates using multi-factor psychological, habits, and lifestyle synergy AI scoring.")

    unallocated_students = db.fetch_all("SELECT * FROM students WHERE room_id IS NULL")
    all_students = db.fetch_all("SELECT * FROM students")
    available_rooms = db.fetch_all("SELECT * FROM rooms WHERE status != 'FULL' AND status != 'MAINTENANCE'")

    st.markdown("""
    <div class="ai-bubble-blue">
        <strong>🧠 AI Allocation Engine Status:</strong> Active & Ready<br>
        Analyzes 7 compatibility vectors: <em>Seniority (Year), Departmental Synergy, Sleep Cycles (Early Bird vs Night Owl), Study Style, Cleanliness Habits, AC Preferences, and Capacity</em>.
    </div>
    """, unsafe_allow_html=True)

    alloc_c1, alloc_c2 = st.columns([1, 1.4])

    # Pre-calculate recommendations for both radar visualization and ranked listing
    student_choices = {f"{s['name']} ({s['student_id_code']} - Yr {s['year']} {s['department']})": s['id'] for s in all_students}
    with alloc_c1:
        st.subheader("1. Select Candidate Student")
        sel_student_label = st.selectbox("Choose Student", list(student_choices.keys()))
        selected_stu_id = student_choices[sel_student_label]
        student_obj = db.fetch_one("SELECT * FROM students WHERE id = ?", (selected_stu_id,))

        recommendations = []
        for r in available_rooms:
            roommates = db.fetch_all("SELECT * FROM students WHERE room_id = ?", (r["id"],))
            comp = ai.calculate_room_compatibility(student_obj, r, roommates)
            if comp["score"] > 0:
                recommendations.append({
                    "room": r,
                    "comp": comp,
                    "roommates": roommates
                })
        recommendations.sort(key=lambda x: x["comp"]["score"], reverse=True)

        st.markdown(f"""
        <div style="background: white; border: 1px solid #e2e8f0; padding: 16px; border-radius: 12px; margin-top: 10px;">
            <h4 style="margin:0 0 8px 0; color:#1e3c72;">Student Profile</h4>
            <table style="width:100%; font-size:0.85rem; color:#334155;">
                <tr><td><strong>ID:</strong></td><td>{student_obj['student_id_code']}</td></tr>
                <tr><td><strong>Year / Dept:</strong></td><td>Year {student_obj['year']} • {student_obj['department']}</td></tr>
                <tr><td><strong>Sleep Schedule:</strong></td><td>🌙 {student_obj['sleep_habit']}</td></tr>
                <tr><td><strong>Study Style:</strong></td><td>📚 {student_obj['study_habit']}</td></tr>
                <tr><td><strong>Cleanliness:</strong></td><td>✨ {student_obj['cleanliness']}</td></tr>
                <tr><td><strong>Dietary:</strong></td><td>🥗 {student_obj['dietary_pref']}</td></tr>
                <tr><td><strong>Current Room:</strong></td><td>{student_obj['room_id'] or '❌ Unallocated'}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # Plotly Lifestyle Radar Chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🧭 Lifestyle Vector Compatibility Radar")
        target_peer = recommendations[0]["roommates"][0] if (recommendations and recommendations[0]["roommates"]) else None
        radar_info = ai.calculate_roommate_radar_profile(student_obj, target_peer)

        radar_categories = radar_info["categories"] + [radar_info["categories"][0]]
        s1_vals = radar_info["student1_values"] + [radar_info["student1_values"][0]]
        s2_vals = radar_info["student2_values"] + [radar_info["student2_values"][0]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=s1_vals,
            theta=radar_categories,
            fill='toself',
            name=radar_info["student1_name"],
            line_color='#2563eb'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=s2_vals,
            theta=radar_categories,
            fill='toself',
            name=radar_info["student2_name"],
            line_color='#10b981'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=280,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.caption(f"🧠 Multi-Factor Lifestyle Synergy Score: **{radar_info['synergy_score']}%** alignment.")

    with alloc_c2:
        st.subheader("2. AI Compatibility Rankings & Recommendations")

        if recommendations:
            for idx, rec in enumerate(recommendations[:5]):
                r = rec["room"]
                comp = rec["comp"]
                avail_beds = r["capacity"] - r["occupied_beds"]
                color = "#16a34a" if comp["score"] >= 80 else ("#2563eb" if comp["score"] >= 65 else "#ea580c")

                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-left: 6px solid {color}; padding: 16px; border-radius: 10px; margin-bottom: 12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin: 0; color: #0f172a;">Rank #{idx+1}: Room {r['room_number']} ({r['hostel_name']})</h4>
                        <span style="font-size: 1.1rem; font-weight: 700; color: {color};">{comp['percentage']} Match</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #64748b; margin: 4px 0;">
                        {r['room_type']} • Floor {r['floor_number']} • {avail_beds} bed(s) available • ₹{r['rent_per_month']:,.0f}/mo
                    </div>
                    <div style="font-size: 0.85rem; color: #334155; margin-top: 6px;">
                        <strong>Key Synergy Factors:</strong>
                        <ul style="margin: 4px 0 0 16px; padding: 0;">
                            {"".join([f"<li>{f}</li>" for f in comp['factors']])}
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state["user_role"] in ["ADMIN", "WARDEN"]:
                    if st.button(f"⚡ Allocate {student_obj['name']} to Room {r['room_number']}", key=f"alloc_btn_{r['id']}"):
                        if student_obj["room_id"]:
                            db.execute_query("UPDATE rooms SET occupied_beds = MAX(0, occupied_beds - 1) WHERE id = ?", (student_obj["room_id"],))
                            prev_r = db.fetch_one("SELECT * FROM rooms WHERE id = ?", (student_obj["room_id"],))
                            if prev_r:
                                new_st = "AVAILABLE" if prev_r["occupied_beds"] == 0 else "PARTIALLY_OCCUPIED"
                                db.execute_query("UPDATE rooms SET status = ? WHERE id = ?", (new_st, student_obj["room_id"]))

                        new_occ = r["occupied_beds"] + 1
                        new_status = "FULL" if new_occ >= r["capacity"] else "PARTIALLY_OCCUPIED"
                        db.execute_query("UPDATE rooms SET occupied_beds = ?, status = ? WHERE id = ?", (new_occ, new_status, r["id"]))
                        db.execute_query("UPDATE students SET room_id = ? WHERE id = ?", (r["id"], student_obj["id"]))
                        st.success(f"🎉 Successfully allocated {student_obj['name']} to Room {r['room_number']} with {comp['percentage']} compatibility!")
                        st.rerun()
        else:
            st.warning("No vacant rooms found meeting allocation constraints.")


# ======================================================================================
# 4. ADMIN / WARDEN: STUDENT DIRECTORY
# ======================================================================================
elif selected_menu == "👨‍🎓 Student Directory":
    st.title("👨‍🎓 Resident Student Directory")
    st.caption("Manage student registrations, contact details, roommate pairings, and guardian info.")

    sd_c1, sd_c2, sd_c3 = st.columns([1, 1, 1.5])
    with sd_c1:
        dept_filter = st.selectbox("Department", ["All Departments", "Computer Science", "Information Science", "Electronics & Comm", "Mechanical Eng", "Biotechnology", "Electrical Eng", "Civil Engineering", "Artificial Intelligence"])
    with sd_c2:
        year_filter = st.selectbox("Academic Year", ["All Years", 1, 2, 3, 4])
    with sd_c3:
        search_query = st.text_input("🔍 Search by Name, Student ID, or Email", "")

    s_query = """
    SELECT s.*, r.room_number, r.hostel_name, r.block_name 
    FROM students s 
    LEFT JOIN rooms r ON s.room_id = r.id 
    WHERE 1=1
    """
    s_params = []
    if dept_filter != "All Departments":
        s_query += " AND s.department = ?"
        s_params.append(dept_filter)
    if year_filter != "All Years":
        s_query += " AND s.year = ?"
        s_params.append(year_filter)
    if search_query:
        s_query += " AND (s.name LIKE ? OR s.student_id_code LIKE ? OR s.email LIKE ?)"
        s_params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

    student_list = db.fetch_all(s_query, s_params)
    st.markdown(f"**Showing {len(student_list)} residents:**")

    df_stu = pd.DataFrame(student_list)
    if not df_stu.empty:
        display_cols = ['student_id_code', 'name', 'gender', 'department', 'year', 'room_number', 'phone', 'email', 'fee_status', 'sleep_habit', 'dietary_pref']
        st.dataframe(
            df_stu[[c for c in display_cols if c in df_stu.columns]], 
            use_container_width=True, 
            hide_index=True
        )

    if st.session_state["user_role"] in ["ADMIN", "WARDEN"]:
        with st.expander("➕ Register New Resident Student"):
            with st.form("new_student_form"):
                ns1, ns2, ns3 = st.columns(3)
                with ns1:
                    n_code = st.text_input("Student ID Code", f"STU-{1000 + len(student_list) + 1}")
                    n_name = st.text_input("Full Name", "Pranav Hegde")
                    n_email = st.text_input("Email Address", "pranav.h@campus.edu")
                    n_phone = st.text_input("Contact Phone", "+91 91234 56799")
                with ns2:
                    n_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                    n_dept = st.selectbox("Department", ["Computer Science", "Information Science", "Electronics & Comm", "Mechanical Eng", "Biotechnology", "Electrical Eng", "Civil Engineering", "Artificial Intelligence"])
                    n_year = st.selectbox("Year of Study", [1, 2, 3, 4])
                    n_diet = st.selectbox("Dietary Preference", ["Veg", "Non-Veg", "Eggetarian"])
                with ns3:
                    n_sleep = st.selectbox("Sleep Habit", ["Early Bird", "Night Owl", "Flexible"])
                    n_study = st.selectbox("Study Style", ["Silent / Intensive", "Group / Music", "Moderate"])
                    n_clean = st.selectbox("Cleanliness Standard", ["Very High", "High", "Moderate"])
                    n_parent = st.text_input("Guardian Name", "Sanjay Hegde")
                    n_parent_phone = st.text_input("Guardian Phone", "+91 98111 22299")

                submit_student = st.form_submit_button("Register Student")
                if submit_student:
                    ok, msg, res = db.register_student_account({
                        "student_id_code": n_code,
                        "name": n_name,
                        "email": n_email,
                        "phone": n_phone,
                        "gender": n_gender,
                        "department": n_dept,
                        "year": n_year,
                        "dietary_pref": n_diet,
                        "sleep_habit": n_sleep,
                        "study_habit": n_study,
                        "cleanliness": n_clean,
                        "parent_name": n_parent,
                        "parent_phone": n_parent_phone
                    })
                    if ok:
                        st.success(f"Student {n_name} ({n_code}) registered successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error registering student: {msg}")


# ======================================================================================
# 5. ADMIN / WARDEN: AI COMPLAINTS & MAINTENANCE TRIAGE
# ======================================================================================
elif selected_menu == "🛠️ AI Complaints & Triage":
    st.title("🛠️ AI Complaint & Maintenance Intelligence Center")
    st.caption("Zero-delay grievance reporting with instant NLP category classification, sentiment analysis, priority assignment, and maintenance routing.")

    tab_file, tab_active, tab_sandbox = st.tabs(["📝 File a New Complaint", "📋 Live Maintenance Matrix", "🧪 NLP Triage Testbed"])

    with tab_file:
        st.subheader("Submit Maintenance Request")
        with st.form("complaint_submission_form"):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                all_stus = db.fetch_all("SELECT * FROM students")
                stu_names = {f"{s['name']} (Room {s['room_id'] or 'Unassigned'})": s for s in all_stus}
                chosen_stu_key = st.selectbox("Reporting Resident", list(stu_names.keys()))
                chosen_stu = stu_names[chosen_stu_key]
                room_no = st.text_input("Room / Location", value=f"Room {chosen_stu['room_id']}" if chosen_stu['room_id'] else "Main Corridor")
            
            with c_col2:
                complaint_title = st.text_input("Issue Headline / Title", placeholder="e.g. Broken water tap in bathroom")

            complaint_desc = st.text_area("Detailed Problem Description (Natural Language)", placeholder="Describe the issue in your own words. The AI engine will parse urgency, category, and dispatch details automatically.", height=120)

            submit_comp = st.form_submit_button("🚀 Run AI Triage & Submit Ticket")

            if submit_comp:
                if not complaint_desc.strip():
                    st.warning("Please provide a description of the issue.")
                else:
                    ai_res = ai.analyze_complaint(complaint_desc)
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                    cid = db.execute_query("""
                    INSERT INTO complaints (student_id, student_name, room_number, category, title, description, priority, sentiment, status, department, suggested_action, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?)
                    """, (chosen_stu['id'], chosen_stu['name'], room_no, ai_res['category'], complaint_title or ai_res['summary'], complaint_desc, ai_res['priority'], ai_res['sentiment'], ai_res['department'], ai_res['suggested_action'], now_str))

                    st.success(f"🎉 Complaint #{cid} successfully submitted and triaged by AI!")
                    st.json(ai_res)

    with tab_active:
        st.subheader("📋 Maintenance Ticket Management")
        all_comp = db.fetch_all("SELECT * FROM complaints ORDER BY id DESC")
        
        for c in all_comp:
            p_badge = "badge-urgent" if c["priority"] == "URGENT" else ("badge-high" if c["priority"] == "HIGH" else "badge-info")
            s_badge = "badge-success" if c["status"] == "RESOLVED" else ("badge-info" if c["status"] == "IN_PROGRESS" else "badge-urgent")

            with st.container():
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin-bottom: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin: 0; color: #1e293b;">#{c['id']} - {c['title']}</h4>
                        <div>
                            <span class="{p_badge}">{c['priority']} Priority</span>
                            <span class="{s_badge}">{c['status']}</span>
                        </div>
                    </div>
                    <div style="font-size: 0.85rem; color: #64748b; margin: 6px 0;">
                        👤 {c['student_name']} • 🚪 {c['room_number']} • 🏷️ <strong>Category:</strong> {c['category']} • 🏢 <strong>Dept:</strong> {c['department']} • 🕒 {c['created_at']}
                    </div>
                    <p style="font-size: 0.9rem; color: #334155; margin: 8px 0; background: #f8fafc; padding: 10px; border-radius: 8px;">
                        "{c['description']}"
                    </p>
                    <div style="font-size: 0.85rem; color: #0284c7; margin-top: 4px;">
                        🤖 <strong>AI Suggested Action:</strong> {c['suggested_action']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state["user_role"] in ["ADMIN", "WARDEN"] and c["status"] != "RESOLVED":
                    u_col1, u_col2 = st.columns([1, 4])
                    with u_col1:
                        if st.button(f"Mark In-Progress", key=f"inp_{c['id']}"):
                            db.execute_query("UPDATE complaints SET status = 'IN_PROGRESS' WHERE id = ?", (c['id'],))
                            st.rerun()
                    with u_col2:
                        if st.button(f"✅ Mark Resolved", key=f"res_{c['id']}"):
                            db.execute_query("UPDATE complaints SET status = 'RESOLVED', resolved_at = ? WHERE id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M"), c['id']))
                            st.rerun()

    with tab_sandbox:
        st.subheader("🧪 Real-Time NLP Complaint Triage Testbed")
        st.caption("Test how the AI Engine classifies grievances, infers sentiment, detects severity, and assigns technician dispatch protocols.")
        sample_query = st.text_area("Type any grievance statement to test AI:", "The ceiling fan in room A-202 is making loud spark sounds and smelling like burnt plastic, it might catch fire!")
        
        if st.button("⚡ Test NLP Engine"):
            res = ai.analyze_complaint(sample_query)
            st.json(res)


# ======================================================================================
# 6. ADMIN / WARDEN: SMART ATTENDANCE & CURFEW
# ======================================================================================
elif selected_menu == "📅 Smart Attendance & Curfew":
    st.title("📅 Smart Biometric Attendance & Curfew Alerts")
    st.caption("Automated turnstile logging, curfew compliance tracking, and unauthorized absentee detection.")

    today_str = date.today().strftime("%Y-%m-%d")
    att_date = st.date_input("Attendance Date", value=date.today())
    date_str = att_date.strftime("%Y-%m-%d")

    records = db.fetch_all("SELECT * FROM attendance WHERE date = ?", (date_str,))
    
    if not records:
        st.info(f"No attendance records found for {date_str}. Showing latest recorded data.")
        records = db.fetch_all("SELECT * FROM attendance ORDER BY date DESC LIMIT 50")

    p_count = sum(1 for r in records if r["status"] == "PRESENT")
    l_count = sum(1 for r in records if r["status"] == "LATE")
    a_count = sum(1 for r in records if r["status"] == "ABSENT")
    lv_count = sum(1 for r in records if r["status"] == "ON_LEAVE")

    ac1, ac2, ac3, ac4 = st.columns(4)
    with ac1:
        st.markdown(f"""<div class="metric-card"><span style="color:#16a34a; font-weight:600;">PRESENT</span><h2>{p_count}</h2></div>""", unsafe_allow_html=True)
    with ac2:
        st.markdown(f"""<div class="metric-card"><span style="color:#d97706; font-weight:600;">LATE CURFEW</span><h2>{l_count}</h2></div>""", unsafe_allow_html=True)
    with ac3:
        st.markdown(f"""<div class="metric-card"><span style="color:#dc2626; font-weight:600;">ABSENT (UNAUTHORIZED)</span><h2>{a_count}</h2></div>""", unsafe_allow_html=True)
    with ac4:
        st.markdown(f"""<div class="metric-card"><span style="color:#2563eb; font-weight:600;">AUTHORIZED LEAVE</span><h2>{lv_count}</h2></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    df_att = pd.DataFrame(records)
    if not df_att.empty:
        st.dataframe(df_att[['student_id', 'student_name', 'room_number', 'date', 'status', 'check_in_time', 'check_out_time', 'marked_by']], use_container_width=True, hide_index=True)

    if a_count > 0 and st.session_state["user_role"] in ["ADMIN", "WARDEN"]:
        st.warning(f"🚨 {a_count} student(s) marked ABSENT past curfew cutoff.")
        if st.button("📲 Send Automated SMS Notification to Absentee Guardians"):
            st.success("✅ SMS Alerts dispatched to guardians: 'Your ward was not present during mandatory 09:30 PM hostel curfew check.'")

    # ADVANCED BIOMETRIC ANOMALY DETECTOR
    st.markdown("---")
    st.markdown("### 🤖 Biometric Anomaly & Repeat Curfew Risk Forecaster")
    leaves_all = db.fetch_all("SELECT * FROM leave_requests")
    anomaly_insights = ai.analyze_biometric_anomalies(records, leaves_all)

    ano_c1, ano_c2 = st.columns([1, 1.2])
    with ano_c1:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="margin:0; color:#1e293b;">Campus Curfew Threat Status</h4>
                <span class="{'badge-urgent' if anomaly_insights['campus_security_risk'] == 'ELEVATED' else 'badge-success'}">
                    {anomaly_insights['campus_security_risk']} RISK
                </span>
            </div>
            <p style="margin: 8px 0 12px 0; font-size: 0.88rem; color: #64748b;">
                AI pattern analysis cross-references biometric turnstile timestamps against authorized outstation leave databases.
            </p>
            <ul style="margin:0; padding-left:18px; font-size:0.85rem; color:#334155;">
                <li>Total Curfew Anomalies Detected: <b>{anomaly_insights['total_anomalies']}</b></li>
                <li>Late Returns Past 09:30 PM: <b>{anomaly_insights['late_entries_count']}</b></li>
                <li>Unaccounted Missing Absences: <b>{len(anomaly_insights['unaccounted_absences'])}</b></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with ano_c2:
        if anomaly_insights['chronic_late_students']:
            st.markdown("##### ⚠️ Chronic Late Arrivals (>= 2 Incidents)")
            for cl in anomaly_insights['chronic_late_students']:
                st.markdown(f"- 👤 **{cl['student']}** — logged `{cl['count']}` late check-ins this week.")
        else:
            st.success("✨ Zero chronic late arrivals detected. Turnstile discipline adherence is optimal.")


# ======================================================================================
# 7. ADMIN / WARDEN: LEAVE & DIGITAL GATE PASS
# ======================================================================================
elif selected_menu == "✈️ Leave & Digital Gate Pass":
    st.title("✈️ Leave & Digital Gate Pass Management")
    st.caption("Apply for outstation permissions, obtain Warden approvals, and generate digital QR gate passes.")

    tab_apply, tab_approvals, tab_my_passes = st.tabs(["📝 Apply for Outstation Leave", "🛡️ Warden Approvals Desk", "🎫 Active Gate Passes"])

    with tab_apply:
        st.subheader("Submit Outstation / Night-Out Permission")
        with st.form("apply_leave_form"):
            l_stus = db.fetch_all("SELECT * FROM students")
            l_stu_dict = {f"{s['name']} ({s['student_id_code']})": s for s in l_stus}
            sel_l_stu_name = st.selectbox("Student Resident", list(l_stu_dict.keys()))
            cur_l_stu = l_stu_dict[sel_l_stu_name]

            l_c1, l_c2 = st.columns(2)
            with l_c1:
                leave_from = st.date_input("Departure Date", value=date.today())
            with l_c2:
                leave_to = st.date_input("Return Date", value=date.today() + timedelta(days=2))

            leave_reason = st.text_area("Reason for Leave / Outstation Destination", placeholder="e.g. Visiting hometown for family event / Attending inter-college conference.")

            apply_btn = st.form_submit_button("Submit Leave Request")
            if apply_btn:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                db.execute_query("""
                INSERT INTO leave_requests (student_id, student_name, room_number, reason, from_date, to_date, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'PENDING', ?)
                """, (cur_l_stu["id"], cur_l_stu["name"], f"Room {cur_l_stu['room_id'] or 'Unassigned'}", leave_reason, leave_from.strftime("%Y-%m-%d"), leave_to.strftime("%Y-%m-%d"), now_str))
                st.success("Leave request forwarded to Warden for verification!")
                st.rerun()

    with tab_approvals:
        st.subheader("Pending Warden Verifications")
        pending_leaves = db.fetch_all("SELECT * FROM leave_requests WHERE status = 'PENDING' ORDER BY id DESC")
        
        if pending_leaves:
            for pl in pending_leaves:
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                    <div style="display:flex; justify-content:space-between;">
                        <strong>{pl['student_name']} ({pl['room_number']})</strong>
                        <span class="badge-high">PENDING WARDEN APPROVAL</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #64748b; margin: 4px 0;">
                        📅 <strong>Duration:</strong> {pl['from_date']} to {pl['to_date']}
                    </div>
                    <p style="font-size: 0.9rem; color: #334155; margin: 6px 0;"><strong>Reason:</strong> {pl['reason']}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state["user_role"] in ["ADMIN", "WARDEN"]:
                    app_c1, app_c2 = st.columns([1, 4])
                    with app_c1:
                        if st.button(f"✅ Approve", key=f"app_{pl['id']}"):
                            gp_code = f"GP-2026-{random.randint(1000, 9999)}"
                            db.execute_query("UPDATE leave_requests SET status = 'APPROVED', approved_by = ?, gate_pass_code = ? WHERE id = ?", (st.session_state["logged_user"], gp_code, pl["id"]))
                            st.success(f"Leave Approved! Gate pass code issued: {gp_code}")
                            st.rerun()
                    with app_c2:
                        if st.button(f"❌ Reject", key=f"rej_{pl['id']}"):
                            db.execute_query("UPDATE leave_requests SET status = 'REJECTED', approved_by = ? WHERE id = ?", (st.session_state["logged_user"], pl["id"]))
                            st.warning("Leave Rejected.")
                            st.rerun()
        else:
            st.info("No pending leave approvals.")

    with tab_my_passes:
        st.subheader("🎫 Approved Digital Gate Passes")
        approved_passes = db.fetch_all("SELECT * FROM leave_requests WHERE status = 'APPROVED' ORDER BY id DESC")
        
        for p in approved_passes:
            st.markdown(f"""
            <div class="gate-pass-box" style="margin-bottom: 16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin: 0; color: #38bdf8;">🎫 DIGITAL CAMPUS GATE PASS</h3>
                    <span class="badge-success" style="font-size: 0.85rem;">VALID & AUTHORIZED</span>
                </div>
                <hr style="border-color: #334155; margin: 12px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.9rem; flex: 1;">
                        <div>
                            <span style="color: #94a3b8;">Resident Name:</span><br>
                            <strong>{p['student_name']}</strong>
                        </div>
                        <div>
                            <span style="color: #94a3b8;">Gate Pass Ref Code:</span><br>
                            <strong style="color: #facc15; font-family: monospace; font-size: 1.1rem;">{p['gate_pass_code']}</strong>
                        </div>
                        <div>
                            <span style="color: #94a3b8;">Valid From:</span><br>
                            <strong>{p['from_date']}</strong>
                        </div>
                        <div>
                            <span style="color: #94a3b8;">Valid Until:</span><br>
                            <strong>{p['to_date']}</strong>
                        </div>
                    </div>
                    <div style="text-align:center; background:white; padding:8px; border-radius:10px;">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={p['gate_pass_code']}" style="display:block; width:100px; height:100px; border-radius:6px;" alt="QR" />
                        <span style="color:#0f172a; font-size:0.65rem; font-weight:700; font-family:monospace;">SCAN AT GATE</span>
                    </div>
                </div>
                <div style="margin-top: 14px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; font-size: 0.8rem; color: #cbd5e1;">
                    🔒 Approved by {p['approved_by']} • Ready for QR Scan at Main Turnstile Security Gate
                </div>
            </div>
            """, unsafe_allow_html=True)


# ======================================================================================
# 8. ADMIN / WARDEN: MESS & AI WASTE ANALYTICS
# ======================================================================================
elif selected_menu == "🍲 Mess & AI Waste Analytics":
    st.title("🍲 Mess & AI Dining Waste Analytics")
    st.caption("Weekly nutritional meal scheduling and AI-driven meal demand forecasting to eliminate food wastage.")

    tab_menu, tab_ai_forecast = st.tabs(["📅 Weekly Dining Menu", "🧠 AI Food Demand & Waste Forecaster"])

    with tab_menu:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        today_name = datetime.now().strftime("%A")
        sel_day = st.selectbox("Select Day of Week", days, index=days.index(today_name) if today_name in days else 0)

        menu_items = db.fetch_all("SELECT * FROM mess_menu WHERE day_of_week = ?", (sel_day,))
        m_cols = st.columns(4)
        meal_icons = {"Breakfast": "🥞", "Lunch": "🍛", "Snacks": "☕", "Dinner": "🍲"}

        for idx, meal_type in enumerate(["Breakfast", "Lunch", "Snacks", "Dinner"]):
            item = next((m for m in menu_items if m["meal_type"] == meal_type), None)
            with m_cols[idx]:
                if item:
                    st.markdown(f"""
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; height: 100%; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                        <h4 style="margin:0 0 6px 0; color:#1e3c72;">{meal_icons.get(meal_type, '')} {meal_type}</h4>
                        <div style="font-size: 0.85rem; color: #16a34a; font-weight: 600; margin-bottom: 8px;">🔥 {item['calories']} kcal</div>
                        <p style="font-size: 0.85rem; color: #334155; min-height: 50px;">{item['items']}</p>
                        <hr style="border-top: 1px dashed #e2e8f0; margin: 8px 0;">
                        <span style="font-size: 0.75rem; color: #64748b;">✨ Special: <strong>{item['special_item']}</strong></span>
                    </div>
                    """, unsafe_allow_html=True)

    with tab_ai_forecast:
        st.subheader("🧠 Predictive Meal Demand & Food Preparation Engine")
        students_cnt = len(db.fetch_all("SELECT id FROM students"))
        leaves_cnt = len(db.fetch_all("SELECT id FROM leave_requests WHERE status = 'APPROVED'"))
        
        day_for_pred = st.selectbox("Forecast Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="pred_day")
        pred = ai.predict_mess_demand(students_cnt, leaves_cnt, day_for_pred)

        st.markdown(f"""
        <div class="ai-bubble">
            <strong>Hostel Headcount Status:</strong> {students_cnt} Total Enrolled • {leaves_cnt} On Approved Leave • <strong>{pred['active_students']} In-Hostel Diners</strong><br>
            🌱 <strong>AI Waste Reduction:</strong> {pred['waste_reduction_estimate']}
        </div>
        """, unsafe_allow_html=True)

        fc_cols = st.columns(4)
        for idx, (m_name, m_data) in enumerate(pred["meals"].items()):
            with fc_cols[idx]:
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px;">
                    <h4 style="margin: 0; color: #0f172a;">{m_name}</h4>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #2563eb; margin: 6px 0;">
                        {m_data['expected_students']} Diners
                    </div>
                    <div style="font-size: 0.8rem; color: #64748b;">Buffer: {m_data['prepared_capacity']} plates</div>
                    <hr style="margin: 8px 0; border: none; border-top: 1px solid #f1f5f9;">
                    <div style="font-size: 0.82rem; color: #334155; line-height: 1.5;">
                        🍚 <strong>Grain / Flour:</strong> {m_data['grain_kg']} kg<br>
                        🥘 <strong>Curry / Dal:</strong> {m_data['curry_dal_kg']} kg<br>
                        📦 <strong>Total Batch:</strong> {m_data['total_food_kg']} kg
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ======================================================================================
# 9. ADMIN / WARDEN: FEE & RISK DEFAULTERS
# ======================================================================================
elif selected_menu == "💳 Fee & Risk Defaulters":
    st.title("💳 Hostel Fee & Defaulter Risk Analytics")
    st.caption("Monitor semester dues, fee payments, and AI default risk scoring.")

    fee_records = db.fetch_all("SELECT * FROM fee_records")
    analyzed_fees = ai.calculate_defaulter_risk(fee_records)

    total_collected = sum(f["amount_paid"] for f in fee_records)
    total_outstanding = sum(f["amount_due"] for f in fee_records)
    high_risk_count = sum(1 for f in analyzed_fees if f["risk_level"] == "HIGH RISK")

    f1, f2, f3 = st.columns(3)
    with f1:
        st.metric("Total Fees Collected", f"₹{total_collected:,.0f}")
    with f2:
        st.metric("Outstanding Due Balance", f"₹{total_outstanding:,.0f}")
    with f3:
        st.metric("High-Risk Defaulter Accounts", f"{high_risk_count} Students")

    st.markdown("### 🔍 Risk Scored Resident Account Ledger")
    df_fee = pd.DataFrame(analyzed_fees)
    if not df_fee.empty:
        st.dataframe(df_fee[['student_name', 'total_amount', 'amount_paid', 'amount_due', 'due_date', 'days_overdue', 'risk_level', 'risk_score', 'recommended_action']], use_container_width=True, hide_index=True)


# ======================================================================================
# 10. ADMIN / WARDEN: VISITOR LOG & SECURITY
# ======================================================================================
elif selected_menu == "🛡️ Visitor Log & Gate Security":
    st.title("🛡️ Campus Gate Security & Visitor Logging")
    st.caption("Real-time logging of parent/guest entries, exits, and security checkpoint clearance.")

    v1, v2 = st.columns([1, 1.5])
    with v1:
        st.subheader("Log New Visitor Entry")
        with st.form("new_visitor_form"):
            stus = db.fetch_all("SELECT * FROM students")
            s_dict = {f"{s['name']} (Room {s['room_id'] or 'N/A'})": s for s in stus}
            v_stu = st.selectbox("Resident Being Visited", list(s_dict.keys()))
            v_name = st.text_input("Visitor Full Name")
            v_rel = st.selectbox("Relationship", ["Father", "Mother", "Guardian", "Sibling", "Official / Delivery"])
            v_phone = st.text_input("Visitor Phone Number")
            v_purpose = st.text_input("Purpose of Visit", "Family meeting & fee payment")

            if st.form_submit_button("Record Check-In"):
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                s_obj = s_dict[v_stu]
                db.execute_query("""
                INSERT INTO visitors (student_id, student_name, visitor_name, relation, phone, entry_time, purpose, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'IN_PREMISES')
                """, (s_obj["id"], s_obj["name"], v_name, v_rel, v_phone, now_str, v_purpose))
                st.success(f"Visitor {v_name} check-in recorded!")
                st.rerun()

    with v2:
        st.subheader("Active Visitors In Premises")
        active_visitors = db.fetch_all("SELECT * FROM visitors ORDER BY id DESC")
        for v in active_visitors:
            v_badge = "badge-urgent" if v["status"] == "IN_PREMISES" else "badge-success"
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; padding: 14px; border-radius: 10px; margin-bottom: 10px;">
                <div style="display:flex; justify-content:space-between;">
                    <strong>{v['visitor_name']} ({v['relation']})</strong>
                    <span class="{v_badge}">{v['status']}</span>
                </div>
                <div style="font-size: 0.85rem; color: #64748b; margin: 4px 0;">
                    Visiting: <strong>{v['student_name']}</strong> • 📞 {v['phone']}
                </div>
                <div style="font-size: 0.8rem; color: #334155;">
                    🕒 Entered: {v['entry_time']} {f'| Exited: {v["exit_time"]}' if v['exit_time'] else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if v["status"] == "IN_PREMISES" and st.button(f"Mark Check-Out", key=f"v_out_{v['id']}"):
                db.execute_query("UPDATE visitors SET status = 'CHECKED_OUT', exit_time = ? WHERE id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M"), v["id"]))
                st.rerun()


# ======================================================================================
# 11. ADMIN / WARDEN: NOTICE BOARD & BROADCASTS
# ======================================================================================
elif selected_menu == "📢 Notice Board & Broadcasts":
    st.title("📢 Campus Notice Board & Emergency Broadcasts")
    st.caption("Publish administrative circulars, maintenance outages, and emergency SOS alerts.")

    if st.session_state["user_role"] in ["ADMIN", "WARDEN"]:
        with st.expander("➕ Publish New Circular / Notice"):
            with st.form("post_notice_form"):
                n_t = st.text_input("Notice Headline")
                n_c = st.text_area("Detailed Circular Content")
                n_col1, n_col2 = st.columns(2)
                with n_col1:
                    n_cat = st.selectbox("Category", ["General", "Emergency", "Maintenance", "Event", "Mess"])
                with n_col2:
                    n_pri = st.selectbox("Priority Level", ["NORMAL", "HIGH", "URGENT"])

                if st.form_submit_button("📢 Publish Notice"):
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    db.execute_query("""
                    INSERT INTO notices (title, content, category, priority, posted_by, posted_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (n_t, n_c, n_cat, n_pri, st.session_state["logged_user"], now_str))
                    st.success("Notice published live!")
                    st.rerun()

    all_notices = db.fetch_all("SELECT * FROM notices ORDER BY id DESC")
    for n in all_notices:
        p_badge = "badge-urgent" if n["priority"] == "URGENT" else ("badge-high" if n["priority"] == "HIGH" else "badge-info")
        st.markdown(f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3 style="margin: 0; color: #1e3c72; font-size: 1.2rem;">{n['title']}</h3>
                <span class="{p_badge}">{n['priority']}</span>
            </div>
            <div style="font-size: 0.85rem; color: #64748b; margin: 6px 0 12px 0;">
                Category: <strong>{n['category']}</strong> • Audience: <strong>{n['target_audience']}</strong> • Posted by: <strong>{n['posted_by']}</strong> • {n['posted_at']}
            </div>
            <p style="font-size: 0.95rem; color: #334155; line-height: 1.6;">{n['content']}</p>
        </div>
        """, unsafe_allow_html=True)


# ======================================================================================
# 12. STUDENT: MY STUDENT DASHBOARD
# ======================================================================================
elif selected_menu == "🏠 My Student Dashboard":
    sp = st.session_state.get("student_profile", {})
    st.markdown(f"""
    <div class="main-header">
        <div>
            <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700;">Welcome back, {sp.get('name', st.session_state['logged_user'])}!</h1>
            <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 0.95rem;">
                Resident ID: <strong>{sp.get('student_id_code', 'STU')}</strong> • Department of {sp.get('department', 'Engineering')} (Year {sp.get('year', 1)})
            </p>
        </div>
        <div style="text-align: right;">
            <span class="badge-success" style="font-size: 0.85rem; padding: 6px 14px;">Resident Status: Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Student Summary KPIs
    room_info = sp.get("room_details")
    r_num = room_info["room_number"] if room_info else "Pending Allocation"
    h_name = room_info["hostel_name"] if room_info else "Hostel Administration"

    fee_info = sp.get("fee_details") or {}
    due_amt = fee_info.get("amount_due", 0)
    fee_stat = fee_info.get("status", "PAID")

    active_pass = next((l for l in sp.get("leaves", []) if l["status"] == "APPROVED"), None)
    active_complaints_cnt = sum(1 for c in sp.get("complaints", []) if c["status"] != "RESOLVED")

    sk1, sk2, sk3, sk4 = st.columns(4)
    with sk1:
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:0.8rem; color:#64748b; font-weight:600; text-transform:uppercase;">Room Allotment</span>
            <h2 style="margin:8px 0 4px 0; color:#1e3c72; font-size:1.6rem;">{r_num}</h2>
            <span style="font-size:0.8rem; color:#64748b;">{h_name}</span>
        </div>
        """, unsafe_allow_html=True)

    with sk2:
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:0.8rem; color:#64748b; font-weight:600; text-transform:uppercase;">Fee Dues</span>
            <h2 style="margin:8px 0 4px 0; color:{'#16a34a' if due_amt == 0 else '#dc2626'}; font-size:1.6rem;">₹{due_amt:,.0f}</h2>
            <span class="{'badge-success' if due_amt == 0 else 'badge-urgent'}">{fee_stat}</span>
        </div>
        """, unsafe_allow_html=True)

    with sk3:
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:0.8rem; color:#64748b; font-weight:600; text-transform:uppercase;">Active Gate Pass</span>
            <h2 style="margin:8px 0 4px 0; color:#0284c7; font-size:1.4rem;">{active_pass['gate_pass_code'] if active_pass else 'None'}</h2>
            <span style="font-size:0.8rem; color:#64748b;">{'Valid for Outstation' if active_pass else 'On Campus'}</span>
        </div>
        """, unsafe_allow_html=True)

    with sk4:
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:0.8rem; color:#64748b; font-weight:600; text-transform:uppercase;">Open Grievances</span>
            <h2 style="margin:8px 0 4px 0; color:#f59e0b; font-size:1.6rem;">{active_complaints_cnt}</h2>
            <span style="font-size:0.8rem; color:#64748b;">Maintenance tickets</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 🎙️ ADVANCED VOICE AI ASSISTANT & EMERGENCY SOS BANNER FOR STUDENT
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 16px; padding: 18px 24px; color: white; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:48px; height:48px; border-radius:50%; background:#6366f1; display:flex; align-items:center; justify-content:center; font-size:1.5rem; box-shadow:0 0 20px rgba(99,102,241,0.6);">
                    🎙️
                </div>
                <div>
                    <h4 style="margin:0; color:#e0e7ff; font-size:1.15rem;">SmartHostel Voice Assistant Active</h4>
                    <p style="margin:2px 0 0 0; font-size:0.85rem; color:#a5b4fc;">
                        Hands-free voice queries, instant meal menus, maintenance dispatch, and emergency SOS alerts.
                    </p>
                </div>
            </div>
            <div>
                <span class="badge-success" style="font-size:0.8rem;">● AI Voice Engine Online</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Voice Trigger Buttons for Student
    v_st_c1, v_st_c2, v_st_c3, v_st_c4, v_st_c5 = st.columns(5)
    stu_ctx = {
        "user_role": "STUDENT",
        "logged_user": sp.get("name", st.session_state["logged_user"]),
        "student_profile": sp
    }

    with v_st_c1:
        if st.button("🍲 Dinner Menu", use_container_width=True, key="stu_v_dinner"):
            v_res = ai.parse_voice_command("What is for dinner tonight?", user_context=stu_ctx)
            st.session_state["last_voice_result"] = v_res
            st.info(f"🗣️ AI: \"{v_res['spoken_text']}\"")
    with v_st_c2:
        if st.button("🚪 My Roommates", use_container_width=True, key="stu_v_rm"):
            v_res = ai.parse_voice_command("Who are my roommates?", user_context=stu_ctx)
            st.session_state["last_voice_result"] = v_res
            st.info(f"🗣️ AI: \"{v_res['spoken_text']}\"")
    with v_st_c3:
        if st.button("🕒 Curfew Rule", use_container_width=True, key="stu_v_curfew"):
            v_res = ai.parse_voice_command("When does the gate close?", user_context=stu_ctx)
            st.session_state["last_voice_result"] = v_res
            st.info(f"🗣️ AI: \"{v_res['spoken_text']}\"")
    with v_st_c4:
        if st.button("💳 Fee Balance", use_container_width=True, key="stu_v_fee"):
            v_res = ai.parse_voice_command("Check my fee balance", user_context=stu_ctx)
            st.session_state["last_voice_result"] = v_res
            st.info(f"🗣️ AI: \"{v_res['spoken_text']}\"")
    with v_st_c5:
        if st.button("🚨 VOICE SOS PANIC", type="primary", use_container_width=True, key="stu_v_sos"):
            v_res = ai.parse_voice_command("EMERGENCY SOS: Immediate help needed!", user_context=stu_ctx)
            st.session_state["last_voice_result"] = v_res
            st.session_state["emergency_sos_alert"] = True
            st.rerun()

    if st.session_state.get("emergency_sos_alert"):
        st.error("🚨 **EMERGENCY SOS DISPATCH TRIGGERED!** Chief Warden (+91 98765 43210) & Security Gate (+91 98765 00100) have received your alert with your room coordinates.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Active Pass QR Spotlight if approved
    if active_pass:
        st.markdown(f"""
        <div class="gate-pass-box" style="margin-bottom: 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3 style="margin:0; color:#38bdf8;">🎫 Your Active Digital Gate Pass</h3>
                <span class="badge-success">AUTHORIZED BY WARDEN</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px; flex-wrap:wrap; gap:16px;">
                <div>
                    <strong>Pass Code:</strong> <span style="color:#facc15; font-family:monospace; font-size:1.2rem;">{active_pass['gate_pass_code']}</span><br>
                    <strong>Valid Dates:</strong> {active_pass['from_date']} to {active_pass['to_date']}<br>
                    <strong>Reason:</strong> {active_pass['reason']}
                </div>
                <div style="background:white; padding:6px; border-radius:8px; text-align:center;">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=90x90&data={active_pass['gate_pass_code']}" style="width:90px; height:90px;" alt="QR" />
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Roommates & Lifestyle Card
    row_c1, row_c2 = st.columns([1.2, 1])
    with row_c1:
        st.subheader("🚪 Room Details & Roommates")
        if room_info:
            st.markdown(f"""
            <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:18px;">
                <h4 style="margin:0 0 6px 0; color:#1e3c72;">Room {room_info['room_number']} ({room_info['hostel_name']} - {room_info['block_name']})</h4>
                <div style="font-size:0.88rem; color:#475569; margin-bottom:10px;">
                    ✨ Amenities: {room_info['amenities'] or 'Standard'} • Capacity: {room_info['capacity']} Beds • Floor: {room_info['floor_number']}
                </div>
                <hr style="margin:10px 0; border:none; border-top:1px solid #f1f5f9;">
                <strong>Roommates:</strong>
            """, unsafe_allow_html=True)
            roommates = sp.get("roommates", [])
            if roommates:
                for rm in roommates:
                    st.markdown(f"- 👤 **{rm['name']}** (Year {rm['year']} {rm['department']}) • 📞 {rm['phone']}")
            else:
                st.info("You currently have single occupancy or roommates are not yet allocated.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("You are not yet allocated to a room. The Chief Administrator will assign you shortly using the AI Room Matcher.")

    with row_c2:
        st.subheader("📢 Latest Hostel Notice")
        top_notice = db.fetch_one("SELECT * FROM notices ORDER BY id DESC LIMIT 1")
        if top_notice:
            st.markdown(f"""
            <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:18px;">
                <span class="badge-info">{top_notice['category']}</span>
                <h4 style="margin:8px 0 4px 0; color:#1e293b;">{top_notice['title']}</h4>
                <p style="font-size:0.88rem; color:#475569; margin:6px 0;">{top_notice['content']}</p>
                <div style="font-size:0.75rem; color:#94a3b8;">Posted by {top_notice['posted_by']} • {top_notice['posted_at']}</div>
            </div>
            """, unsafe_allow_html=True)


# ======================================================================================
# 13. STUDENT: MY ROOM & ROOMMATES
# ======================================================================================
elif selected_menu == "🚪 My Room & Roommates":
    sp = st.session_state.get("student_profile", {})
    st.title("🚪 My Room & Resident Roommates")
    st.caption("View your assigned room specifications, amenities, and roommate compatibility.")

    room_info = sp.get("room_details")
    if room_info:
        r1, r2 = st.columns([1, 1.2])
        with r1:
            st.markdown(f"""
            <div style="background:white; border:1px solid #e2e8f0; border-radius:14px; padding:20px; box-shadow:0 4px 12px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 style="margin:0; color:#1e3c72;">Room {room_info['room_number']}</h2>
                    <span class="badge-info">{room_info['room_type']} Room</span>
                </div>
                <div style="font-size:0.9rem; color:#64748b; margin:6px 0 14px 0;">
                    {room_info['hostel_name']} • {room_info['block_name']} • Floor {room_info['floor_number']}
                </div>
                <hr style="margin:10px 0; border:none; border-top:1px solid #f1f5f9;">
                <div style="font-size:0.9rem; line-height:1.7; color:#334155;">
                    🛏️ <strong>Beds:</strong> {room_info['occupied_beds']} / {room_info['capacity']} Occupied<br>
                    💵 <strong>Monthly Rent:</strong> ₹{room_info['rent_per_month']:,.0f}<br>
                    ✨ <strong>Amenities:</strong> {room_info['amenities'] or 'Standard'}<br>
                    🛡️ <strong>Hostel Warden:</strong> Dr. Rajesh Sharma (+91 98765 43210)
                </div>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            st.subheader("👥 Your Roommates")
            roommates = sp.get("roommates", [])
            if roommates:
                for rm in roommates:
                    st.markdown(f"""
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:16px; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between;">
                            <strong>👤 {rm['name']}</strong>
                            <span class="badge-success">Resident</span>
                        </div>
                        <div style="font-size:0.85rem; color:#64748b; margin-top:4px;">
                            🆔 {rm.get('student_id_code', 'STU')} • {rm['department']} (Year {rm['year']})<br>
                            📞 Phone: {rm['phone']} • ✉️ {rm.get('email', 'N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No roommates assigned yet.")
    else:
        st.warning("You currently do not have a room assigned. Please contact the Hostel Warden office or check back once the AI allocator runs.")


# ======================================================================================
# 14. STUDENT: APPLY LEAVE & ACTIVE GATE PASS
# ======================================================================================
elif selected_menu == "✈️ Apply Leave & Active Gate Pass":
    sp = st.session_state.get("student_profile", {})
    st.title("✈️ Outstation Leave & Digital QR Gate Pass")
    st.caption("Apply for leave, track warden approvals in real time, and present your encrypted QR code at security checkpoints.")

    tab_my_reqs, tab_new_req = st.tabs(["🎫 My Gate Passes & Requests", "📝 Submit New Leave Application"])

    with tab_new_req:
        st.subheader("Submit Outstation / Weekend Permission")
        with st.form("stu_apply_leave"):
            st.text_input("Resident Full Name", value=sp.get("name", st.session_state["logged_user"]), disabled=True)
            st.text_input("Student Roll Code", value=sp.get("student_id_code", "STU"), disabled=True)

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                leave_from = st.date_input("Departure Date", value=date.today())
            with col_d2:
                leave_to = st.date_input("Return Date", value=date.today() + timedelta(days=2))

            leave_reason = st.text_area("Reason & Destination for Outstation Leave", placeholder="e.g. Visiting parents in Pune / Attending technical symposium at IIT Bombay")

            if st.form_submit_button("🚀 Submit for Warden Approval", use_container_width=True):
                if not leave_reason.strip():
                    st.warning("Please provide a reason for the leave.")
                else:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    r_no = f"Room {sp.get('room_details', {}).get('room_number', 'Unassigned')}" if sp.get("room_details") else "Unassigned"
                    db.execute_query("""
                    INSERT INTO leave_requests (student_id, student_name, room_number, reason, from_date, to_date, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'PENDING', ?)
                    """, (sp.get("id"), sp.get("name", st.session_state["logged_user"]), r_no, leave_reason, leave_from.strftime("%Y-%m-%d"), leave_to.strftime("%Y-%m-%d"), now_str))
                    st.success("🎉 Leave application submitted! Your Warden will review and issue your digital QR pass.")
                    st.rerun()

    with tab_my_reqs:
        st.subheader("My Past & Active Leave Requests")
        my_leaves = db.fetch_all("SELECT * FROM leave_requests WHERE student_id = ? ORDER BY id DESC", (sp.get("id"),))
        
        if my_leaves:
            for pl in my_leaves:
                if pl["status"] == "APPROVED":
                    st.markdown(f"""
                    <div class="gate-pass-box" style="margin-bottom:16px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="margin:0; color:#38bdf8;">🎫 ACTIVE GATE PASS: {pl['gate_pass_code']}</h3>
                            <span class="badge-success">APPROVED</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:12px; flex-wrap:wrap; gap:16px;">
                            <div style="font-size:0.9rem;">
                                📅 <strong>Valid:</strong> {pl['from_date']} to {pl['to_date']}<br>
                                🎯 <strong>Reason:</strong> {pl['reason']}<br>
                                🔒 <strong>Approved By:</strong> {pl['approved_by']}
                            </div>
                            <div style="background:white; padding:6px; border-radius:8px;">
                                <img src="https://api.qrserver.com/v1/create-qr-code/?size=90x90&data={pl['gate_pass_code']}" style="width:90px; height:90px;" alt="QR" />
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st_badge = "badge-high" if pl["status"] == "PENDING" else "badge-urgent"
                    st.markdown(f"""
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:16px; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between;">
                            <strong>📅 {pl['from_date']} to {pl['to_date']}</strong>
                            <span class="{st_badge}">{pl['status']}</span>
                        </div>
                        <div style="font-size:0.88rem; color:#475569; margin-top:4px;">
                            Reason: {pl['reason']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("You haven't submitted any leave requests yet.")


# ======================================================================================
# 15. STUDENT: FILE & TRACK COMPLAINTS (AI TRIAGE)
# ======================================================================================
elif selected_menu == "🛠️ File & Track Complaints (AI Triage)":
    sp = st.session_state.get("student_profile", {})
    st.title("🛠️ Resident Grievance & Maintenance Center")
    st.caption("Submit maintenance tickets in natural language. The AI triage engine automatically assigns priority, category, and maintenance routing.")

    tab_my_c, tab_new_c = st.tabs(["📋 My Submitted Complaints", "📝 File New Complaint"])

    with tab_new_c:
        st.subheader("Report a Facility or Room Maintenance Issue")
        with st.form("stu_file_complaint"):
            r_no = sp.get("room_details", {}).get("room_number", "Room Corridor") if sp.get("room_details") else "Main Corridor"
            st.text_input("Your Room / Location", value=r_no, disabled=True)
            c_title = st.text_input("Headline / Brief Title", placeholder="e.g. Geyser in bathroom not heating water")
            c_desc = st.text_area("Detailed Problem Description (Natural Language)", placeholder="Describe what is broken or not working. The AI engine will parse urgency and dispatch technicians.", height=120)

            if st.form_submit_button("🚀 Run AI Triage & Submit Grievance", use_container_width=True):
                if not c_desc.strip():
                    st.warning("Please provide a description of the grievance.")
                else:
                    ai_res = ai.analyze_complaint(c_desc)
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                    cid = db.execute_query("""
                    INSERT INTO complaints (student_id, student_name, room_number, category, title, description, priority, sentiment, status, department, suggested_action, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?)
                    """, (sp.get("id"), sp.get("name", st.session_state["logged_user"]), r_no, ai_res['category'], c_title or ai_res['summary'], c_desc, ai_res['priority'], ai_res['sentiment'], ai_res['department'], ai_res['suggested_action'], now_str))

                    st.success(f"🎉 Ticket #{cid} submitted! Categorized by AI as '{ai_res['category']}' with '{ai_res['priority']}' priority.")
                    st.rerun()

    with tab_my_c:
        st.subheader("Your Grievance History")
        my_comps = db.fetch_all("SELECT * FROM complaints WHERE student_id = ? ORDER BY id DESC", (sp.get("id"),))

        if my_comps:
            for c in my_comps:
                p_badge = "badge-urgent" if c["priority"] == "URGENT" else ("badge-high" if c["priority"] == "HIGH" else "badge-info")
                s_badge = "badge-success" if c["status"] == "RESOLVED" else ("badge-info" if c["status"] == "IN_PROGRESS" else "badge-urgent")

                st.markdown(f"""
                <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:16px; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#1e293b;">#{c['id']} - {c['title']}</h4>
                        <div>
                            <span class="{p_badge}">{c['priority']}</span>
                            <span class="{s_badge}">{c['status']}</span>
                        </div>
                    </div>
                    <div style="font-size:0.85rem; color:#64748b; margin:4px 0;">
                        🏷️ Category: <strong>{c['category']}</strong> • 🕒 Filed on {c['created_at']}
                    </div>
                    <p style="font-size:0.9rem; color:#334155; margin:6px 0; background:#f8fafc; padding:8px 12px; border-radius:8px;">
                        "{c['description']}"
                    </p>
                    <div style="font-size:0.82rem; color:#0284c7;">
                        🤖 <strong>AI Action Note:</strong> {c['suggested_action']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("You haven't filed any maintenance complaints.")


# ======================================================================================
# 16. STUDENT: MESS MENU & DAILY SCHEDULE
# ======================================================================================
elif selected_menu == "🍲 Mess Menu & Daily Schedule":
    st.title("🍲 Campus Dining & Daily Mess Menu")
    st.caption("View nutritional meal schedules, specials, and calorie counts for the week.")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    today_name = datetime.now().strftime("%A")
    sel_day = st.selectbox("Select Day of Week", days, index=days.index(today_name) if today_name in days else 0)

    menu_items = db.fetch_all("SELECT * FROM mess_menu WHERE day_of_week = ?", (sel_day,))
    m_cols = st.columns(4)
    meal_icons = {"Breakfast": "🥞", "Lunch": "🍛", "Snacks": "☕", "Dinner": "🍲"}

    for idx, meal_type in enumerate(["Breakfast", "Lunch", "Snacks", "Dinner"]):
        item = next((m for m in menu_items if m["meal_type"] == meal_type), None)
        with m_cols[idx]:
            if item:
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; height: 100%; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                    <h4 style="margin:0 0 6px 0; color:#1e3c72;">{meal_icons.get(meal_type, '')} {meal_type}</h4>
                    <div style="font-size: 0.85rem; color: #16a34a; font-weight: 600; margin-bottom: 8px;">🔥 {item['calories']} kcal</div>
                    <p style="font-size: 0.85rem; color: #334155; min-height: 50px;">{item['items']}</p>
                    <hr style="border-top: 1px dashed #e2e8f0; margin: 8px 0;">
                    <span style="font-size: 0.75rem; color: #64748b;">✨ Special: <strong>{item['special_item']}</strong></span>
                </div>
                """, unsafe_allow_html=True)


# ======================================================================================
# 17. STUDENT: MY FEE STATUS & RECEIPTS
# ======================================================================================
elif selected_menu == "💳 My Fee Status & Receipts":
    sp = st.session_state.get("student_profile", {})
    st.title("💳 Hostel Fee Status & Payment Ledger")
    st.caption("Review your semester hostel fees, payments, dues, and transaction receipts.")

    fee_info = sp.get("fee_details")
    if fee_info:
        fk1, fk2, fk3 = st.columns(3)
        with fk1:
            st.metric("Total Semester Fee", f"₹{fee_info['total_amount']:,.0f}")
        with fk2:
            st.metric("Amount Paid", f"₹{fee_info['amount_paid']:,.0f}")
        with fk3:
            st.metric("Due Balance", f"₹{fee_info['amount_due']:,.0f}")

        st.markdown(f"""
        <div style="background:white; border:1px solid #e2e8f0; border-radius:14px; padding:20px; margin-top:16px;">
            <h4 style="margin:0 0 10px 0; color:#1e3c72;">Receipt & Payment Details</h4>
            <table style="width:100%; font-size:0.9rem; color:#334155; line-height:2;">
                <tr><td><strong>Account Status:</strong></td><td><span class="{'badge-success' if fee_info['amount_due'] == 0 else 'badge-urgent'}">{fee_info['status']}</span></td></tr>
                <tr><td><strong>Due Date:</strong></td><td>{fee_info['due_date']}</td></tr>
                <tr><td><strong>Last Payment Date:</strong></td><td>{fee_info['last_payment_date'] or 'N/A'}</td></tr>
                <tr><td><strong>Transaction Ref:</strong></td><td><code>{fee_info['transaction_ref'] or 'N/A'}</code></td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No fee record found for your account.")


# ======================================================================================
# 18. STUDENT / SECURITY: CAMPUS NOTICES & CIRCULARS
# ======================================================================================
elif selected_menu in ["📢 Campus Notices & Circulars", "📢 Campus Emergency Broadcasts"]:
    st.title("📢 Campus Notices & Administrative Circulars")
    st.caption("Official hostel circulars, emergency announcements, and mess updates.")

    all_notices = db.fetch_all("SELECT * FROM notices ORDER BY id DESC")
    for n in all_notices:
        p_badge = "badge-urgent" if n["priority"] == "URGENT" else ("badge-high" if n["priority"] == "HIGH" else "badge-info")
        st.markdown(f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3 style="margin: 0; color: #1e3c72; font-size: 1.2rem;">{n['title']}</h3>
                <span class="{p_badge}">{n['priority']}</span>
            </div>
            <div style="font-size: 0.85rem; color: #64748b; margin: 6px 0 12px 0;">
                Category: <strong>{n['category']}</strong> • Audience: <strong>{n['target_audience']}</strong> • Posted by: <strong>{n['posted_by']}</strong> • {n['posted_at']}
            </div>
            <p style="font-size: 0.95rem; color: #334155; line-height: 1.6;">{n['content']}</p>
        </div>
        """, unsafe_allow_html=True)


# ======================================================================================
# 19. SECURITY: GATE PASS QR SCANNER & VERIFIER
# ======================================================================================
elif selected_menu == "🎫 Gate Pass QR Scanner & Verifier":
    st.title("🎫 Security Gate Turnstile Pass Verification")
    st.caption("Verify digital QR gate passes and record student check-out / check-in events.")

    sc1, sc2 = st.columns([1, 1.2])
    with sc1:
        st.subheader("Manual / Barcode Scanner Input")
        pass_code_input = st.text_input("Enter Gate Pass Code (e.g. GP-2026-9812)", placeholder="GP-2026-xxxx")
        
        if st.button("🔍 Verify Gate Pass Authenticity", use_container_width=True):
            if pass_code_input.strip():
                match = db.fetch_one("SELECT * FROM leave_requests WHERE UPPER(gate_pass_code) = ?", (pass_code_input.strip().upper(),))
                if match:
                    if match["status"] == "APPROVED":
                        st.success(f"✅ PASS VALID: {match['student_name']} is authorized to exit from {match['from_date']} to {match['to_date']}.")
                    else:
                        st.error(f"❌ PASS INVALID: Status is {match['status']}.")
                else:
                    st.error("❌ Invalid Gate Pass Code: No matching record found in database.")

    with sc2:
        st.subheader("Recent Approved Gate Passes")
        recent_p = db.fetch_all("SELECT * FROM leave_requests WHERE status = 'APPROVED' ORDER BY id DESC LIMIT 5")
        for rp in recent_p:
            st.markdown(f"- 🎫 **{rp['gate_pass_code']}**: {rp['student_name']} ({rp['room_number']}) — Valid until {rp['to_date']}")


# ======================================================================================
# 20. SECURITY: CURFEW & NIGHT CHECK-IN LOG
# ======================================================================================
elif selected_menu == "📅 Curfew & Night Check-In Log":
    st.title("📅 Night Curfew & Biometric Check-In Turnstile")
    st.caption("Monitor night entries past 09:30 PM curfew and log turnstile biometric punches.")

    records = db.fetch_all("SELECT * FROM attendance ORDER BY id DESC LIMIT 50")
    df_att = pd.DataFrame(records)
    if not df_att.empty:
        st.dataframe(df_att[['student_id', 'student_name', 'room_number', 'date', 'status', 'check_in_time', 'check_out_time', 'marked_by']], use_container_width=True, hide_index=True)


# ======================================================================================
# 21. SECURITY: VISITOR ENTRY & CHECK-OUT REGISTRY
# ======================================================================================
elif selected_menu == "🛡️ Visitor Entry & Check-Out Registry":
    st.title("🛡️ Campus Security Visitor In/Out Log")
    st.caption("Record and verify external guest visits, deliveries, and parent meetings.")

    v_all = db.fetch_all("SELECT * FROM visitors ORDER BY id DESC")
    for v in v_all:
        v_badge = "badge-urgent" if v["status"] == "IN_PREMISES" else "badge-success"
        st.markdown(f"""
        <div style="background: white; border: 1px solid #e2e8f0; padding: 14px; border-radius: 10px; margin-bottom: 10px;">
            <div style="display:flex; justify-content:space-between;">
                <strong>{v['visitor_name']} ({v['relation']})</strong>
                <span class="{v_badge}">{v['status']}</span>
            </div>
            <div style="font-size: 0.85rem; color: #64748b; margin: 4px 0;">
                Visiting: <strong>{v['student_name']}</strong> • 📞 {v['phone']}
            </div>
            <div style="font-size: 0.8rem; color: #334155;">
                🕒 Entered: {v['entry_time']} {f'| Exited: {v["exit_time"]}' if v['exit_time'] else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if v["status"] == "IN_PREMISES" and st.button(f"Mark Check-Out", key=f"sec_v_out_{v['id']}"):
            db.execute_query("UPDATE visitors SET status = 'CHECKED_OUT', exit_time = ? WHERE id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M"), v["id"]))
            st.rerun()


# ======================================================================================
# 22. ADVANCED AI HOSTEL ASSISTANT (CHATBOT)
# ======================================================================================
elif selected_menu == "🤖 AI Hostel Assistant (Chatbot)":
    st.markdown("""
    <div class="main-header">
        <div>
            <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700;">🤖 24x7 Intelligent Campus AI Assistant</h1>
            <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 0.95rem;">
                Autonomous RAG Engine grounded in real-time hostel databases, room pairings, gate passes, and mess schedules.
            </p>
        </div>
        <div style="text-align: right;">
            <span class="badge-success" style="font-size: 0.85rem; padding: 6px 14px;">🟢 Real-Time Database Grounded</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Optional AI Engine Configuration Expander
    with st.expander("⚙️ Advanced AI Engine & Provider Configuration (Optional LLM Integration)"):
        cfg_c1, cfg_c2, cfg_c3 = st.columns(3)
        with cfg_c1:
            custom_provider_url = st.text_input(
                "OpenAI-Compatible / Gemini API URL", 
                value=os.environ.get("AI_PROVIDER_URL", ""),
                placeholder="https://api.openai.com/v1/chat/completions"
            )
        with cfg_c2:
            custom_api_key = st.text_input(
                "API Key (Never hard-coded)", 
                value=os.environ.get("AI_API_KEY", ""),
                type="password",
                placeholder="sk-..."
            )
        with cfg_c3:
            custom_model = st.text_input(
                "Model Identifier", 
                value=os.environ.get("AI_MODEL", "gpt-4o-mini"),
                placeholder="gpt-4o-mini / gemini-1.5-flash / llama-3.3-70b"
            )

        st.caption("💡 *If no external API is configured, the assistant seamlessly runs on the local Autonomous Domain RAG Engine with 0% latency.*")

    # Interactive Quick-Prompt Suggestion Pills based on user role
    st.markdown("**⚡ Quick Prompts & Grounded Query Actions:**")
    u_role = st.session_state.get("user_role", "STUDENT")
    quick_query = None
    
    if u_role == "STUDENT":
        q_col1, q_col2, q_col3, q_col4 = st.columns(4)

        with q_col1:
            if st.button("🍲 Sunday Dum Biryani", use_container_width=True):
                quick_query = "What is on the mess menu for Sunday lunch?"
            if st.button("🚪 My Room & Roommates", use_container_width=True):
                quick_query = "Who are my roommates and what are my room details?"

        with q_col2:
            if st.button("💳 My Fee Statement", use_container_width=True):
                quick_query = "What is my fee payment status and due balance?"
            if st.button("✈️ Active Gate Pass", use_container_width=True):
                quick_query = "What is the status of my latest leave request and gate pass?"

        with q_col3:
            if st.button("📢 Latest Notices", use_container_width=True):
                quick_query = "Show me the latest campus hostel notices and circulars."
            if st.button("🕒 Curfew Rules (09:30 PM)", use_container_width=True):
                quick_query = "What are the night curfew hours and late entry rules?"

        with q_col4:
            if st.button("🚨 Emergency Directory", use_container_width=True):
                quick_query = "Give me emergency contacts for Warden, Security, and Campus Medical Centre."
            if st.button("🧹 Clear Chat History", use_container_width=True):
                st.session_state["chat_history"] = [
                    {"role": "assistant", "content": "👋 Chat history cleared. How can I help you today?"}
                ]
                st.rerun()

    else: # ADMIN, WARDEN, SECURITY
        q_col1, q_col2, q_col3, q_col4 = st.columns(4)

        with q_col1:
            if st.button("📊 Real-Time Campus Stats", use_container_width=True):
                quick_query = "Give me an overview of hostel stats, occupancy, and open complaints."
            if st.button("⚠️ Outstanding Fee Defaulters", use_container_width=True):
                quick_query = "Who has overdue fees and unpaid semester balances?"

        with q_col2:
            if st.button("🏢 Search Room A-101", use_container_width=True):
                quick_query = "Who is in room A-101 and what are the room features?"
            if st.button("🎓 Student STU-1041 Profile", use_container_width=True):
                quick_query = "Tell me about student STU-1041"

        with q_col3:
            if st.button("📢 Campus Notices Board", use_container_width=True):
                quick_query = "Show me the latest campus hostel notices."
            if st.button("✈️ Students On Leave", use_container_width=True):
                quick_query = "How many students are currently on approved outstation leave?"

        with q_col4:
            if st.button("🍲 Full Dining Menu", use_container_width=True):
                quick_query = "What is the complete mess menu for today?"
            if st.button("🧹 Clear Chat History", use_container_width=True):
                st.session_state["chat_history"] = [
                    {"role": "assistant", "content": "👋 Chat history cleared. How can I help you today?"}
                ]
                st.rerun()

    # Helpful prompt syntax guide
    with st.expander("💡 Natural Language Query Examples (Grounded Database Actions)"):
        st.markdown("""
        - 🔍 **Room Lookup:** *"Who is in room G-102?"* or *"Tell me about room R-101"*
        - 👨‍🎓 **Student Search:** *"Tell me about student STU-1006"* or *"Show profile for Aarav Sharma"*
        - 🍲 **Mess Meals:** *"What is for lunch on Wednesday?"* or *"Friday dinner special item"*
        - 💳 **Fee Analysis:** *"Show me fee defaulters"* or *"Who has not paid fees?"*
        - 🛠️ **Direct Ticket Creation:** Type `Report issue: Exhaust fan making loud noise in room A-202`
        - 🚨 **Emergencies:** *"Medical emergency contacts"* or *"Warden phone numbers"*
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Process Quick Query if clicked
    if quick_query:
        st.session_state["chat_history"].append({"role": "user", "content": quick_query})
        user_ctx = {
            "user_role": st.session_state.get("user_role", "STUDENT"),
            "logged_user": st.session_state.get("logged_user", "Resident"),
            "student_profile": st.session_state.get("student_profile", {})
        }
        ai_reply = ai.generate_chat_response(
            quick_query, 
            user_context=user_ctx,
            api_url=custom_provider_url,
            api_key=custom_api_key,
            model_name=custom_model
        )
        audio_url = ai.generate_tts_base64_audio_url(ai.clean_text_for_speech(ai_reply))
        st.session_state["chat_history"].append({"role": "assistant", "content": ai_reply, "audio_url": audio_url})
        st.rerun()

    # Voice Mode Switcher & Controls inside Chatbot
    c_voice_c1, c_voice_c2 = st.columns([1.5, 1])
    with c_voice_c1:
        enable_chat_voice = st.toggle("🔊 Spoken Voice Responses (TTS Audio)", value=True, help="Automatically synthesize voice audio for AI responses.")
    with c_voice_c2:
        st.caption("🎙️ *For hands-free speech recognition and SOS alerts, visit the **Voice AI Command Center** tab.*")

    # Display Chat Timeline
    for idx, msg in enumerate(st.session_state["chat_history"]):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("audio_url"):
                st.markdown(f"""
                <audio controls style="height: 32px; width: 220px; margin-top: 6px;">
                    <source src="{msg['audio_url']}" type="audio/mp3">
                </audio>
                """, unsafe_allow_html=True)

    # Natural Language Chat Input
    if prompt := st.chat_input("Ask a question (e.g. 'What is today's dinner?', 'Who is my roommate?', 'Report issue: Tap leaking in bathroom')..."):
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        user_ctx = {
            "user_role": st.session_state.get("user_role", "STUDENT"),
            "logged_user": st.session_state.get("logged_user", "Resident"),
            "student_profile": st.session_state.get("student_profile", {})
        }

        with st.spinner("AI Assistant is retrieving campus records..."):
            ai_reply = ai.generate_chat_response(
                prompt,
                user_context=user_ctx,
                api_url=custom_provider_url,
                api_key=custom_api_key,
                model_name=custom_model
            )
        
        audio_url = ""
        if enable_chat_voice:
            clean_speech = ai.clean_text_for_speech(ai_reply)
            audio_url = ai.generate_tts_base64_audio_url(clean_speech)

        st.session_state["chat_history"].append({
            "role": "assistant", 
            "content": ai_reply,
            "audio_url": audio_url
        })
        with st.chat_message("assistant"):
            st.markdown(ai_reply)
            if audio_url:
                st.markdown(f"""
                <audio controls autoplay style="height: 32px; width: 220px; margin-top: 6px;">
                    <source src="{audio_url}" type="audio/mp3">
                </audio>
                """, unsafe_allow_html=True)


