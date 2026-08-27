"""
AI Engine for Advanced Hostel Management System
Includes NLP Complaint Analysis, Smart Room Compatibility Matching, 
Predictive Analytics (Food Demand, Fee Risk, Attendance Anomaly), and Conversational AI Assistant.
"""

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
# 4. CONVERSATIONAL AI HOSTEL ASSISTANT
# --------------------------------------------------------------------------------------

HOSTEL_KNOWLEDGE_BASE = [
    {
        "keywords": ["curfew", "night", "timing", "gate close", "in-time", "late"],
        "answer": "🕒 **Hostel Timings & Curfew Rules:**\n- Main campus gate closes at **09:30 PM** for all resident blocks.\n- Night biometric attendance roll call is taken between **09:00 PM - 09:45 PM**.\n- Late entries require a valid digital Gate Pass pre-approved by your Block Warden. Repeat unauthorized late entries incur fine and parent notification."
    },
    {
        "keywords": ["leave", "gate pass", "outstation", "home", "permission", "vacation"],
        "answer": "✈️ **Leave & Gate Pass Application Process:**\n1. Go to the **Leave / Gate Pass** tab on the left sidebar.\n2. Submit your departure date, return date, and destination reason.\n3. Your Warden receives the request in real-time. Once approved, an instant **QR Code Gate Pass** is generated.\n4. Scan this QR code with the security turnstile at the main entrance."
    },
    {
        "keywords": ["complaint", "repair", "plumber", "electrician", "wifi not working", "leak", "clean"],
        "answer": "🛠️ **Filing & Tracking Maintenance Complaints:**\n- Navigate to the **AI Complaints & Maintenance** section.\n- Type your issue in natural language (e.g. *'Wi-Fi router in floor 2 is dropping packets'* or *'Washbasin tap leaking'*).\n- Our **NLP AI Triage Engine** automatically categorizes the issue, determines urgency, and dispatches the duty technician within SLA."
    },
    {
        "keywords": ["mess", "food", "menu", "timings", "meal", "breakfast", "dinner", "lunch"],
        "answer": "🍲 **Mess Timings & Dining Schedule:**\n- **Breakfast:** 07:30 AM – 09:15 AM\n- **Lunch:** 12:30 PM – 02:15 PM\n- **Evening Snacks:** 05:00 PM – 06:15 PM\n- **Dinner:** 07:45 PM – 09:30 PM\nCheck the **Mess & Dining** tab to view today's complete nutritional menu and Sunday special polls."
    },
    {
        "keywords": ["fee", "payment", "due", "dues", "installment", "receipt", "fine"],
        "answer": "💳 **Hostel Fee & Payment Guidelines:**\n- Semester room & mess fees must be cleared by the 15th of the start month.\n- View your breakdown and download digital receipts in the **Fee & Accounts** tab.\n- Online payment modes include UPI, Net Banking, and Debit/Credit card."
    },
    {
        "keywords": ["room change", "swap", "allocate", "single room", "roommate"],
        "answer": "🎯 **Room Allocation & Swap Requests:**\n- Room changes are processed at the start of each semester via our **AI Compatibility Matching Engine**.\n- You can explore available rooms in the **AI Room Allocation** module and submit a preferred allocation request to the Chief Warden."
    },
    {
        "keywords": ["emergency", "warden contact", "medical", "doctor", "ambulance", "security", "fire", "help"],
        "answer": "🚨 **Emergency Assistance Directory:**\n- 🏥 **Campus Medical Centre / Ambulance:** Ext: 108 / +91 98765 00108 (24x7)\n- 👨‍💼 **Chief Boys Warden (Dr. Rajesh Sharma):** +91 98765 43210\n- 👩‍💼 **Chief Girls Warden (Dr. Sunita Verma):** +91 98765 43211\n- 🛡️ **Main Security Gate Control Room:** Ext: 100 / +91 98765 00100"
    },
    {
        "keywords": ["wifi", "internet", "password", "lan", "speed", "login"],
        "answer": "📶 **Campus Wi-Fi & Network Access:**\n- SSID: **CAMPUS_HOSTEL_5G** / **CAMPUS_HOSTEL_2.4G**\n- Login: Enter your Student ID (`STU-XXXX`) and campus portal password on the captive portal.\n- For dedicated high-bandwidth LAN ports in study rooms, register your MAC address at the IT Helpdesk."
    }
]

def generate_chat_response(query: str, api_url: str = None, api_key: str = None, model_name: str = "gpt-4.1-mini") -> str:
    """
    Answers student or administrator queries using LLM if configured, 
    or built-in AI retrieval engine.
    """
    q_clean = query.strip().lower()

    # If external AI API is configured
    if api_url and api_key and api_url.startswith("http"):
        try:
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are the AI Assistant for the Smart University Hostel Management System. Answer questions politely, accurately, and clearly about hostel rules, room allocations, mess, leave gate passes, complaints, and campus amenities."
                    },
                    {"role": "user", "content": query}
                ]
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
            pass # Fall back to local knowledge engine

    # Local Knowledge Engine Matching
    best_match = None
    max_hits = 0

    for item in HOSTEL_KNOWLEDGE_BASE:
        hits = sum(1 for kw in item["keywords"] if kw in q_clean)
        if hits > max_hits:
            max_hits = hits
            best_match = item["answer"]

    if best_match and max_hits > 0:
        return best_match

    # General intelligent fallback
    return (
        f"🤖 **Hostel AI Assistant:**\n\n"
        f"I understand you are asking about: *'{query}'*.\n\n"
        f"Here are quick shortcuts to assist you:\n"
        f"- 📋 **Complaints:** Submit a ticket with NLP triage in the *Complaints* tab.\n"
        f"- ✈️ **Gate Pass:** Apply for outstation pass in the *Leave Management* tab.\n"
        f"- 🍲 **Mess:** View today's meal schedule in the *Mess & Dining* tab.\n"
        f"- 🏢 **Rooms:** View room vacancy & AI match score in *Room Allocation*.\n\n"
        f"For urgent assistance, contact the Warden Office or Security Control Desk (+91 98765 00100)."
    )
