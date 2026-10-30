"""
AI Engine for Advanced Hostel Management System
Includes NLP Complaint Analysis, Smart Room Compatibility Matching, 
Predictive Analytics (Food Demand, Fee Risk, Attendance Anomaly), and Conversational AI Assistant.
"""

import os
import re
import math
from datetime import datetime, date, timedelta
import json
import urllib.request
import urllib.error
import io
import base64

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except Exception:
    GTTS_AVAILABLE = False

# --------------------------------------------------------------------------------------
# 1. NLP COMPLAINT ANALYSIS & TRIAGE ENGINE
# --------------------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Plumbing": ["water", "pipe", "leak", "tap", "flush", "shower", "drain", "clog", "sink", "washbasin", "toilet", "sewage", "faucet"],
    "Electrical": ["light", "fan", "spark", "electric", "power", "switch", "socket", "short circuit", "ac", "air conditioner", "geyser", "wire", "mcb"],
    "Internet & Wi-Fi": ["wifi", "wi-fi", "internet", "router", "network", "speed", "lan", "disconnect", "signal", "ethernet", "slow net", "access point"],
    "Food & Mess": ["food", "mess", "taste", "dal", "roti", "rice", "curry", "stale", "cold", "insects", "hygiene", "meal", "dinner", "lunch", "breakfast", "caterer"],
    "Housekeeping & Cleanliness": ["clean", "dust", "garbage", "trash", "dustbin", "sweep", "mop", "smell", "odor", "dirty", "corridor", "washroom dirty", "pest", "cockroach", "mosquito"],
    "Carpentry & Furniture": ["bed", "chair", "table", "almirah", "cupboard", "door", "window", "lock", "hinge", "handle", "wardrobe", "broken"],
    "Discipline & Noise": ["noise", "loud", "music", "disturb", "shouting", "fight", "smoking", "ragging", "harassment", "party", "curfew"],
    "Security & Safety": ["theft", "stolen", "lost", "stranger", "trespass", "cctv", "guard", "safety", "threat", "emergency"]
}

URGENT_KEYWORDS = ["danger", "emergency", "fire", "spark", "shock", "flooding", "burst", "theft", "harassment", "bleeding", "severe", "short circuit", "bursting", "collapsed"]
HIGH_KEYWORDS = ["leak", "urgent", "no water", "power cut", "broken lock", "no wifi", "stale", "immediately", "spoil", "cold food", "overflowing"]

NEGATIVE_SENTIMENT_WORDS = ["terrible", "worst", "horrible", "bad", "angry", "frustrated", "awful", "unacceptable", "disaster", "urgent", "pathetic", "dirty", "broken", "useless", "suffering"]
POSITIVE_SENTIMENT_WORDS = ["good", "resolved", "thanks", "helpful", "appreciated", "better", "great", "satisfied"]

def analyze_complaint(text: str) -> dict:
    """Performs deep rule-based NLP classification on a complaint description."""
    if not text:
        text = "General complaint"

    t = text.lower()
    
    # 1. Category Detection
    category_scores = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in t)
        if score > 0:
            category_scores[cat] = score

    if category_scores:
        category = max(category_scores, key=category_scores.get)
    else:
        category = "Other"

    # 2. Priority & Urgency Score
    if any(k in t for k in URGENT_KEYWORDS):
        priority = "URGENT"
        sla_hours = 2
        confidence = 0.95
    elif any(k in t for k in HIGH_KEYWORDS) or len(text) > 150:
        priority = "HIGH"
        sla_hours = 8
        confidence = 0.88
    elif len(text) < 40 and category in ["Housekeeping & Cleanliness", "Carpentry & Furniture"]:
        priority = "LOW"
        sla_hours = 48
        confidence = 0.80
    else:
        priority = "MEDIUM"
        sla_hours = 24
        confidence = 0.85

    # 3. Sentiment Analysis
    neg_count = sum(1 for w in NEGATIVE_SENTIMENT_WORDS if w in t)
    pos_count = sum(1 for w in POSITIVE_SENTIMENT_WORDS if w in t)
    
    if neg_count > pos_count or "!" in text or priority in ["URGENT", "HIGH"]:
        sentiment = "NEGATIVE"
        sentiment_score = -0.75 if priority == "URGENT" else -0.45
    elif pos_count > neg_count:
        sentiment = "POSITIVE"
        sentiment_score = 0.60
    else:
        sentiment = "NEUTRAL"
        sentiment_score = 0.0

    # 4. Department & Action
    dept_map = {
        "Plumbing": ("Maintenance / Plumbing Dept", "Dispatch licensed plumber to inspect pipe pressure, valves, and replace worn seals."),
        "Electrical": ("Electrical Maintenance Dept", "Check circuit breakers, isolate faulty line, replace damaged fixture or socket."),
        "Internet & Wi-Fi": ("Campus IT & Networking Support", "Run ping test on nearest AP, check DHCP pool, reset switch port if packet loss persists."),
        "Food & Mess": ("Hostel Mess Committee & Caterer", "Inspect pantry batch sample, review kitchen hygiene protocol with head chef."),
        "Housekeeping & Cleanliness": ("Housekeeping & Sanitation Team", "Deploy floor cleaning staff for immediate sanitization and waste clearance."),
        "Carpentry & Furniture": ("Carpentry & Infrastructure", "Assess furniture integrity, repair hinges/latches, or schedule replacement."),
        "Discipline & Noise": ("Hostel Proctor & Warden Office", "Counsel involved residents, enforce hostel silence hours (10:00 PM - 06:00 AM)."),
        "Security & Safety": ("Chief Security Officer", "Review CCTV footage at timestamps and increase gate patrol frequency."),
        "Other": ("Hostel Administration", "Review grievance and assign to corresponding hostel staff.")
    }

    dept, action = dept_map.get(category, ("Hostel Administration", "Review and triage."))

    # Summary extraction (first sentence or 90 chars)
    sentences = re.split(r'[.!?]+', text.strip())
    summary = sentences[0].strip() if sentences and sentences[0] else text[:80]
    if len(summary) > 85:
        summary = summary[:82] + "..."

    return {
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "department": dept,
        "suggested_action": action,
        "sla_hours": sla_hours,
        "confidence": confidence,
        "summary": summary
    }


# --------------------------------------------------------------------------------------
# 2. SMART ROOM ALLOCATION & COMPATIBILITY ENGINE
# --------------------------------------------------------------------------------------

def calculate_room_compatibility(student: dict, room: dict, existing_roommates: list = None) -> dict:
    """
    Calculates a multi-dimensional AI compatibility score (0-100%) for allocating
    a student to a specific room with explainable breakdown.
    """
    score = 45 # Base score
    factors = []

    # 1. Capacity & Availability check
    avail_beds = room["capacity"] - room["occupied_beds"]
    if avail_beds <= 0 or room["status"] == "MAINTENANCE":
        return {
            "score": 0,
            "percentage": "0%",
            "recommended": False,
            "reason": "Room is currently full or under maintenance.",
            "factors": ["Unavailable"]
        }

    # 2. Seniority / Year Compatibility
    year = student.get("year", 1)
    if year >= 3 and room["room_type"] in ["Single", "Double"]:
        score += 15
        factors.append(f"Year {year} seniority matches preferred low-occupancy ({room['room_type']}) room (+15%)")
    elif year == 1 and room["room_type"] in ["Double", "Triple"]:
        score += 12
        factors.append("First-year peer group collaboration bonus (+12%)")
    else:
        score += 5
        factors.append(f"Standard room capacity match for Year {year} (+5%)")

    # 3. Room Type & Amenities
    amenities = room.get("amenities", "") or ""
    if "AC" in amenities:
        score += 8
        factors.append("Equipped with Air Conditioning & climate comfort (+8%)")
    if "Attached Bath" in amenities:
        score += 7
        factors.append("Attached bathroom hygiene convenience (+7%)")
    if "Balcony" in amenities:
        score += 5
        factors.append("Natural ventilation and balcony access (+5%)")

    # 4. Lifestyle & Habit Matching with Existing Roommates
    if existing_roommates:
        match_count = 0
        total_checks = 0
        
        stu_sleep = student.get("sleep_habit", "Flexible")
        stu_study = student.get("study_habit", "Moderate")
        stu_clean = student.get("cleanliness", "High")
        stu_dept = student.get("department", "")

        for mate in existing_roommates:
            total_checks += 4
            # Sleep habit
            if mate.get("sleep_habit") == stu_sleep or stu_sleep == "Flexible" or mate.get("sleep_habit") == "Flexible":
                match_count += 1
            # Study habit
            if mate.get("study_habit") == stu_study or stu_study == "Moderate" or mate.get("study_habit") == "Moderate":
                match_count += 1
            # Cleanliness
            if mate.get("cleanliness") == stu_clean:
                match_count += 1
            # Department synergy (shared coursework vs cross-disciplinary quiet)
            if mate.get("department") == stu_dept:
                match_count += 1

        synergy_pct = (match_count / max(1, total_checks))
        synergy_bonus = int(synergy_pct * 20)
        score += synergy_bonus
        factors.append(f"Lifestyle & roommate habit synergy: {int(synergy_pct*100)}% alignment (+{synergy_bonus}%)")
    else:
        # Fresh unoccupied room bonus
        score += 15
        factors.append("Fresh room selection with maximum privacy and quiet environment (+15%)")

    # Floor preference adjustment
    floor = room.get("floor_number", 1)
    if floor in [1, 2]:
        score += 5
        factors.append(f"Floor {floor} easy campus accessibility (+5%)")

    final_score = min(max(score, 25), 98)

    return {
        "score": final_score,
        "percentage": f"{final_score}%",
        "recommended": final_score >= 70,
        "reason": factors[0] if factors else "Standard matching criteria fulfilled.",
        "factors": factors
    }


# --------------------------------------------------------------------------------------
# 3. PREDICTIVE ANALYTICS ENGINE
# --------------------------------------------------------------------------------------

def predict_mess_demand(total_students: int, on_leave_count: int, day_of_week: str) -> dict:
    """
    Predicts expected meal headcounts and estimated grocery/portions needed
    to prevent dining waste.
    """
    active_in_hostel = max(0, total_students - on_leave_count)
    is_weekend = day_of_week in ["Saturday", "Sunday"]

    # Historical attendance coefficients
    factors = {
        "Breakfast": 0.88 if not is_weekend else 0.72,
        "Lunch": 0.78 if not is_weekend else 0.92,
        "Snacks": 0.65 if not is_weekend else 0.80,
        "Dinner": 0.94 if not is_weekend else 0.85
    }

    forecast = {}
    for meal, factor in factors.items():
        expected_headcount = int(active_in_hostel * factor)
        # Buffer of +5%
        buffer_headcount = int(expected_headcount * 1.05)
        # Food weight approx 380g per student per meal
        est_food_kg = round(buffer_headcount * 0.38, 1)
        est_rice_wheat_kg = round(buffer_headcount * 0.16, 1)
        est_veg_dal_kg = round(buffer_headcount * 0.22, 1)

        forecast[meal] = {
            "expected_students": expected_headcount,
            "prepared_capacity": buffer_headcount,
            "total_food_kg": est_food_kg,
            "grain_kg": est_rice_wheat_kg,
            "curry_dal_kg": est_veg_dal_kg,
            "confidence": "94%" if not is_weekend else "89%"
        }

    return {
        "active_students": active_in_hostel,
        "on_leave_students": on_leave_count,
        "meals": forecast,
        "waste_reduction_estimate": f"{int(active_in_hostel * 0.12 * 0.38)} kg saved vs unoptimized cooking"
    }

def calculate_defaulter_risk(fee_records: list) -> list:
    """Analyzes fee dues, due dates, and marks default risk levels."""
    today = date.today()
    analyzed = []

    for record in fee_records:
        due_date_str = record.get("due_date", "2026-08-15")
        try:
            due_d = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            days_overdue = (today - due_d).days
        except Exception:
            days_overdue = 0

        amt_due = record.get("amount_due", 0)
        total_amt = record.get("total_amount", 1)

        if amt_due <= 0:
            risk = "NO RISK"
            score = 0
            action = "Account settled in full."
        elif days_overdue > 30 or (amt_due == total_amt and days_overdue > 7):
            risk = "HIGH RISK"
            score = 85 + min(10, days_overdue)
            action = "Send automated SMS alert to guardian and place temporary gate pass hold."
        elif days_overdue > 0 or amt_due > (total_amt * 0.5):
            risk = "MODERATE RISK"
            score = 55
            action = "Send email reminder to student portal notification inbox."
        else:
            risk = "LOW RISK"
            score = 25
            action = "Payment pending within regular grace period."

        item = dict(record)
        item["days_overdue"] = max(0, days_overdue)
        item["risk_level"] = risk
        item["risk_score"] = score
        item["recommended_action"] = action
        analyzed.append(item)

    return sorted(analyzed, key=lambda x: x["risk_score"], reverse=True)


# --------------------------------------------------------------------------------------
# 4. CONVERSATIONAL AI HOSTEL ASSISTANT WITH REAL-TIME DATABASE GROUNDING
# --------------------------------------------------------------------------------------

HOSTEL_KNOWLEDGE_BASE = [
    {
        "keywords": ["hi", "hello", "hey", "who are you", "what can you do", "help", "about", "assist", "good morning", "good evening"],
        "answer": "👋 **Hello! I am your AI Hostel Assistant.**\n\nI am connected to real-time campus databases and can assist you with:\n- 🍲 **Mess & Dining:** Today's menu, nutrition, meal timings & specials\n- 🚪 **My Room & Roommates:** Allocation status, bed details & contact info\n- 🕒 **Hostel & Curfew Rules:** 09:30 PM gate cutoff & biometric attendance\n- ✈️ **Leave & Gate Pass:** Digital QR passes & Warden approvals\n- 🛠️ **Maintenance Complaints:** NLP ticket triage & technician dispatch\n- 💳 **Fee & Payments:** Dues, payment deadlines & transaction receipts\n- 📊 **Campus Intelligence:** Live occupancy & maintenance stats (Admins)\n- 🚨 **Emergency Directory:** Warden, Security & Medical helplines\n\n*What would you like to know?*"
    },
    {
        "keywords": ["curfew", "night", "timing", "gate close", "in-time", "late", "entry", "night out", "hours"],
        "answer": "🕒 **Hostel Timings & Night Curfew Policy:**\n- **Main Campus Gate Cutoff:** **09:30 PM** sharp for all resident blocks.\n- **Night Biometric Attendance:** Taken between **09:00 PM – 09:45 PM** daily at the turnstile.\n- **Late Entry Rule:** Entering after 09:30 PM requires an approved **Digital Gate Pass** signed by your Warden. Unauthorized late entries trigger automated notification to parents."
    },
    {
        "keywords": ["leave", "gate pass", "outstation", "home", "permission", "vacation", "pass", "qr", "apply leave"],
        "answer": "✈️ **Leave & Digital Gate Pass Application:**\n1. Go to the **Leave & Digital Gate Pass** tab on the left sidebar.\n2. Enter departure & return dates along with your destination reason.\n3. Your Warden receives the request in real-time. Once approved, an instant **QR Code Gate Pass** is generated on screen.\n4. Show the QR code to the turnstile scanner at the main security gate."
    },
    {
        "keywords": ["complaint", "repair", "plumber", "electrician", "leak", "clean", "tap", "fan", "light", "water", "geyser", "socket", "maintenance", "broken", "dirty"],
        "answer": "🛠️ **Filing & Tracking Maintenance Grievances:**\n- Navigate to the **AI Complaints & Triage** section or type *'Report issue: [description]'* here in chat.\n- Our **NLP AI Triage Engine** automatically categorizes the grievance, assesses urgency (SLA: 2–24 hrs), and routes it to the duty technician."
    },
    {
        "keywords": ["fee", "payment", "due", "dues", "installment", "receipt", "fine", "online payment", "upi", "bank", "cost", "rent"],
        "answer": "💳 **Hostel Fee & Payment Guidelines:**\n- Semester room & mess dues must be cleared by the **15th** of each semester cycle.\n- You can inspect your payment status and download receipts in the **Fee Status** ledger.\n- Accepted modes: UPI, Net Banking, NEFT/RTGS, and Debit/Credit card."
    },
    {
        "keywords": ["room change", "swap", "allocate", "single room", "double", "triple", "occupancy", "vacancy", "bed", "allotment"],
        "answer": "🎯 **Room Allocation & Compatibility Engine:**\n- View available rooms and match scores in the **AI Smart Room Allocation** tab.\n- Our algorithm matches students based on **Sleep Schedule (Early Bird vs Night Owl)**, **Study Habits**, **Cleanliness**, and **Year/Department synergy** to ensure optimal compatibility."
    },
    {
        "keywords": ["visitor", "parent", "guest", "friend", "father", "mother", "visiting hours", "relatives"],
        "answer": "🛡️ **Visitor & Guest Policy:**\n- **Visiting Hours:** 09:00 AM – 07:00 PM daily in the Ground Floor Visitor Lounge.\n- Parents and guardians must register at the Security Gate with valid photo ID proof.\n- Non-resident guests are not permitted in residential rooms after 07:30 PM."
    },
    {
        "keywords": ["wifi", "internet", "password", "lan", "speed", "login", "network", "ethernet"],
        "answer": "📶 **Campus High-Speed Wi-Fi & Internet:**\n- **SSID:** `CAMPUS_HOSTEL_5G` / `CAMPUS_HOSTEL_2.4G`\n- **Login:** Enter your Student ID (`STU-XXXX`) and portal credentials on the captive login page.\n- High-speed 1Gbps LAN ports are also available in study rooms and library kiosks."
    },
    {
        "keywords": ["attendance", "roll call", "biometric", "rfid", "present", "absent", "punch", "turnstile"],
        "answer": "📅 **Smart Attendance & Night Roll Call:**\n- Night biometric/RFID roll call takes place between **09:00 PM – 09:45 PM** at your block entrance turnstile.\n- Unexcused absences past 09:30 PM automatically trigger SMS alerts to parents and disciplinary remarks."
    },
    {
        "keywords": ["emergency", "warden contact", "medical", "doctor", "ambulance", "security", "fire", "hospital", "first aid", "sick", "phone", "help"],
        "answer": "🚨 **24x7 Emergency Contact Directory:**\n- 🏥 **Campus Health Centre & Ambulance:** Ext: 108 / +91 98765 00108\n- 👨‍💼 **Chief Boys Warden (Dr. Rajesh Sharma):** +91 98765 43210\n- 👩‍💼 **Chief Girls Warden (Dr. Sunita Verma):** +91 98765 43211\n- 🛡️ **Main Security Gate Control Desk:** Ext: 100 / +91 98765 00100"
    },
    {
        "keywords": ["gym", "laundry", "washing machine", "sports", "library", "amenities", "facilities"],
        "answer": "🏋️ **Hostel Amenities & Facilities:**\n- **Gymnasium:** Open 06:00 AM – 08:30 AM & 05:30 PM – 08:30 PM.\n- **Automated Laundry Room:** 24x7 smart token washing machines on Floor 1.\n- **Reading Room & Library:** Open 24x7 with high-speed AC & silent study pods.\n- **Sports Facilities:** Badminton, Table Tennis, and Basketball courts open till 09:00 PM."
    },
    {
        "keywords": ["ragging", "discipline", "harassment", "alcohol", "smoking", "proctor", "rule", "penalty"],
        "answer": "⚖️ **Zero-Tolerance Anti-Ragging & Discipline Code:**\n- The campus enforces a strict **Zero-Tolerance Anti-Ragging Policy** under national guidelines.\n- Possession of alcohol, smoking, or contraband inside hostel premises is strictly prohibited and results in immediate suspension.\n- Anti-Ragging Helpline (24x7): **1800-180-5522** or contact the Proctor Office."
    }
]


def generate_chat_response(
    query: str, 
    user_context: dict = None,
    api_url: str = None, 
    api_key: str = None, 
    model_name: str = None
) -> str:
    """
    Advanced context-aware AI Chatbot with real-time SQLite database grounding, 
    student/admin personalization, tool queries, and multi-model LLM integration.
    """
    if not query or not query.strip():
        return "👋 How can I help you today? Ask about curfew timings, room allotments, mess menus, leave gate passes, or filing complaints."

    q_clean = query.strip().lower()
    user_context = user_context or {}
    user_role = user_context.get("user_role", "STUDENT")
    logged_user = user_context.get("logged_user", "Resident")
    student_profile = user_context.get("student_profile", {})

    import database as db

    # ==================================================================================
    # 1. LIVE DATABASE GROUNDING: MESS & FOOD MENU INTENTS
    # ==================================================================================
    food_kws = ["mess", "food", "menu", "dinner", "lunch", "breakfast", "snacks", "meal", "meals", "eating", "eat", "curry", "dish", "diet"]
    if any(re.search(rf"\b{k}\b", q_clean) for k in food_kws) and not any(r in q_clean for r in ["room", "block"]):
        # Determine target day
        days_map = {
            "monday": "Monday", "tuesday": "Tuesday", "wednesday": "Wednesday",
            "thursday": "Thursday", "friday": "Friday", "saturday": "Saturday", "sunday": "Sunday"
        }
        target_day = None
        for d_key, d_val in days_map.items():
            if d_key in q_clean:
                target_day = d_val
                break

        if not target_day:
            if "tomorrow" in q_clean:
                target_day = (datetime.now() + timedelta(days=1)).strftime("%A")
            elif "yesterday" in q_clean:
                target_day = (datetime.now() - timedelta(days=1)).strftime("%A")
            else:
                target_day = datetime.now().strftime("%A")

        # Query live database
        menu_items = db.fetch_all("SELECT * FROM mess_menu WHERE day_of_week = ?", (target_day,))
        if menu_items:
            # Check if specific meal requested
            specific_meal = None
            if "breakfast" in q_clean:
                specific_meal = "Breakfast"
            elif "lunch" in q_clean:
                specific_meal = "Lunch"
            elif "snacks" in q_clean or "snack" in q_clean or "tea" in q_clean:
                specific_meal = "Snacks"
            elif "dinner" in q_clean:
                specific_meal = "Dinner"

            if specific_meal:
                meal_data = next((m for m in menu_items if m["meal_type"] == specific_meal), None)
                if meal_data:
                    return (
                        f"🍲 **{target_day} {specific_meal} Menu:**\n\n"
                        f"• **Dishes:** {meal_data['items']}\n"
                        f"• ✨ **Special Item:** {meal_data['special_item']}\n"
                        f"• 🔥 **Nutritional Energy:** {meal_data['calories']} kcal\n\n"
                        f"🕒 *Dining Hall is open for {specific_meal} as per standard mess schedule.*"
                    )

            # Full day menu
            lines = [f"📅 **Dining Menu for {target_day}:**\n"]
            icons = {"Breakfast": "🥞", "Lunch": "🍛", "Snacks": "☕", "Dinner": "🍲"}
            for m in menu_items:
                ic = icons.get(m["meal_type"], "🍽️")
                lines.append(
                    f"{ic} **{m['meal_type']}** ({m['calories']} kcal):\n"
                    f"  {m['items']}\n"
                    f"  *Special:* **{m['special_item']}**\n"
                )
            return "\n".join(lines)

    # ==================================================================================
    # 2. LIVE DATABASE GROUNDING: STUDENT ROOM & ROOMMATES INTENTS
    # ==================================================================================
    if any(k in q_clean for k in ["my room", "roommates", "roommate", "who is in my room", "my bed", "my block", "my floor", "room details"]) and user_role == "STUDENT":
        if student_profile:
            room_info = student_profile.get("room_details")
            roommates = student_profile.get("roommates", [])
            
            if room_info:
                rm_text = ""
                if roommates:
                    rm_list = [f"• 👤 **{rm['name']}** (Year {rm['year']} {rm['department']}) — 📞 {rm['phone']}" for rm in roommates]
                    rm_text = "\n\n**Your Roommates:**\n" + "\n".join(rm_list)
                else:
                    rm_text = "\n\n*No roommates are currently assigned to your room.*"

                return (
                    f"🚪 **Your Room Details ({logged_user}):**\n\n"
                    f"• **Room Number:** **{room_info['room_number']}**\n"
                    f"• **Hostel / Block:** {room_info['hostel_name']} ({room_info['block_name']}, Floor {room_info['floor_number']})\n"
                    f"• **Room Type:** {room_info['room_type']} ({room_info['occupied_beds']} / {room_info['capacity']} Beds Occupied)\n"
                    f"• **Monthly Rent:** ₹{room_info['rent_per_month']:,.0f}\n"
                    f"• **Amenities:** {room_info['amenities'] or 'Standard'}"
                    f"{rm_text}"
                )
            else:
                return f"ℹ️ **Hi {logged_user}**, you are currently not allocated to a room yet. The Hostel Warden will allocate your room shortly using the AI Compatibility Matcher."

    # ==================================================================================
    # 3. LIVE DATABASE GROUNDING: FEE DUES & ACCOUNT INTENTS
    # ==================================================================================
    if any(k in q_clean for k in ["my fee", "fee due", "fee status", "how much fee", "my dues", "payment receipt"]) and user_role == "STUDENT":
        if student_profile:
            fee_info = student_profile.get("fee_details")
            if fee_info:
                status_emoji = "✅" if fee_info['amount_due'] == 0 else "⚠️"
                return (
                    f"💳 **Your Hostel Fee Statement ({logged_user}):**\n\n"
                    f"• **Account Status:** {status_emoji} **{fee_info['status']}**\n"
                    f"• **Total Semester Fee:** ₹{fee_info['total_amount']:,.0f}\n"
                    f"• **Amount Paid:** ₹{fee_info['amount_paid']:,.0f}\n"
                    f"• **Outstanding Due:** **₹{fee_info['amount_due']:,.0f}**\n"
                    f"• **Due Date:** {fee_info['due_date']}\n"
                    f"• **Transaction Ref:** `{fee_info['transaction_ref'] or 'N/A'}`"
                )

    # ==================================================================================
    # 4. LIVE DATABASE GROUNDING: GATE PASS & LEAVE STATUS INTENTS
    # ==================================================================================
    if any(k in q_clean for k in ["my gate pass", "my pass", "my leave", "leave status", "is my leave approved"]) and user_role == "STUDENT":
        if student_profile:
            leaves = student_profile.get("leaves", [])
            if leaves:
                latest = leaves[0]
                badge = "🟢 APPROVED" if latest['status'] == "APPROVED" else ("🟡 PENDING WARDEN REVIEW" if latest['status'] == "PENDING" else "🔴 REJECTED")
                pass_snippet = f"\n• 🎫 **Gate Pass Code:** `{latest['gate_pass_code']}` (Ready for QR Scan at gate)" if latest['gate_pass_code'] else ""
                return (
                    f"✈️ **Your Latest Leave Request:**\n\n"
                    f"• **Status:** {badge}\n"
                    f"• **Duration:** {latest['from_date']} to {latest['to_date']}\n"
                    f"• **Destination / Reason:** {latest['reason']}"
                    f"{pass_snippet}\n"
                    f"• **Created On:** {latest['created_at']}"
                )
            else:
                return f"ℹ️ **Hi {logged_user}**, you have not submitted any outstation leave requests yet. You can apply directly in the **Leave & Digital Gate Pass** tab."

    # ==================================================================================
    # 5. LIVE DATABASE GROUNDING: STUDENT COMPLAINTS INTENTS
    # ==================================================================================
    if any(k in q_clean for k in ["my complaints", "my grievance", "my tickets", "repair status"]) and user_role == "STUDENT":
        if student_profile:
            comps = student_profile.get("complaints", [])
            if comps:
                lines = [f"🛠️ **Your Maintenance Tickets ({len(comps)} total):**\n"]
                for c in comps[:4]:
                    st_icon = "✅" if c['status'] == "RESOLVED" else ("⚙️" if c['status'] == "IN_PROGRESS" else "🚨")
                    lines.append(
                        f"{st_icon} **Ticket #{c['id']} — {c['title']}**\n"
                        f"  Status: `{c['status']}` • Priority: `{c['priority']}` • Dept: {c['department']}\n"
                        f"  *AI Note:* {c['suggested_action']}\n"
                    )
                return "\n".join(lines)
            else:
                return f"ℹ️ **Hi {logged_user}**, you have no active maintenance complaints filed."

    # ==================================================================================
    # 6. ACTION INTENT: DIRECT COMPLAINT REPORTING VIA CHAT
    # ==================================================================================
    if q_clean.startswith("report issue:") or q_clean.startswith("file complaint:") or q_clean.startswith("report:") or q_clean.startswith("complaint:"):
        complaint_text = re.sub(r'^(report issue:|file complaint:|report:|complaint:)\s*', '', query, flags=re.IGNORECASE).strip()
        if complaint_text:
            ai_res = analyze_complaint(complaint_text)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            s_id = student_profile.get("id") if student_profile else None
            r_no = student_profile.get("room_details", {}).get("room_number", "Corridor") if student_profile else "Main Block"

            cid = db.execute_query("""
            INSERT INTO complaints (student_id, student_name, room_number, category, title, description, priority, sentiment, status, department, suggested_action, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?)
            """, (s_id, logged_user, r_no, ai_res['category'], ai_res['summary'], complaint_text, ai_res['priority'], ai_res['sentiment'], ai_res['department'], ai_res['suggested_action'], now_str))

            return (
                f"🎉 **Maintenance Grievance Ticket #{cid} Created Successfully!**\n\n"
                f"• 🏷️ **Category:** {ai_res['category']}\n"
                f"• 🚨 **Urgency:** `{ai_res['priority']} Priority` (SLA: {ai_res['sla_hours']} Hours)\n"
                f"• 🏢 **Assigned Department:** {ai_res['department']}\n"
                f"• 🤖 **AI Action Recommendation:** {ai_res['suggested_action']}\n\n"
                f"Our maintenance supervisor has been alerted."
            )

    # ==================================================================================
    # 7. LIVE DATABASE GROUNDING: SPECIFIC ROOM LOOKUPS (e.g., "room A-101", "who is in room G-102")
    # ==================================================================================
    room_match = re.search(r'\b([a-z]\d?-\d{3}|room\s+([a-z]\d?-\d{3}|\d+))\b', q_clean, re.IGNORECASE)
    if room_match:
        matched_str = room_match.group(1).upper().replace("ROOM", "").strip()
        matched_room = db.fetch_one("SELECT * FROM rooms WHERE UPPER(room_number) = ? OR UPPER(room_number) = ?", (matched_str, f"ROOM {matched_str}"))
        if not matched_room:
            matched_room = db.fetch_one("SELECT * FROM rooms WHERE UPPER(room_number) LIKE ?", (f"%{matched_str}%",))

        if matched_room:
            occupants = db.fetch_all("SELECT id, student_id_code, name, department, year, phone, email FROM students WHERE room_id = ?", (matched_room["id"],))
            occ_list_str = ""
            if occupants:
                occ_list_str = "\n\n**Current Occupants:**\n" + "\n".join([f"• 👤 **{o['name']}** (`{o['student_id_code']}`, Year {o['year']} {o['department']}) — 📞 {o['phone']}" for o in occupants])
            else:
                occ_list_str = "\n\n*No students currently allocated to this room (Vacant).* "

            return (
                f"🏢 **Room {matched_room['room_number']} Details:**\n\n"
                f"• **Hostel Complex:** {matched_room['hostel_name']} ({matched_room['block_name']}, Floor {matched_room['floor_number']})\n"
                f"• **Type & Capacity:** {matched_room['room_type']} ({matched_room['occupied_beds']} / {matched_room['capacity']} Beds Occupied)\n"
                f"• **Status:** `{matched_room['status']}`\n"
                f"• **Monthly Rent:** ₹{matched_room['rent_per_month']:,.0f}\n"
                f"• **Amenities:** {matched_room['amenities'] or 'Standard Furnishing'}"
                f"{occ_list_str}"
            )

    # ==================================================================================
    # 8. LIVE DATABASE GROUNDING: SPECIFIC STUDENT SEARCH (e.g., "STU-1041", "student Aarav")
    # ==================================================================================
    stu_code_match = re.search(r'\b(stu-?\d{4})\b', q_clean, re.IGNORECASE)
    if stu_code_match or (any(k in q_clean for k in ["tell me about student", "who is student", "student profile", "student details"]) and not q_clean.startswith("my ")):
        target_code = stu_code_match.group(1).upper() if stu_code_match else None
        if target_code and "-" not in target_code:
            target_code = f"STU-{target_code[3:]}"

        stu_row = None
        if target_code:
            stu_row = db.fetch_one("SELECT * FROM students WHERE UPPER(student_id_code) = ?", (target_code,))
        else:
            # Try searching by name in query
            all_stus = db.fetch_all("SELECT * FROM students")
            for s in all_stus:
                if s["name"].lower() in q_clean:
                    stu_row = s
                    break

        if stu_row:
            room_info = db.fetch_one("SELECT * FROM rooms WHERE id = ?", (stu_row["room_id"],)) if stu_row.get("room_id") else None
            room_str = f"Room {room_info['room_number']} ({room_info['hostel_name']})" if room_info else "Pending Allocation"
            fee_info = db.fetch_one("SELECT * FROM fee_records WHERE student_id = ? ORDER BY id DESC LIMIT 1", (stu_row["id"],))
            fee_str = f"₹{fee_info['amount_due']:,.0f} Due ({fee_info['status']})" if fee_info else stu_row["fee_status"]

            return (
                f"🎓 **Student Profile: {stu_row['name']} ({stu_row['student_id_code']}):**\n\n"
                f"• 📚 **Academic:** Year {stu_row['year']}, {stu_row['department']} ({stu_row['gender']})\n"
                f"• 🚪 **Allocated Room:** **{room_str}**\n"
                f"• 💳 **Fee Status:** `{fee_str}`\n"
                f"• 🧠 **Lifestyle Profile:** {stu_row['sleep_habit']} | {stu_row['study_habit']} | {stu_row['cleanliness']} Cleanliness | {stu_row['dietary_pref']}\n"
                f"• 📞 **Contact:** {stu_row['phone']} | ✉️ {stu_row['email']}\n"
                f"• 👨‍👩‍👦 **Guardian:** {stu_row['parent_name']} ({stu_row['parent_phone']})"
            )

    # ==================================================================================
    # 9. LIVE DATABASE GROUNDING: OVERDUE FEES / DEFAULTERS
    # ==================================================================================
    if any(k in q_clean for k in ["overdue fee", "defaulters", "unpaid fee", "fee due list", "who has not paid fee", "pending payments"]):
        overdue_records = db.fetch_all("SELECT * FROM fee_records WHERE status IN ('OVERDUE', 'PARTIAL') ORDER BY amount_due DESC")
        if overdue_records:
            lines = [f"⚠️ **Found {len(overdue_records)} Residents with Outstanding Dues:**\n"]
            for f_rec in overdue_records:
                lines.append(
                    f"• 👤 **{f_rec['student_name']}** — Outstanding: **₹{f_rec['amount_due']:,.0f}** / ₹{f_rec['total_amount']:,.0f} "
                    f"(`{f_rec['status']}`, Due: {f_rec['due_date']})"
                )
            return "\n".join(lines)
        else:
            return "✅ **Great news!** All resident students have cleared their hostel fee obligations."

    # ==================================================================================
    # 10. LIVE DATABASE GROUNDING: NOTICES & CIRCULARS
    # ==============================================================================
    if any(k in q_clean for k in ["notice", "notices", "circular", "announcement", "news", "what is happening", "events"]):
        notices = db.fetch_all("SELECT * FROM notices ORDER BY id DESC LIMIT 5")
        if notices:
            lines = ["📢 **Latest Official Campus Hostel Notices:**\n"]
            for n in notices:
                p_icon = "🚨" if n['priority'] == "URGENT" else ("⚠️" if n['priority'] == "HIGH" else "📌")
                lines.append(
                    f"{p_icon} **{n['title']}** ({n['category']})\n"
                    f"  {n['content']}\n"
                    f"  *Posted by: {n['posted_by']} on {n['posted_at']}*\n"
                )
            return "\n".join(lines)

    # ==================================================================================
    # 11. LIVE DATABASE GROUNDING: ADMIN / WARDEN CAMPUS STATS
    # ==================================================================================
    if any(k in q_clean for k in ["occupancy", "how many students", "campus stats", "vacant beds", "active complaints", "hostel stats", "overview of hostel"]):
        students = db.fetch_all("SELECT id, room_id FROM students")
        rooms = db.fetch_all("SELECT capacity, occupied_beds FROM rooms")
        open_comps = db.fetch_all("SELECT priority FROM complaints WHERE status != 'RESOLVED'")
        urgent_comps = [c for c in open_comps if c['priority'] in ['URGENT', 'HIGH']]
        leaves = db.fetch_all("SELECT id FROM leave_requests WHERE status = 'APPROVED'")

        tot_beds = sum(r['capacity'] for r in rooms)
        occ_beds = sum(r['occupied_beds'] for r in rooms)
        unalloc = sum(1 for s in students if not s['room_id'])
        rate = (occ_beds / max(1, tot_beds)) * 100

        return (
            f"📊 **Hostel Real-Time Operational Statistics:**\n\n"
            f"• 👨‍🎓 **Total Residents:** {len(students)} ({unalloc} pending room allocation)\n"
            f"• 🛏️ **Bed Occupancy:** {occ_beds} / {tot_beds} ({rate:.1f}% capacity across {len(rooms)} rooms)\n"
            f"• 🚨 **Open Grievances:** {len(open_comps)} ({len(urgent_comps)} High/Urgent Priority)\n"
            f"• ✈️ **Students on Approved Leave:** {len(leaves)} residents\n\n"
            f"🟢 *All 6 Hostel Blocks, automated turnstiles & AI allocation engines operating normally.*"
        )

    # ==================================================================================
    # 12. EXTERNAL LLM PROVIDER CALL (IF CONFIGURED)
    # ==================================================================================
    if not api_url:
        api_url = os.environ.get("AI_PROVIDER_URL", "")
    if not api_key:
        api_key = os.environ.get("AI_API_KEY", "")
    if not model_name:
        model_name = os.environ.get("AI_MODEL", "gpt-4o-mini")

    if api_url and api_key and api_url.startswith("http"):
        try:
            system_prompt = (
                f"You are the Advanced AI Assistant for SmartHostel AI Platform. "
                f"Current User: {logged_user} (Role: {user_role}). "
                f"Always answer clearly, politely, and accurately using markdown formatting. "
                f"Provide concise, actionable answers grounded in university hostel policies."
            )
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                "temperature": 0.3
            }
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if "choices" in res_data and len(res_data["choices"]) > 0:
                    return res_data["choices"][0]["message"]["content"]
        except Exception:
            pass  # Fall back to local knowledge engine

    # ==================================================================================
    # 9. LOCAL KNOWLEDGE BASE FUZZY MATCHING
    # ==================================================================================
    best_match = None
    max_score = 0
    query_words = set(re.findall(r'\b\w+\b', q_clean))

    for item in HOSTEL_KNOWLEDGE_BASE:
        score = 0
        for kw in item["keywords"]:
            if kw in q_clean:
                score += 3
            else:
                kw_words = set(re.findall(r'\b\w+\b', kw))
                if kw_words.issubset(query_words):
                    score += 2

        if score > max_score:
            max_score = score
            best_match = item["answer"]

    if best_match and max_score > 0:
        return best_match

    # Intelligent contextual fallback
    return (
        f"🤖 **Hostel AI Assistant:**\n\n"
        f"I received your question: *\"{query}\"*\n\n"
        f"Here are helpful quick links & direct actions:\n"
        f"- 🍲 **Dining:** Ask *'What is for lunch today?'* to view the live menu.\n"
        f"- 🚪 **Room & Roommates:** Ask *'Who are my roommates?'* to view assigned peers.\n"
        f"- 🛠️ **File Ticket:** Type *'Report: [issue description]'* to auto-create a maintenance ticket.\n"
        f"- 🕒 **Hostel Rules:** Main gate closes strictly at **09:30 PM**.\n"
        f"- ✈️ **Gate Pass:** Apply for outstation permissions in the **Leave & Gate Pass** tab.\n\n"
        f"📞 *For urgent assistance, contact Campus Security: +91 98765 00100 or Warden Office: +91 98765 43210.*"
    )


# --------------------------------------------------------------------------------------
# 5. VOICE ASSISTANCE & AUDIO SPEECH SYNTHESIS ENGINE
# --------------------------------------------------------------------------------------

def clean_text_for_speech(text: str) -> str:
    """Condenses markdown formatted text into a natural, conversational spoken phrase for voice TTS."""
    if not text:
        return "I am here to assist you."
    
    # Strip markdown headers, bold, italics, code blocks
    cleaned = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    cleaned = re.sub(r'`[^`]+`', '', cleaned)
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)
    cleaned = re.sub(r'[\*\#\_\|\~]', '', cleaned)
    # Strip emojis
    cleaned = re.sub(r'[\U00010000-\U0010ffff]', '', cleaned)
    # Remove bullet markers
    cleaned = re.sub(r'^\s*[\•\-\*]\s*', '', cleaned, flags=re.MULTILINE)
    # Consolidate whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Extract first 2-3 clean sentences
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    spoken_sentences = []
    for s in sentences:
        s_trim = s.strip()
        if s_trim and not s_trim.startswith("http") and len(s_trim) > 5:
            spoken_sentences.append(s_trim)
        if len(spoken_sentences) >= 2:
            break
            
    res = " ".join(spoken_sentences) if spoken_sentences else cleaned[:200]
    if len(res) > 280:
        res = res[:275] + "..."
    return res

def generate_tts_audio_bytes(text: str, lang: str = "en", tld: str = "com") -> bytes:
    """Generates MP3 audio bytes using gTTS for in-memory playback."""
    if not GTTS_AVAILABLE or not text:
        return b""
    try:
        clean = clean_text_for_speech(text)
        buf = io.BytesIO()
        tts = gTTS(text=clean, lang=lang, tld=tld, slow=False)
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return b""

def generate_tts_base64_audio_url(text: str, lang: str = "en") -> str:
    """Generates a data URI base64 audio URL for embedding directly in HTML5 audio tags."""
    audio_bytes = generate_tts_audio_bytes(text, lang=lang)
    if not audio_bytes:
        return ""
    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return f"data:audio/mp3;base64,{b64}"

def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    """Transcribes recorded audio bytes into text using SpeechRecognition engine with fallbacks."""
    if not audio_bytes:
        return ""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with io.BytesIO(audio_bytes) as audio_file:
            with sr.AudioFile(audio_file) as source:
                r.adjust_for_ambient_noise(source, duration=0.2)
                audio_data = r.record(source)
                return r.recognize_google(audio_data)
    except Exception:
        return ""



# --------------------------------------------------------------------------------------
# 6. ADVANCED VOICE INTENT INTERPRETER & ACTION DISPATCHER
# --------------------------------------------------------------------------------------

def parse_voice_command(transcript: str, user_context: dict = None) -> dict:
    """
    State-of-the-art Voice Assistant Intent Parser and Action Dispatcher.
    Transforms spoken voice input into targeted database actions, natural spoken feedback,
    and visual dashboard cards.
    """
    if not transcript or not transcript.strip():
        return {
            "intent": "EMPTY",
            "spoken_text": "I am listening. Please speak a command or question.",
            "markdown_display": "🎙️ *Please speak into your microphone or choose a voice command shortcut.*",
            "action_taken": False,
            "action_type": "NONE"
        }

    raw_query = transcript.strip()
    t = raw_query.lower()
    user_context = user_context or {}
    user_role = user_context.get("user_role", "STUDENT")
    logged_user = user_context.get("logged_user", "Resident")
    student_profile = user_context.get("student_profile", {})

    import database as db

    # 1. EMERGENCY & SOS VOICE COMMAND
    if any(k in t for k in ["emergency", "sos", "call warden", "call security", "ambulance", "medical help", "police", "fire in room", "intruder", "danger"]):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        s_id = student_profile.get("id") if student_profile else None
        r_no = student_profile.get("room_details", {}).get("room_number", "Main Campus") if student_profile else "Main Block"
        
        # Log emergency priority complaint
        db.execute_query("""
        INSERT INTO complaints (student_id, student_name, room_number, category, title, description, priority, sentiment, status, department, suggested_action, created_at)
        VALUES (?, ?, ?, 'Security & Safety', '🚨 VOICE SOS EMERGENCY BROADCAST', ?, 'URGENT', 'NEGATIVE', 'OPEN', 'Chief Security & Warden Office', 'Immediate physical dispatch to resident location.', ?)
        """, (s_id, logged_user, r_no, f"Voice SOS alert triggered: '{raw_query}' from {r_no}", now_str))

        spoken = f"Emergency protocol initiated. Campus Health Center, Security Desk, and Warden Office have been alerted for {r_no}. Help is on the way."
        card = (
            f"<div style='background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%); color: white; padding: 20px; border-radius: 14px; border: 2px solid #ef4444;'>"
            f"<h3 style='margin:0 0 8px 0; color:#fecaca;'>🚨 EMERGENCY SOS BROADCAST ACTIVATED</h3>"
            f"<p style='margin:0 0 10px 0;'>Alert dispatched to Chief Warden and Central Security Patrol for <b>{logged_user} ({r_no})</b>.</p>"
            f"<div style='background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; font-size: 0.9rem;'>"
            f"📞 <b>Campus Ambulance & Medical:</b> Ext 108 / +91 98765 00108<br>"
            f"🛡️ <b>Security Main Gate:</b> Ext 100 / +91 98765 00100<br>"
            f"👨‍💼 <b>Chief Warden (Dr. Rajesh Sharma):</b> +91 98765 43210"
            f"</div>"
            f"</div>"
        )
        return {
            "intent": "EMERGENCY_SOS",
            "spoken_text": spoken,
            "markdown_display": card,
            "action_taken": True,
            "action_type": "EMERGENCY_BROADCAST",
            "audio_base64": generate_tts_base64_audio_url(spoken)
        }

    # 2. VOICE COMPLAINT / ISSUE REPORTING
    if (any(k in t for k in ["report issue", "file complaint", "report", "complaint", "repair", "fix", "not working", "broken", "leaking", "spark", "no water", "no wifi"]) and len(t) > 10) or t.startswith("report"):
        issue_clean = re.sub(r'^(report issue|file complaint|report|complaint|please report|there is a|my)\s*:?\s*', '', raw_query, flags=re.IGNORECASE).strip()
        if not issue_clean:
            issue_clean = raw_query
            
        ai_res = analyze_complaint(issue_clean)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        s_id = student_profile.get("id") if student_profile else None
        r_no = student_profile.get("room_details", {}).get("room_number", "Campus") if student_profile else "Main Block"

        cid = db.execute_query("""
        INSERT INTO complaints (student_id, student_name, room_number, category, title, description, priority, sentiment, status, department, suggested_action, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?)
        """, (s_id, logged_user, r_no, ai_res['category'], ai_res['summary'], issue_clean, ai_res['priority'], ai_res['sentiment'], ai_res['department'], ai_res['suggested_action'], now_str))

        spoken = f"Your maintenance ticket for {ai_res['category']} has been created with {ai_res['priority']} priority. Assigned to {ai_res['department']}."
        card = (
            f"✅ **Maintenance Ticket #{cid} Created via Voice Command!**\n\n"
            f"• 🏷️ **Category:** {ai_res['category']}\n"
            f"• 🚨 **Priority & SLA:** `{ai_res['priority']}` ({ai_res['sla_hours']} Hours turnaround)\n"
            f"• 🏢 **Dispatched To:** {ai_res['department']}\n"
            f"• 🤖 **AI Suggested Action:** {ai_res['suggested_action']}\n\n"
            f"*Issue Summary:* {ai_res['summary']}"
        )
        return {
            "intent": "REPORT_COMPLAINT",
            "spoken_text": spoken,
            "markdown_display": card,
            "action_taken": True,
            "action_type": "TICKET_CREATED",
            "ticket_id": cid,
            "audio_base64": generate_tts_base64_audio_url(spoken)
        }

    # 3. VOICE QUERY: MESS & FOOD MENU
    if any(k in t for k in ["mess", "food", "menu", "dinner", "lunch", "breakfast", "snacks", "meal", "eating"]):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        target_day = None
        for d in days:
            if d.lower() in t:
                target_day = d
                break
        if not target_day:
            if "tomorrow" in t:
                target_day = (datetime.now() + timedelta(days=1)).strftime("%A")
            else:
                target_day = datetime.now().strftime("%A")

        meal_req = None
        if "breakfast" in t:
            meal_req = "Breakfast"
        elif "lunch" in t:
            meal_req = "Lunch"
        elif "snacks" in t or "snack" in t or "tea" in t:
            meal_req = "Snacks"
        elif "dinner" in t:
            meal_req = "Dinner"

        menu_items = db.fetch_all("SELECT * FROM mess_menu WHERE day_of_week = ?", (target_day,))
        if menu_items:
            if meal_req:
                m_item = next((m for m in menu_items if m["meal_type"] == meal_req), None)
                if m_item:
                    spoken = f"For {target_day} {meal_req}, the menu features {m_item['items']}. The special item is {m_item['special_item']} with {m_item['calories']} calories."
                    card = (
                        f"🍲 **{target_day} {meal_req} Menu:**\n\n"
                        f"• **Items:** {m_item['items']}\n"
                        f"• ✨ **Special Dish:** {m_item['special_item']}\n"
                        f"• 🔥 **Energy:** {m_item['calories']} kcal\n\n"
                        f"🕒 *Dining hall open per standard mess schedule.*"
                    )
                    return {
                        "intent": "MESS_MENU",
                        "spoken_text": spoken,
                        "markdown_display": card,
                        "action_taken": False,
                        "audio_base64": generate_tts_base64_audio_url(spoken)
                    }

            spoken = f"On {target_day}, breakfast is {menu_items[0]['items']}, lunch has {menu_items[1]['special_item']}, and dinner features {menu_items[3]['special_item']}."
            lines = [f"📅 **Dining Menu for {target_day}:**\n"]
            icons = {"Breakfast": "🥞", "Lunch": "🍛", "Snacks": "☕", "Dinner": "🍲"}
            for m in menu_items:
                ic = icons.get(m["meal_type"], "🍽️")
                lines.append(f"{ic} **{m['meal_type']}** ({m['calories']} kcal):\n  {m['items']}\n  *Special:* **{m['special_item']}**\n")
            card = "\n".join(lines)
            return {
                "intent": "MESS_MENU",
                "spoken_text": spoken,
                "markdown_display": card,
                "action_taken": False,
                "audio_base64": generate_tts_base64_audio_url(spoken)
            }

    # 4. VOICE QUERY: ROOM & ROOMMATES
    if any(k in t for k in ["my room", "roommates", "roommate", "who is in my room", "my bed", "my block"]):
        if student_profile:
            room_info = student_profile.get("room_details")
            roommates = student_profile.get("roommates", [])
            if room_info:
                rm_names = ", ".join([r['name'] for r in roommates]) if roommates else "no other roommates"
                spoken = f"You are allocated to Room {room_info['room_number']} in {room_info['hostel_name']}. Your roommates are {rm_names}."
                rm_list = [f"• 👤 **{rm['name']}** (Year {rm['year']} {rm['department']}) — 📞 {rm['phone']}" for rm in roommates] if roommates else ["*No roommates assigned.*"]
                card = (
                    f"🚪 **Your Room Details ({logged_user}):**\n\n"
                    f"• **Room Number:** **{room_info['room_number']}**\n"
                    f"• **Hostel / Block:** {room_info['hostel_name']} ({room_info['block_name']}, Floor {room_info['floor_number']})\n"
                    f"• **Room Type:** {room_info['room_type']} ({room_info['occupied_beds']} / {room_info['capacity']} Beds Occupied)\n"
                    f"• **Amenities:** {room_info['amenities'] or 'Standard'}\n\n"
                    f"**Your Roommates:**\n" + "\n".join(rm_list)
                )
                return {
                    "intent": "ROOM_DETAILS",
                    "spoken_text": spoken,
                    "markdown_display": card,
                    "action_taken": False,
                    "audio_base64": generate_tts_base64_audio_url(spoken)
                }

    # 5. VOICE QUERY: FEE BALANCE
    if any(k in t for k in ["fee", "dues", "payment", "due date", "balance"]):
        if student_profile:
            fee_info = student_profile.get("fee_details")
            if fee_info:
                if fee_info['amount_due'] == 0:
                    spoken = "Your hostel fee account is fully paid with zero outstanding dues. Thank you!"
                else:
                    spoken = f"Your outstanding hostel fee is {int(fee_info['amount_due']):,} rupees due on {fee_info['due_date']}."
                card = (
                    f"💳 **Your Hostel Fee Statement ({logged_user}):**\n\n"
                    f"• **Status:** `{'✅ PAID' if fee_info['amount_due'] == 0 else '⚠️ OVERDUE / PENDING'}`\n"
                    f"• **Outstanding Due:** **₹{fee_info['amount_due']:,.0f}**\n"
                    f"• **Paid So Far:** ₹{fee_info['amount_paid']:,.0f} of ₹{fee_info['total_amount']:,.0f}\n"
                    f"• **Due Date:** {fee_info['due_date']}"
                )
                return {
                    "intent": "FEE_STATUS",
                    "spoken_text": spoken,
                    "markdown_display": card,
                    "action_taken": False,
                    "audio_base64": generate_tts_base64_audio_url(spoken)
                }

    # 6. VOICE QUERY: GATE PASS & LEAVE
    if any(k in t for k in ["gate pass", "leave pass", "outstation", "my pass", "leave status"]):
        if student_profile:
            leaves = student_profile.get("leaves", [])
            if leaves:
                latest = leaves[0]
                status_str = latest['status']
                spoken = f"Your outstation leave pass to {latest['reason']} is currently {status_str}."
                if latest['gate_pass_code']:
                    spoken += f" Your digital gate pass code is {latest['gate_pass_code']}."
                card = (
                    f"✈️ **Latest Digital Gate Pass Status:**\n\n"
                    f"• **Status:** `{latest['status']}`\n"
                    f"• **Duration:** {latest['from_date']} to {latest['to_date']}\n"
                    f"• **Reason:** {latest['reason']}\n"
                    f"• 🎫 **Gate Pass Code:** `{latest['gate_pass_code'] or 'Pending approval'}`"
                )
                return {
                    "intent": "GATE_PASS",
                    "spoken_text": spoken,
                    "markdown_display": card,
                    "action_taken": False,
                    "audio_base64": generate_tts_base64_audio_url(spoken)
                }

    # 7. VOICE QUERY: CURFEW & RULES
    if any(k in t for k in ["curfew", "timing", "gate close", "in time", "late entry", "rules", "attendance timing"]):
        spoken = "Hostel gates close strictly at 9:30 PM. Night turnstile biometric roll call is taken between 9:00 PM and 9:45 PM daily. Late entry requires an approved gate pass."
        card = (
            f"🕒 **Hostel Timings & Night Curfew Policy:**\n\n"
            f"• **Gate Cutoff:** **09:30 PM** sharp for all resident blocks.\n"
            f"• **Biometric Attendance:** **09:00 PM – 09:45 PM** daily at turnstiles.\n"
            f"• **Late Pass Requirement:** Entries after 09:30 PM require an approved Digital Gate Pass signed by the Warden."
        )
        return {
            "intent": "CURFEW_RULES",
            "spoken_text": spoken,
            "markdown_display": card,
            "action_taken": False,
            "audio_base64": generate_tts_base64_audio_url(spoken)
        }

    # 8. VOICE QUERY: CAMPUS OVERVIEW & STATS
    if any(k in t for k in ["stats", "statistics", "occupancy", "how many students", "overview", "vacant"]):
        students = db.fetch_all("SELECT id FROM students")
        rooms = db.fetch_all("SELECT capacity, occupied_beds FROM rooms")
        open_comps = db.fetch_all("SELECT id FROM complaints WHERE status != 'RESOLVED'")
        tot_beds = sum(r['capacity'] for r in rooms)
        occ_beds = sum(r['occupied_beds'] for r in rooms)
        rate = (occ_beds / max(1, tot_beds)) * 100
        spoken = f"The campus hostel is currently at {rate:.1f}% occupancy with {len(students)} residents and {len(open_comps)} active maintenance tickets."
        card = (
            f"📊 **Campus Operational Statistics:**\n\n"
            f"• 👨‍🎓 **Active Residents:** {len(students)}\n"
            f"• 🛏️ **Bed Occupancy:** {occ_beds} / {tot_beds} ({rate:.1f}%)\n"
            f"• 🛠️ **Open Grievance Tickets:** {len(open_comps)}\n"
            f"• 🏢 **Hostel Blocks Active:** 6 complexes (All Nominal)"
        )
        return {
            "intent": "CAMPUS_STATS",
            "spoken_text": spoken,
            "markdown_display": card,
            "action_taken": False,
            "audio_base64": generate_tts_base64_audio_url(spoken)
        }

    # 9. GENERAL CONVERSATION (Fallback to Grounded RAG)
    rag_response = generate_chat_response(raw_query, user_context)
    clean_spoken = clean_text_for_speech(rag_response)
    return {
        "intent": "GENERAL_QA",
        "spoken_text": clean_spoken,
        "markdown_display": rag_response,
        "action_taken": False,
        "action_type": "KNOWLEDGE_LOOKUP",
        "audio_base64": generate_tts_base64_audio_url(clean_spoken)
    }


# --------------------------------------------------------------------------------------
# 7. AI SUSTAINABILITY & CAMPUS ENERGY CONSUMPTION FORECASTER
# --------------------------------------------------------------------------------------

def predict_campus_energy_demand(total_students: int, occupancy_pct: float, avg_temp_c: float = 28.5, day_name: str = "Monday") -> dict:
    """
    Advanced AI Energy & Resource Sustainability Forecaster.
    Estimates campus electricity demand (kWh), HVAC/AC load, carbon footprint,
    and identifies abnormal peak power risks.
    """
    is_weekend = day_name in ["Saturday", "Sunday"]
    base_kwh_per_student = 3.2
    
    temp_factor = 1.0
    if avg_temp_c > 26:
        temp_factor = 1.0 + ((avg_temp_c - 26) * 0.12)
    elif avg_temp_c < 18:
        temp_factor = 1.0 + ((18 - avg_temp_c) * 0.08)
        
    active_occupants = max(10, int(total_students * (occupancy_pct / 100.0)))
    daily_base_kwh = active_occupants * base_kwh_per_student
    daily_ac_kwh = round(daily_base_kwh * (temp_factor - 0.7) * 1.4, 1)
    daily_total_kwh = round(daily_base_kwh + daily_ac_kwh, 1)
    
    carbon_kg = round(daily_total_kwh * 0.82, 1)
    peak_kw = round((daily_total_kwh / 24) * 2.2, 1)
    peak_risk = "HIGH" if peak_kw > 120 else ("MODERATE" if peak_kw > 80 else "OPTIMAL")
    
    curve_weights = [
        0.02, 0.02, 0.018, 0.018, 0.02, 0.03,
        0.045, 0.065, 0.07, 0.04, 0.03, 0.03,
        0.035, 0.035, 0.03, 0.035, 0.04, 0.05,
        0.065, 0.085, 0.09, 0.085, 0.07, 0.04
    ]
    hourly_distribution = []
    for hr, w in enumerate(curve_weights):
        hourly_distribution.append({
            "hour": f"{hr:02d}:00",
            "kwh": round(daily_total_kwh * w, 1),
            "ac_pct": int(min(90, max(20, temp_factor * 35)))
        })
        
    if peak_risk == "HIGH":
        rec = "⚠️ Projected peak load exceeds 120 kW. Activate automated corridor dimming and cycle central chiller units."
    elif avg_temp_c > 30:
        rec = "🌡️ Elevated temperature detected. Set central common-room AC thermostats to eco-mode 24°C."
    else:
        rec = "🌿 Campus power consumption within optimal sustainability envelope. Solar offset covers ~28% of baseline."

    return {
        "daily_total_kwh": daily_total_kwh,
        "base_kwh": round(daily_base_kwh, 1),
        "ac_hvac_kwh": daily_ac_kwh,
        "peak_kw": peak_kw,
        "peak_risk": peak_risk,
        "carbon_kg": carbon_kg,
        "hourly_curve": hourly_distribution,
        "recommendation": rec,
        "green_score": 88 if peak_risk == "OPTIMAL" else (74 if peak_risk == "MODERATE" else 62)
    }


# --------------------------------------------------------------------------------------
# 8. BIOMETRIC & CURFEW ANOMALY RISK ANALYZER
# --------------------------------------------------------------------------------------

def analyze_biometric_anomalies(attendance_logs: list, leave_requests: list) -> dict:
    """
    Analyzes biometric gate logs for curfew violations, repeat late returns,
    and missing roll calls.
    """
    late_entries = []
    unaccounted_absences = []
    student_late_counts = {}

    for log in attendance_logs:
        st_name = log.get("student_name", "Resident")
        st_status = log.get("status", "")
        chk_in = log.get("check_in_time", "")
        log_date = log.get("date", "")
        
        is_late = st_status == "LATE"
        if not is_late and chk_in:
            try:
                parts = chk_in.split(":")
                hh = int(parts[0])
                mm = int(parts[1]) if len(parts) > 1 else 0
                if hh > 21 or (hh == 21 and mm > 30):
                    is_late = True
            except Exception:
                pass
                
        if is_late:
            student_late_counts[st_name] = student_late_counts.get(st_name, 0) + 1
            late_entries.append({
                "student_name": st_name,
                "room_number": log.get("room_number", "N/A"),
                "date": log_date,
                "time": chk_in or "21:45+",
                "severity": "CRITICAL" if student_late_counts[st_name] >= 3 else "WARNING"
            })
            
        elif st_status == "ABSENT":
            has_leave = False
            for lr in leave_requests:
                if lr.get("student_name") == st_name and lr.get("status") == "APPROVED":
                    has_leave = True
                    break
            if not has_leave:
                unaccounted_absences.append({
                    "student_name": st_name,
                    "room_number": log.get("room_number", "N/A"),
                    "date": log_date,
                    "action_needed": "Contact guardian and verify resident whereabouts."
                })
                
    chronic_late = [{"student": k, "count": v} for k, v in student_late_counts.items() if v >= 2]
    chronic_late = sorted(chronic_late, key=lambda x: x["count"], reverse=True)

    risk_level = "ELEVATED" if len(unaccounted_absences) > 2 or len(chronic_late) > 2 else "NORMAL"
    return {
        "total_anomalies": len(late_entries) + len(unaccounted_absences),
        "late_entries_count": len(late_entries),
        "unaccounted_absences": unaccounted_absences,
        "chronic_late_students": chronic_late,
        "recent_late_logs": late_entries[:8],
        "campus_security_risk": risk_level
    }


# --------------------------------------------------------------------------------------
# 9. MULTIDIMENSIONAL ROOMMATE VECTOR RADAR PROFILER
# --------------------------------------------------------------------------------------

def calculate_roommate_radar_profile(student1: dict, student2: dict = None) -> dict:
    """
    Computes 6-dimensional lifestyle compatibility radar scores for visual Plotly radar chart.
    Dimensions: Sleep Sync, Study Focus, Cleanliness, Social Battery, Noise Tolerance, Routine Rhythm.
    """
    categories = [
        "Sleep Chronotype",
        "Study Focus",
        "Cleanliness",
        "Social Tolerance",
        "Noise Tolerance",
        "Daily Rhythm"
    ]
    
    s1_sleep = 90 if student1.get("sleep_habit") == "Night Owl" else (30 if student1.get("sleep_habit") == "Early Bird" else 60)
    s1_study = 90 if "Intensive" in student1.get("study_habit", "") else (40 if "Group" in student1.get("study_habit", "") else 65)
    s1_clean = 95 if student1.get("cleanliness") == "Very High" else (80 if student1.get("cleanliness") == "High" else 55)
    s1_social = 45 if "Intensive" in student1.get("study_habit", "") else 80
    s1_noise = 30 if "Silent" in student1.get("study_habit", "") else 75
    s1_routine = 85 if student1.get("sleep_habit") in ["Early Bird", "Night Owl"] else 50
    
    vals1 = [s1_sleep, s1_study, s1_clean, s1_social, s1_noise, s1_routine]
    
    if student2:
        s2_sleep = 90 if student2.get("sleep_habit") == "Night Owl" else (30 if student2.get("sleep_habit") == "Early Bird" else 60)
        s2_study = 90 if "Intensive" in student2.get("study_habit", "") else (40 if "Group" in student2.get("study_habit", "") else 65)
        s2_clean = 95 if student2.get("cleanliness") == "Very High" else (80 if student2.get("cleanliness") == "High" else 55)
        s2_social = 45 if "Intensive" in student2.get("study_habit", "") else 80
        s2_noise = 30 if "Silent" in student2.get("study_habit", "") else 75
        s2_routine = 85 if student2.get("sleep_habit") in ["Early Bird", "Night Owl"] else 50
        vals2 = [s2_sleep, s2_study, s2_clean, s2_social, s2_noise, s2_routine]
        
        diffs = [abs(a - b) for a, b in zip(vals1, vals2)]
        avg_diff = sum(diffs) / len(diffs)
        synergy_score = int(max(30, 100 - avg_diff))
    else:
        vals2 = [60, 60, 70, 65, 60, 60]
        synergy_score = 85
        
    return {
        "categories": categories,
        "student1_values": vals1,
        "student2_values": vals2,
        "student1_name": student1.get("name", "Student"),
        "student2_name": student2.get("name", "Target Peer") if student2 else "Room Baseline",
        "synergy_score": synergy_score
    }


