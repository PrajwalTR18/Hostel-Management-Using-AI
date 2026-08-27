"""
Database Layer for AI-Based Hostel Management System
Provides SQLite schema setup, seeding with realistic demo records, and query helper functions.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
import random

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hostel_database.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hostels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL, -- Boys / Girls
        capacity INTEGER NOT NULL,
        address TEXT,
        warden_name TEXT,
        contact TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostel_name TEXT NOT NULL,
        block_name TEXT NOT NULL,
        floor_number INTEGER NOT NULL,
        room_number TEXT NOT NULL UNIQUE,
        room_type TEXT NOT NULL, -- Single, Double, Triple, Quad
        capacity INTEGER NOT NULL,
        occupied_beds INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'AVAILABLE', -- AVAILABLE, PARTIALLY_OCCUPIED, FULL, MAINTENANCE
        rent_per_month REAL NOT NULL,
        amenities TEXT -- e.g. "AC, Attached Bath, Balcony"
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        gender TEXT NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        room_id INTEGER,
        sleep_habit TEXT DEFAULT 'Flexible', -- 'Early Bird', 'Night Owl', 'Flexible'
        study_habit TEXT DEFAULT 'Moderate', -- 'Silent / Intensive', 'Group / Music', 'Moderate'
        cleanliness TEXT DEFAULT 'High', -- 'Very High', 'High', 'Moderate'
        dietary_pref TEXT DEFAULT 'Veg', -- 'Veg', 'Non-Veg', 'Eggetarian'
        fee_status TEXT DEFAULT 'PAID', -- 'PAID', 'PARTIAL', 'PENDING'
        parent_name TEXT,
        parent_phone TEXT,
        FOREIGN KEY (room_id) REFERENCES rooms(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        student_name TEXT NOT NULL,
        room_number TEXT NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        priority TEXT NOT NULL, -- URGENT, HIGH, MEDIUM, LOW
        sentiment TEXT NOT NULL, -- POSITIVE, NEUTRAL, NEGATIVE
        status TEXT NOT NULL DEFAULT 'OPEN', -- OPEN, IN_PROGRESS, RESOLVED, CLOSED
        department TEXT NOT NULL,
        suggested_action TEXT,
        created_at TEXT NOT NULL,
        resolved_at TEXT,
        assigned_to TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        room_number TEXT,
        date TEXT NOT NULL,
        status TEXT NOT NULL, -- PRESENT, ABSENT, ON_LEAVE, LATE
        check_in_time TEXT,
        check_out_time TEXT,
        marked_by TEXT DEFAULT 'Warden Biometric',
        FOREIGN KEY (student_id) REFERENCES students(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        room_number TEXT,
        reason TEXT NOT NULL,
        from_date TEXT NOT NULL,
        to_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
        approved_by TEXT,
        gate_pass_code TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fee_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        total_amount REAL NOT NULL,
        amount_paid REAL NOT NULL,
        amount_due REAL NOT NULL,
        due_date TEXT NOT NULL,
        status TEXT NOT NULL, -- PAID, OVERDUE, PARTIAL, PENDING
        last_payment_date TEXT,
        transaction_ref TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mess_menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day_of_week TEXT NOT NULL,
        meal_type TEXT NOT NULL, -- Breakfast, Lunch, Snacks, Dinner
        items TEXT NOT NULL,
        special_item TEXT,
        calories INTEGER
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        student_name TEXT NOT NULL,
        visitor_name TEXT NOT NULL,
        relation TEXT NOT NULL,
        phone TEXT NOT NULL,
        entry_time TEXT NOT NULL,
        exit_time TEXT,
        purpose TEXT,
        status TEXT DEFAULT 'IN_PREMISES', -- IN_PREMISES, CHECKED_OUT
        FOREIGN KEY (student_id) REFERENCES students(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT NOT NULL, -- General, Emergency, Maintenance, Event, Mess
        priority TEXT NOT NULL, -- URGENT, HIGH, NORMAL
        target_audience TEXT DEFAULT 'All Students',
        posted_by TEXT NOT NULL,
        posted_at TEXT NOT NULL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL, -- ADMIN, WARDEN, STUDENT, SECURITY
        full_name TEXT NOT NULL,
        email TEXT,
        student_id INTEGER
    )""")

    conn.commit()

    # Seed if tables are empty
    cursor.execute("SELECT COUNT(*) FROM hostels")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()

    # Hostels
    cursor.executemany("""
    INSERT INTO hostels (name, type, capacity, address, warden_name, contact) VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ("Aryabhata Block (Boys)", "Boys", 200, "North Campus, Sector 4", "Dr. Rajesh Sharma", "+91 98765 43210"),
        ("Gargi Bhavan (Girls)", "Girls", 180, "South Campus, Sector 2", "Dr. Sunita Verma", "+91 98765 43211"),
        ("CV Raman Hall (Boys PG)", "Boys", 120, "East Campus, Sector 5", "Prof. Anand Nair", "+91 98765 43212")
    ])

    # Rooms
    rooms_data = [
        # Aryabhata Block
        ("Aryabhata Block (Boys)", "Block A", 1, "A-101", "Single", 1, 1, "FULL", 8500, "AC, Attached Bath, High-Speed WiFi"),
        ("Aryabhata Block (Boys)", "Block A", 1, "A-102", "Double", 2, 2, "FULL", 6500, "AC, Attached Bath, Balcony"),
        ("Aryabhata Block (Boys)", "Block A", 1, "A-103", "Double", 2, 1, "PARTIALLY_OCCUPIED", 6500, "Attached Bath, WiFi"),
        ("Aryabhata Block (Boys)", "Block A", 1, "A-104", "Triple", 3, 2, "PARTIALLY_OCCUPIED", 5000, "Common Bath, Study Table"),
        ("Aryabhata Block (Boys)", "Block A", 1, "A-105", "Triple", 3, 0, "AVAILABLE", 5000, "Common Bath, Balcony"),
        ("Aryabhata Block (Boys)", "Block A", 2, "A-201", "Single", 1, 0, "AVAILABLE", 8500, "AC, Attached Bath"),
        ("Aryabhata Block (Boys)", "Block A", 2, "A-202", "Double", 2, 1, "PARTIALLY_OCCUPIED", 6500, "AC, Attached Bath"),
        ("Aryabhata Block (Boys)", "Block A", 2, "A-203", "Double", 2, 0, "MAINTENANCE", 6500, "Attached Bath (Under Repair)"),
        ("Aryabhata Block (Boys)", "Block B", 1, "B-101", "Double", 2, 2, "FULL", 6200, "Attached Bath, Study Table"),
        ("Aryabhata Block (Boys)", "Block B", 1, "B-102", "Triple", 3, 1, "PARTIALLY_OCCUPIED", 4800, "Common Bath, Balcony"),
        
        # Gargi Bhavan
        ("Gargi Bhavan (Girls)", "Block G1", 1, "G-101", "Single", 1, 1, "FULL", 8800, "AC, Attached Bath, Garden View"),
        ("Gargi Bhavan (Girls)", "Block G1", 1, "G-102", "Double", 2, 2, "FULL", 6800, "AC, Attached Bath"),
        ("Gargi Bhavan (Girls)", "Block G1", 1, "G-103", "Double", 2, 1, "PARTIALLY_OCCUPIED", 6800, "Attached Bath, WiFi"),
        ("Gargi Bhavan (Girls)", "Block G1", 2, "G-201", "Double", 2, 0, "AVAILABLE", 6800, "AC, Attached Bath, Balcony"),
        ("Gargi Bhavan (Girls)", "Block G1", 2, "G-202", "Triple", 3, 2, "PARTIALLY_OCCUPIED", 5200, "Attached Bath, Study Lamps"),
        
        # CV Raman Hall
        ("CV Raman Hall (Boys PG)", "Block R", 1, "R-101", "Single", 1, 1, "FULL", 9500, "AC, Attached Bath, Refrigerator"),
        ("CV Raman Hall (Boys PG)", "Block R", 1, "R-102", "Single", 1, 0, "AVAILABLE", 9500, "AC, Attached Bath, Refrigerator")
    ]
    cursor.executemany("""
    INSERT INTO rooms (hostel_name, block_name, floor_number, room_number, room_type, capacity, occupied_beds, status, rent_per_month, amenities)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rooms_data)

    # Students
    students_data = [
        ("STU-1001", "Aarav Sharma", "aarav.sharma@campus.edu", "+91 91234 56781", "Male", "Computer Science", 3, 1, "Night Owl", "Silent / Intensive", "Very High", "Veg", "PAID", "Ramesh Sharma", "+91 98111 22231"),
        ("STU-1002", "Vikramaditya Roy", "vikram.roy@campus.edu", "+91 91234 56782", "Male", "Information Science", 3, 2, "Early Bird", "Moderate", "High", "Non-Veg", "PAID", "Debashis Roy", "+91 98111 22232"),
        ("STU-1003", "Rohan Kulkarni", "rohan.k@campus.edu", "+91 91234 56783", "Male", "Electronics & Comm", 2, 2, "Early Bird", "Moderate", "High", "Veg", "PAID", "Suresh Kulkarni", "+91 98111 22233"),
        ("STU-1004", "Kabir Mehta", "kabir.m@campus.edu", "+91 91234 56784", "Male", "Mechanical Eng", 1, 3, "Night Owl", "Group / Music", "Moderate", "Non-Veg", "PARTIAL", "Alok Mehta", "+91 98111 22234"),
        ("STU-1005", "Tanmay Deshmukh", "tanmay.d@campus.edu", "+91 91234 56785", "Male", "Computer Science", 2, 4, "Flexible", "Silent / Intensive", "High", "Veg", "PAID", "Nitin Deshmukh", "+91 98111 22235"),
        ("STU-1006", "Ananya Sen", "ananya.sen@campus.edu", "+91 91234 56786", "Female", "Computer Science", 4, 11, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PAID", "Pradip Sen", "+91 98111 22236"),
        ("STU-1007", "Pooja Hegde", "pooja.h@campus.edu", "+91 91234 56787", "Female", "Biotechnology", 2, 12, "Night Owl", "Moderate", "High", "Non-Veg", "PAID", "Venkatesh Hegde", "+91 98111 22237"),
        ("STU-1008", "Sneha Iyer", "sneha.iyer@campus.edu", "+91 91234 56788", "Female", "Information Science", 2, 12, "Night Owl", "Moderate", "High", "Veg", "PAID", "Subramanian Iyer", "+91 98111 22238"),
        ("STU-1009", "Meera Nair", "meera.nair@campus.edu", "+91 91234 56789", "Female", "Electrical Eng", 1, 13, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PENDING", "Gopal Nair", "+91 98111 22239"),
        ("STU-1010", "Devansh Pandey", "devansh.p@campus.edu", "+91 91234 56790", "Male", "Civil Engineering", 3, 9, "Flexible", "Group / Music", "Moderate", "Non-Veg", "PAID", "Harish Pandey", "+91 98111 22240"),
        ("STU-1011", "Kavya Murthy", "kavya.m@campus.edu", "+91 91234 56791", "Female", "Computer Science", 1, None, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PAID", "Narayana Murthy", "+91 98111 22241"),
        ("STU-1012", "Aryan Gupta", "aryan.gupta@campus.edu", "+91 91234 56792", "Male", "Artificial Intelligence", 1, None, "Night Owl", "Silent / Intensive", "High", "Non-Veg", "PAID", "Rajiv Gupta", "+91 98111 22242")
    ]
    cursor.executemany("""
    INSERT INTO students (student_id_code, name, email, phone, gender, department, year, room_id, sleep_habit, study_habit, cleanliness, dietary_pref, fee_status, parent_name, parent_phone)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, students_data)

    # Users for login
    users_data = [
        ("admin", "admin123", "ADMIN", "Chief Hostel Administrator", "admin@hostel.edu", None),
        ("warden_rajesh", "warden123", "WARDEN", "Dr. Rajesh Sharma (Boys Warden)", "warden.boys@hostel.edu", None),
        ("warden_sunita", "warden123", "WARDEN", "Dr. Sunita Verma (Girls Warden)", "warden.girls@hostel.edu", None),
        ("security_gate", "security123", "SECURITY", "Head Security Officer", "security@hostel.edu", None),
        ("aarav", "student123", "STUDENT", "Aarav Sharma", "aarav.sharma@campus.edu", 1),
        ("ananya", "student123", "STUDENT", "Ananya Sen", "ananya.sen@campus.edu", 6)
    ]
    cursor.executemany("""
    INSERT INTO users (username, password, role, full_name, email, student_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """, users_data)

    # Complaints
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    complaints_data = [
        (1, "Aarav Sharma", "A-101", "Plumbing", "Severe bathroom pipe leakage", "The main washbasin pipe is continuously leaking water creating a slippery floor pool.", "HIGH", "NEGATIVE", "IN_PROGRESS", "Maintenance", "Inspect and replace seal ring on basin connection", now_str, None, "Ramu (Plumber)"),
        (2, "Vikramaditya Roy", "A-102", "Internet", "Wi-Fi disconnecting repeatedly during online classes", "The 5GHz access point in floor 1 hallway is restarting every 15 minutes.", "MEDIUM", "NEGATIVE", "OPEN", "Maintenance", "Check AP firmware and power supply PoE", now_str, None, "Suresh (IT Admin)"),
        (6, "Ananya Sen", "G-101", "Electrical", "Tube light flickering and spark near switchboard", "The main room tube light is flickering heavily and buzzing with small sparks.", "URGENT", "NEGATIVE", "OPEN", "Maintenance", "Isolate circuit breaker and replace socket assembly immediately", now_str, None, "Govind (Electrician)"),
        (7, "Pooja Hegde", "G-102", "Food", "Dinner dal was cold and stale smell noticed", "Dinner served yesterday had cold food and rotis were undercooked.", "MEDIUM", "NEGATIVE", "RESOLVED", "Mess", "Audit mess supervisor preparation schedule", (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "Mess In-charge Chef"),
        (10, "Devansh Pandey", "B-101", "Cleaning", "Corridor dustbin not emptied for 2 days", "Common floor wastebin overflowing near room B-101.", "LOW", "NEUTRAL", "RESOLVED", "Hostel Administration", "Dispatch floor housekeeping staff for daily rotation", (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "Cleaning Supervisor")
    ]
    cursor.executemany("""
    INSERT INTO complaints (student_id, student_name, room_number, category, title, description, priority, sentiment, status, department, suggested_action, created_at, resolved_at, assigned_to)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, complaints_data)

    # Attendance (Recent 5 days)
    today = date.today()
    att_data = []
    student_list = [
        (1, "Aarav Sharma", "A-101"),
        (2, "Vikramaditya Roy", "A-102"),
        (3, "Rohan Kulkarni", "A-102"),
        (4, "Kabir Mehta", "A-103"),
        (5, "Tanmay Deshmukh", "A-104"),
        (6, "Ananya Sen", "G-101"),
        (7, "Pooja Hegde", "G-102"),
        (8, "Sneha Iyer", "G-102"),
        (9, "Meera Nair", "G-103"),
        (10, "Devansh Pandey", "B-101")
    ]

    for d_offset in range(5, -1, -1):
        cur_d = (today - timedelta(days=d_offset)).strftime("%Y-%m-%d")
        for s_id, s_name, r_no in student_list:
            rand_val = random.random()
            if rand_val > 0.15:
                status = "PRESENT"
                cin = "20:45"
                cout = "07:30"
            elif rand_val > 0.08:
                status = "LATE"
                cin = "22:15"
                cout = "07:30"
            elif rand_val > 0.03:
                status = "ON_LEAVE"
                cin = None
                cout = None
            else:
                status = "ABSENT"
                cin = None
                cout = None
            att_data.append((s_id, s_name, r_no, cur_d, status, cin, cout, "Smart RFID Turnstile"))

    cursor.executemany("""
    INSERT INTO attendance (student_id, student_name, room_number, date, status, check_in_time, check_out_time, marked_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, att_data)

    # Leave Requests
    leaves = [
        (1, "Aarav Sharma", "A-101", "Attending sister's wedding ceremony in home town", (today + timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=5)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Rajesh Sharma", "GP-2026-8819", now_str),
        (6, "Ananya Sen", "G-101", "Inter-college Hackathon competition in Bengaluru", (today + timedelta(days=1)).strftime("%Y-%m-%d"), (today + timedelta(days=3)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Sunita Verma", "GP-2026-9042", now_str),
        (4, "Kabir Mehta", "A-103", "Medical checkup and family doctor consultation", today.strftime("%Y-%m-%d"), (today + timedelta(days=2)).strftime("%Y-%m-%d"), "PENDING", None, None, now_str),
        (9, "Meera Nair", "G-103", "Weekend trip home", (today + timedelta(days=4)).strftime("%Y-%m-%d"), (today + timedelta(days=6)).strftime("%Y-%m-%d"), "PENDING", None, None, now_str)
    ]
    cursor.executemany("""
    INSERT INTO leave_requests (student_id, student_name, room_number, reason, from_date, to_date, status, approved_by, gate_pass_code, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, leaves)

    # Fee Records
    fee_data = [
        (1, "Aarav Sharma", 45000, 45000, 0, "2026-08-15", "PAID", "2026-08-05", "TXN-998812"),
        (2, "Vikramaditya Roy", 40000, 40000, 0, "2026-08-15", "PAID", "2026-08-10", "TXN-998834"),
        (3, "Rohan Kulkarni", 40000, 40000, 0, "2026-08-15", "PAID", "2026-08-12", "TXN-998855"),
        (4, "Kabir Mehta", 35000, 20000, 15000, "2026-08-15", "PARTIAL", "2026-08-14", "TXN-998877"),
        (5, "Tanmay Deshmukh", 35000, 35000, 0, "2026-08-15", "PAID", "2026-08-01", "TXN-998899"),
        (6, "Ananya Sen", 48000, 48000, 0, "2026-08-15", "PAID", "2026-08-04", "TXN-998901"),
        (7, "Pooja Hegde", 42000, 42000, 0, "2026-08-15", "PAID", "2026-08-09", "TXN-998902"),
        (8, "Sneha Iyer", 42000, 42000, 0, "2026-08-15", "PAID", "2026-08-08", "TXN-998903"),
        (9, "Meera Nair", 42000, 0, 42000, "2026-08-15", "OVERDUE", None, None),
        (10, "Devansh Pandey", 38000, 38000, 0, "2026-08-15", "PAID", "2026-08-02", "TXN-998905")
    ]
    cursor.executemany("""
    INSERT INTO fee_records (student_id, student_name, total_amount, amount_paid, amount_due, due_date, status, last_payment_date, transaction_ref)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fee_data)

    # Mess Menu
    menu_data = [
        ("Monday", "Breakfast", "Masala Dosa, Sambar, Coconut Chutney, Tea/Coffee", "Sprouted Moong", 450),
        ("Monday", "Lunch", "Chapati, Dal Tadka, Paneer Butter Masala, Steamed Rice, Curd", "Gulab Jamun", 750),
        ("Monday", "Snacks", "Veg Cutlet, Green Mint Chutney, Ginger Tea", "Biscuits", 250),
        ("Monday", "Dinner", "Phulka, Mixed Veg Korma, Jeera Rice, Dal Fry, Fresh Fruit", "Custard", 680),
        
        ("Tuesday", "Breakfast", "Idli Vada, Sambar, Tomato Chutney, Filter Coffee", "Boiled Eggs / Banana", 420),
        ("Tuesday", "Lunch", "Poori, Chole Masala, Veg Pulao, Boondi Raita", "Fruit Salad", 800),
        ("Tuesday", "Snacks", "Onion Pakoda, Masala Chai", "Cookies", 280),
        ("Tuesday", "Dinner", "Roti, Rajma Masala, Steamed Basmati Rice, Salad, Kheer", "Sewai Kheer", 710),

        ("Wednesday", "Breakfast", "Aloo Paratha with White Butter, Curd, Pickle, Tea", "Fresh Orange", 520),
        ("Wednesday", "Lunch", "Roti, Kadai Paneer / Chicken Curry (Optional), Rice, Rasam", "Ice Cream", 820),
        ("Wednesday", "Snacks", "Samosa, Tamarind Chutney, Tea", "Roasted Peanuts", 300),
        ("Wednesday", "Dinner", "Veg Biryani / Egg Biryani, Mirchi Ka Salan, Onion Raita", "Rasgulla", 790),

        ("Thursday", "Breakfast", "Poha with Roasted Peanuts, Sev, Lemon, Milk / Tea", "Apple", 390),
        ("Thursday", "Lunch", "Phulka, Methi Malai Matar, Yellow Dal, Ghee Rice, Papad", "Moong Dal Halwa", 730),
        ("Thursday", "Snacks", "Pav Bhaji, Lemon Wedges, Filter Coffee", "Butter Toast", 350),
        ("Thursday", "Dinner", "Roti, Dum Aloo, Steamed Rice, Sambar, Curd", "Banana", 640),

        ("Friday", "Breakfast", "Puri Bhaji, Halwa, Tea / Coffee", "Boiled Egg", 510),
        ("Friday", "Lunch", "Roti, Palak Paneer, Dal Makhani, Jeera Rice, Buttermilk", "Jalebi", 780),
        ("Friday", "Snacks", "Bhel Puri / Sev Puri, Tea", "Marie Gold", 220),
        ("Friday", "Dinner", "South Indian Meals: Rice, Sambar, Poriyal, Rasam, Payasam", "Payasam", 690),

        ("Saturday", "Breakfast", "Uttapam, Sambar, Coriander Chutney, Tea/Coffee", "Papaya Slices", 430),
        ("Saturday", "Lunch", "Roti, Bhindi Masala, Dal Tadka, Lemon Rice, Raita", "Sweet Boondi", 710),
        ("Saturday", "Snacks", "Veg Sandwich, Tomato Ketchup, Tea", "Biscuits", 260),
        ("Saturday", "Dinner", "Special Fried Rice, Veg Manchurian, Spring Rolls, Ice Cream", "Vanilla Ice Cream", 850),

        ("Sunday", "Breakfast", "Chole Bhature, Sweet Lassi, Coffee", "Fresh Fruits", 620),
        ("Sunday", "Lunch", "Special Hyderabadi Dum Biryani (Veg/Chicken), Salan, Raita", "Shahi Tukda", 920),
        ("Sunday", "Snacks", "Dhokla with Green Chilli, Mint Tea", "Khakhra", 240),
        ("Sunday", "Dinner", "Light Dinner: Khichdi, Kadhi, Papad, Achar, Milk with Turmeric", "Sweet Curd", 550)
    ]
    cursor.executemany("""
    INSERT INTO mess_menu (day_of_week, meal_type, items, special_item, calories)
    VALUES (?, ?, ?, ?, ?)
    """, menu_data)

    # Visitors
    visitors_data = [
        (1, "Aarav Sharma", "Ramesh Sharma", "Father", "+91 98111 22231", (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), None, "Semester fee discussion & family visit", "IN_PREMISES"),
        (6, "Ananya Sen", "Pradip Sen", "Father", "+91 98111 22236", (datetime.now() - timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M"), (datetime.now() - timedelta(days=1, hours=1)).strftime("%Y-%m-%d %H:%M"), "Delivered project hardware kit", "CHECKED_OUT")
    ]
    cursor.executemany("""
    INSERT INTO visitors (student_id, student_name, visitor_name, relation, phone, entry_time, exit_time, purpose, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, visitors_data)

    # Notices
    notices_data = [
        ("Hostel Annual Fest 'SANSKRITI 2026' Registrations Open!", "All hostel residents are invited to participate in the upcoming cultural & sports tournament scheduled from Sept 5-8. Cash prizes and trophies up for grabs.", "Event", "NORMAL", "All Students", "Hostel Cultural Committee", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")),
        ("Water Tank Cleaning & Maintenance Notice - Aryabhata Block", "Overhead water supply will be temporarily shut down tomorrow between 10:00 AM to 01:00 PM for deep disinfection and maintenance. Please store sufficient water.", "Maintenance", "HIGH", "Aryabhata Block Residents", "Chief Maintenance Warden", (datetime.now() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")),
        ("Mandatory Night Attendance Curfew Timing Reminder", "Strict 09:30 PM biometric night curfew applies to all blocks. Late entries without warden-approved gate pass will lead to disciplinary remarks and automated SMS to parents.", "Emergency", "URGENT", "All Students", "Chief Proctor & Warden Office", (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M")),
        ("Special Sunday Feast & Feedback Poll", "Vote on the Student Portal for next Sunday's special dessert choice (Shahi Tukda vs Chocolate Brownie with Ice Cream).", "Mess", "NORMAL", "All Students", "Mess Student Representative", (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"))
    ]
    cursor.executemany("""
    INSERT INTO notices (title, content, category, priority, target_audience, posted_by, posted_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, notices_data)

    conn.commit()

# Helper queries
def fetch_all(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def fetch_one(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def execute_query(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id
