"""
Advanced AI-Based Hostel Management System - Streamlit Dashboard & Web Application
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
    page_title="AI Hostel Management Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db.init_database()

# Custom Modern Glassmorphism & Dashboard CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
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

    .gate-pass-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #334155;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }

    .ai-bubble {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 14px 18px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "ADMIN"
if "logged_user" not in st.session_state:
    st.session_state["logged_user"] = "Chief Administrator"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "👋 Hello! I am your **AI Hostel Assistant**. Ask me anything about room allotments, leave policies, mess menus, curfew hours, or maintenance status!"}
    ]

# Sidebar Brand & User Switcher
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <h2 style="margin: 0; color: #1e3c72;">🏢 SmartHostel AI</h2>
        <span style="font-size: 0.8rem; color: #64748b; font-weight: 500;">INTELLIGENT CAMPUS LIVING</span>
    </div>
    """, unsafe_allow_html=True)

    # Role Selector for rapid demoing / role-based views
    role = st.selectbox(
        "🎭 View Mode / Role",
        ["ADMIN", "WARDEN", "STUDENT (Aarav Sharma)", "STUDENT (Ananya Sen)", "SECURITY / GATE"],
        index=0
    )

    if role == "ADMIN":
        st.session_state["user_role"] = "ADMIN"
        st.session_state["logged_user"] = "Chief Administrator"
    elif role == "WARDEN":
        st.session_state["user_role"] = "WARDEN"
        st.session_state["logged_user"] = "Dr. Rajesh Sharma (Warden)"
    elif "Aarav" in role:
        st.session_state["user_role"] = "STUDENT"
        st.session_state["student_id"] = 1
        st.session_state["logged_user"] = "Aarav Sharma (STU-1001)"
    elif "Ananya" in role:
        st.session_state["user_role"] = "STUDENT"
        st.session_state["student_id"] = 6
        st.session_state["logged_user"] = "Ananya Sen (STU-1006)"
    elif "SECURITY" in role:
        st.session_state["user_role"] = "SECURITY"
        st.session_state["logged_user"] = "Security Command Post"

    st.markdown("---")

    menu_options = [
        "📊 Dashboard Overview",
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

    selected_menu = st.radio("Navigation", menu_options, label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"""
    <div style="background: #f1f5f9; padding: 12px; border-radius: 10px; font-size: 0.8rem; color: #475569;">
        <strong>Active Profile:</strong><br>
        👤 {st.session_state['logged_user']}<br>
        🏷️ Role: <span class="badge-info">{st.session_state['user_role']}</span>
    </div>
    """, unsafe_allow_html=True)


# ======================================================================================
# 1. DASHBOARD OVERVIEW
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


# ======================================================================================
# 2. HOSTEL & ROOM MATRIX
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

    # Grid Display
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

            # Get students in this room
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

    # Add / Edit Room Modal Expander
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
# 3. AI SMART ROOM ALLOCATION
# ======================================================================================
elif selected_menu == "🎯 AI Smart Room Allocation":
    st.title("🎯 AI Smart Room Allocation & Compatibility Matcher")
    st.caption("Matches unallocated students or room swap candidates using multi-factor psychological, habits, and lifestyle synergy AI scoring.")

    unallocated_students = db.fetch_all("SELECT * FROM students WHERE room_id IS NULL")
    all_students = db.fetch_all("SELECT * FROM students")
    available_rooms = db.fetch_all("SELECT * FROM rooms WHERE status != 'FULL' AND status != 'MAINTENANCE'")

    st.markdown(f"""
    <div class="ai-bubble">
        <strong>🧠 AI Allocation Engine Status:</strong> Active & Ready<br>
        Analyzes 7 compatibility vectors: <em>Seniority (Year), Departmental Synergy, Sleep Cycles (Early Bird vs Night Owl), Study Style, Cleanliness Habits, AC Preferences, and Capacity</em>.
    </div>
    """, unsafe_allow_html=True)

    alloc_c1, alloc_c2 = st.columns([1, 1.4])

    with alloc_c1:
        st.subheader("1. Select Candidate Student")
        student_choices = {f"{s['name']} ({s['student_id_code']} - Yr {s['year']} {s['department']})": s['id'] for s in all_students}
        sel_student_label = st.selectbox("Choose Student", list(student_choices.keys()))
        selected_stu_id = student_choices[sel_student_label]
        student_obj = db.fetch_one("SELECT * FROM students WHERE id = ?", (selected_stu_id,))

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

    with alloc_c2:
        st.subheader("2. AI Compatibility Rankings & Recommendations")
        
        recommendations = []
        for r in available_rooms:
            # Fetch existing roommates in this room
            roommates = db.fetch_all("SELECT * FROM students WHERE room_id = ?", (r["id"],))
            comp = ai.calculate_room_compatibility(student_obj, r, roommates)
            if comp["score"] > 0:
                recommendations.append({
                    "room": r,
                    "comp": comp,
                    "roommates": roommates
                })

        recommendations.sort(key=lambda x: x["comp"]["score"], reverse=True)

        if recommendations:
            for idx, rec in enumerate(recommendations[:5]):
                r = rec["room"]
                comp = rec["comp"]
                roommates = rec["roommates"]
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
                        # Free previous room if any
                        if student_obj["room_id"]:
                            db.execute_query("UPDATE rooms SET occupied_beds = MAX(0, occupied_beds - 1) WHERE id = ?", (student_obj["room_id"],))
                            # update status
                            prev_r = db.fetch_one("SELECT * FROM rooms WHERE id = ?", (student_obj["room_id"],))
                            if prev_r:
                                new_st = "AVAILABLE" if prev_r["occupied_beds"] == 0 else "PARTIALLY_OCCUPIED"
                                db.execute_query("UPDATE rooms SET status = ? WHERE id = ?", (new_st, student_obj["room_id"]))

                        # Allocate new room
                        new_occ = r["occupied_beds"] + 1
                        new_status = "FULL" if new_occ >= r["capacity"] else "PARTIALLY_OCCUPIED"
                        db.execute_query("UPDATE rooms SET occupied_beds = ?, status = ? WHERE id = ?", (new_occ, new_status, r["id"]))
                        db.execute_query("UPDATE students SET room_id = ? WHERE id = ?", (r["id"], student_obj["id"]))
                        st.success(f"🎉 Successfully allocated {student_obj['name']} to Room {r['room_number']} with {comp['percentage']} compatibility!")
                        st.rerun()
        else:
            st.warning("No vacant rooms found meeting allocation constraints.")


# ======================================================================================
# 4. STUDENT DIRECTORY
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

    st.markdown(f"**Total Registered Residents: {len(student_list)}**")

    # Table view
    df_stus = pd.DataFrame(student_list)
    if not df_stus.empty:
        display_cols = ['student_id_code', 'name', 'gender', 'department', 'year', 'room_number', 'sleep_habit', 'fee_status', 'phone', 'parent_phone']
        st.dataframe(df_stus[display_cols], use_container_width=True, hide_index=True)

    # Register New Student Modal
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
                    n_gender = st.selectbox("Gender", ["Male", "Female"])
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
                    try:
                        db.execute_query("""
                        INSERT INTO students (student_id_code, name, email, phone, gender, department, year, sleep_habit, study_habit, cleanliness, dietary_pref, fee_status, parent_name, parent_phone)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?, ?)
                        """, (n_code, n_name, n_email, n_phone, n_gender, n_dept, n_year, n_sleep, n_study, n_clean, n_diet, n_parent, n_parent_phone))
                        st.success(f"Student {n_name} ({n_code}) registered successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error registering student: {e}")


# ======================================================================================
# 5. AI COMPLAINTS & MAINTENANCE TRIAGE
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
                # Student selection
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
                    # Run AI analysis
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
            
            sb_c1, sb_c2, sb_c3, sb_c4 = st.columns(4)
            with sb_c1:
                st.metric("Detected Category", res["category"])
            with sb_c2:
                st.metric("Urgency / Priority", res["priority"])
            with sb_c3:
                st.metric("Sentiment", res["sentiment"])
            with sb_c4:
                st.metric("Target SLA", f"{res['sla_hours']} Hours")

            st.markdown("---")
            st.markdown(f"**🏢 Assigned Department:** `{res['department']}`")
            st.markdown(f"**🔧 Recommended Action Plan:** `{res['suggested_action']}`")
            st.markdown(f"**🎯 AI Confidence Score:** `{int(res['confidence']*100)}%`")


# ======================================================================================
# 6. SMART ATTENDANCE & NIGHT CURFEW
# ======================================================================================
elif selected_menu == "📅 Smart Attendance & Curfew":
    st.title("📅 Smart Attendance & Night Curfew Tracker")
    st.caption("Automated turnstile RFID/Biometric night roll call logger and absentee alert system.")

    att_date = st.date_input("Select Attendance Date", value=date.today())
    att_date_str = att_date.strftime("%Y-%m-%d")

    records = db.fetch_all("SELECT * FROM attendance WHERE date = ?", (att_date_str,))
    students = db.fetch_all("SELECT * FROM students")

    # If no records for selected date, provide 1-click batch generation
    if not records:
        st.info(f"No roll call logged yet for {att_date_str}.")
        if st.button("⚡ Run Automated RFID Night Attendance Simulation for Today"):
            for s in students:
                rand_val = random.random()
                stat = "PRESENT" if rand_val > 0.12 else ("LATE" if rand_val > 0.05 else "ABSENT")
                cin = "21:10" if stat == "PRESENT" else ("22:40" if stat == "LATE" else None)
                cout = "07:30" if stat in ["PRESENT", "LATE"] else None
                db.execute_query("""
                INSERT INTO attendance (student_id, student_name, room_number, date, status, check_in_time, check_out_time, marked_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Smart RFID Biometric Gate')
                """, (s["id"], s["name"], f"Room {s['room_id'] or 'Unassigned'}", att_date_str, stat, cin, cout))
            st.success("RFID Roll Call generated!")
            st.rerun()
    else:
        # Metrics
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
        
        # Display Table
        df_att = pd.DataFrame(records)
        st.dataframe(df_att[['student_id', 'student_name', 'room_number', 'date', 'status', 'check_in_time', 'check_out_time', 'marked_by']], use_container_width=True, hide_index=True)

        # Trigger Automated Parent Alert for Absentees
        if a_count > 0 and st.session_state["user_role"] in ["ADMIN", "WARDEN"]:
            st.warning(f"🚨 {a_count} student(s) marked ABSENT past curfew cutoff.")
            if st.button("📲 Send Automated SMS Notification to Absentee Guardians"):
                st.success("✅ SMS Alerts dispatched to guardians: 'Your ward was not present during mandatory 09:30 PM hostel curfew check.'")


# ======================================================================================
# 7. LEAVE & DIGITAL GATE PASS
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
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.9rem;">
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
                <div style="margin-top: 14px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; font-size: 0.8rem; color: #cbd5e1;">
                    🔒 Approved by {p['approved_by']} • Ready for QR Scan at Main Turnstile Security Gate
                </div>
            </div>
            """, unsafe_allow_html=True)


# ======================================================================================
# 8. MESS & AI WASTE ANALYTICS
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
# 9. FEE & RISK DEFAULTERS
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
# 10. VISITOR LOG & SECURITY
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
# 11. NOTICE BOARD & BROADCASTS
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
# 12. AI HOSTEL ASSISTANT (CHATBOT)
# ======================================================================================
elif selected_menu == "🤖 AI Hostel Assistant (Chatbot)":
    st.title("🤖 24x7 AI Hostel Assistant")
    st.caption("Ask questions in natural language about hostel rules, mess schedules, fee deadlines, gate passes, and room facilities.")

    # Display chat history
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    if prompt := st.chat_input("Ask a question (e.g. 'What are the night curfew rules?', 'How to apply for gate pass?', 'What is today's dinner?')..."):
        # Append user message
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        ai_reply = ai.generate_chat_response(prompt)
        
        st.session_state["chat_history"].append({"role": "assistant", "content": ai_reply})
        with st.chat_message("assistant"):
            st.markdown(ai_reply)
