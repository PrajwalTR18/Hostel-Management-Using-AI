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

