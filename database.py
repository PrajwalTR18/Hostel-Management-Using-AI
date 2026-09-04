"""
Database Layer for AI-Based Hostel Management System
Provides SQLite schema setup, comprehensive enterprise seeding, and query helper functions.
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

def init_database(force_reseed=False):
    conn = get_connection()
    cursor = conn.cursor()

    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS hostels")
        cursor.execute("DROP TABLE IF EXISTS rooms")
        cursor.execute("DROP TABLE IF EXISTS students")
        cursor.execute("DROP TABLE IF EXISTS complaints")
        cursor.execute("DROP TABLE IF EXISTS attendance")
        cursor.execute("DROP TABLE IF EXISTS leave_requests")
        cursor.execute("DROP TABLE IF EXISTS fee_records")
        cursor.execute("DROP TABLE IF EXISTS mess_menu")
        cursor.execute("DROP TABLE IF EXISTS visitors")
        cursor.execute("DROP TABLE IF EXISTS notices")
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hostels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL, -- Boys / Girls / Co-ed
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
        dietary_pref TEXT DEFAULT 'Veg', -- 'Veg', 'Non-Veg', 'Eggetarian', 'Jain', 'Vegan'
        fee_status TEXT DEFAULT 'PAID', -- 'PAID', 'PARTIAL', 'PENDING', 'OVERDUE'
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
        marked_by TEXT DEFAULT 'Turnstile Biometric #1',
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

    # Seed if tables are empty or count is small
    cursor.execute("SELECT COUNT(*) FROM students")
    count_stu = cursor.fetchone()[0]
    if count_stu < 20 or force_reseed:
        seed_data(conn)

    conn.close()
    ensure_student_users()


def seed_data(conn):
    cursor = conn.cursor()

    # Clear existing data to ensure pristine seeding
    cursor.execute("DELETE FROM hostels")
    cursor.execute("DELETE FROM rooms")
    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM complaints")
    cursor.execute("DELETE FROM attendance")
    cursor.execute("DELETE FROM leave_requests")
    cursor.execute("DELETE FROM fee_records")
    cursor.execute("DELETE FROM mess_menu")
    cursor.execute("DELETE FROM visitors")
    cursor.execute("DELETE FROM notices")
    cursor.execute("DELETE FROM users")

    # ==============================================================================
    # 1. HOSTELS (6 Diverse Campus Complexes)
    # ==============================================================================
    hostels_data = [
        ("Aryabhata Block (Boys)", "Boys", 240, "North Campus, Engineering Enclave", "Dr. Rajesh Sharma", "+91 98765 43210"),
        ("Gargi Bhavan (Girls)", "Girls", 220, "South Campus, Green Enclave", "Dr. Sunita Verma", "+91 98765 43211"),
        ("CV Raman Hall (Boys PG)", "Boys", 150, "East Campus, Research & Innovation Park", "Prof. Anand Nair", "+91 98765 43212"),
        ("Sarojini Naidu Tower (Girls PG)", "Girls", 160, "West Campus, Scholars Circle", "Dr. Meenakshi Sundaram", "+91 98765 43213"),
        ("Kalam Innovation Block (Boys)", "Boys", 180, "Central Campus, Tech Boulevard", "Dr. Vikram Sethi", "+91 98765 43214"),
        ("Tagore Executive Residence (Co-ed)", "Co-ed", 100, "Main Campus Square, Academic Circle", "Prof. Sharmila Tagore", "+91 98765 43215")
    ]
    cursor.executemany("""
    INSERT INTO hostels (name, type, capacity, address, warden_name, contact) VALUES (?, ?, ?, ?, ?, ?)
    """, hostels_data)

    # ==============================================================================
    # 2. ROOMS (52 Diverse Units across Blocks and Floors 1-5)
    # ==============================================================================
    rooms_data = [
        # Aryabhata Block (Boys) - Block A & B
        ("Aryabhata Block (Boys)", "Block A", 1, "A-101", "Single", 1, 1, "FULL", 8500, "AC, Attached Bath, High-Speed LAN, Ergonomic Desk"),
        ("Aryabhata Block (Boys)", "Block A", 1, "A-102", "Double", 2, 2, "FULL", 6500, "AC, Attached Bath, Balcony, Individual Wardrobes"),
        ("Aryabhata Block (Boys)", "Block A", 1, "A-103", "Double", 2, 2, "FULL", 6500, "Attached Bath, High-Speed WiFi, Bookshelves"),
        ("Aryabhata Block (Boys)", "Block A", 1, "A-104", "Triple", 3, 3, "FULL", 5000, "Attached Bath, Common Balcony, Study Tables"),
        ("Aryabhata Block (Boys)", "Block A", 1, "A-105", "Triple", 3, 2, "PARTIALLY_OCCUPIED", 5000, "Common Bath, Garden View, Balcony"),
        ("Aryabhata Block (Boys)", "Block A", 2, "A-201", "Single", 1, 0, "AVAILABLE", 8500, "AC, Attached Bath, Smart Lock"),
        ("Aryabhata Block (Boys)", "Block A", 2, "A-202", "Double", 2, 2, "FULL", 6500, "AC, Attached Bath, Balcony"),
        ("Aryabhata Block (Boys)", "Block A", 2, "A-203", "Double", 2, 1, "PARTIALLY_OCCUPIED", 6500, "Attached Bath (New LED Lighting)"),
        ("Aryabhata Block (Boys)", "Block A", 2, "A-204", "Triple", 3, 2, "PARTIALLY_OCCUPIED", 5000, "Attached Bath, Study Tables"),
        ("Aryabhata Block (Boys)", "Block A", 3, "A-301", "Single", 1, 1, "FULL", 8500, "AC, Attached Bath, Mini Fridge"),
        ("Aryabhata Block (Boys)", "Block A", 3, "A-302", "Double", 2, 0, "MAINTENANCE", 6500, "Attached Bath (Plumbing Replacement in Progress)"),
        ("Aryabhata Block (Boys)", "Block A", 3, "A-303", "Quad", 4, 3, "PARTIALLY_OCCUPIED", 4200, "Spacious Suite, 2 Attached Baths, Balcony"),

        ("Aryabhata Block (Boys)", "Block B", 1, "B-101", "Double", 2, 2, "FULL", 6200, "Attached Bath, Study Table, WiFi"),
        ("Aryabhata Block (Boys)", "Block B", 1, "B-102", "Triple", 3, 2, "PARTIALLY_OCCUPIED", 4800, "Common Bath, Balcony"),
        ("Aryabhata Block (Boys)", "Block B", 2, "B-201", "Single", 1, 1, "FULL", 8200, "AC, Attached Bath, Corner View"),
        ("Aryabhata Block (Boys)", "Block B", 2, "B-202", "Double", 2, 1, "PARTIALLY_OCCUPIED", 6200, "Attached Bath, LAN Port"),
        ("Aryabhata Block (Boys)", "Block B", 3, "B-301", "Triple", 3, 0, "AVAILABLE", 4800, "Common Bath, Freshly Painted"),

        # Gargi Bhavan (Girls) - Block G1 & G2
        ("Gargi Bhavan (Girls)", "Block G1", 1, "G-101", "Single", 1, 1, "FULL", 8800, "AC, Attached Bath, Garden View, Smart Lock"),
        ("Gargi Bhavan (Girls)", "Block G1", 1, "G-102", "Double", 2, 2, "FULL", 6800, "AC, Attached Bath, Full-Length Mirrors"),
        ("Gargi Bhavan (Girls)", "Block G1", 1, "G-103", "Double", 2, 2, "FULL", 6800, "Attached Bath, High-Speed WiFi"),
        ("Gargi Bhavan (Girls)", "Block G1", 1, "G-104", "Triple", 3, 2, "PARTIALLY_OCCUPIED", 5200, "Attached Bath, Study Lamps"),
        ("Gargi Bhavan (Girls)", "Block G1", 2, "G-201", "Single", 1, 0, "AVAILABLE", 8800, "AC, Attached Bath, Balcony"),
        ("Gargi Bhavan (Girls)", "Block G1", 2, "G-202", "Double", 2, 2, "FULL", 6800, "AC, Attached Bath, Balcony"),
        ("Gargi Bhavan (Girls)", "Block G1", 2, "G-203", "Double", 2, 1, "PARTIALLY_OCCUPIED", 6800, "Attached Bath, Garden View"),
        ("Gargi Bhavan (Girls)", "Block G1", 3, "G-301", "Single", 1, 1, "FULL", 8800, "AC, Attached Bath, Refrigerator"),
        ("Gargi Bhavan (Girls)", "Block G1", 3, "G-302", "Triple", 3, 2, "PARTIALLY_OCCUPIED", 5200, "Common Bath, Sunrise Balcony"),

        ("Gargi Bhavan (Girls)", "Block G2", 1, "G2-101", "Double", 2, 2, "FULL", 6600, "Attached Bath, Study Desks"),
        ("Gargi Bhavan (Girls)", "Block G2", 1, "G2-102", "Triple", 3, 2, "PARTIALLY_OCCUPIED", 5000, "Common Bath, Balcony"),
        ("Gargi Bhavan (Girls)", "Block G2", 2, "G2-201", "Single", 1, 0, "AVAILABLE", 8500, "AC, Attached Bath, Corner View"),
        ("Gargi Bhavan (Girls)", "Block G2", 2, "G2-202", "Quad", 4, 3, "PARTIALLY_OCCUPIED", 4400, "2 Attached Baths, Lounge Area"),

        # CV Raman Hall (Boys PG & Research)
        ("CV Raman Hall (Boys PG)", "Block R", 1, "R-101", "Single", 1, 1, "FULL", 9500, "AC, Attached Bath, Refrigerator, Silent Soundproofing"),
        ("CV Raman Hall (Boys PG)", "Block R", 1, "R-102", "Single", 1, 1, "FULL", 9500, "AC, Attached Bath, High-Speed 1Gbps LAN"),
        ("CV Raman Hall (Boys PG)", "Block R", 2, "R-201", "Single", 1, 0, "AVAILABLE", 9500, "AC, Attached Bath, Lake View Balcony"),
        ("CV Raman Hall (Boys PG)", "Block R", 2, "R-202", "Double", 2, 2, "FULL", 7500, "AC, Attached Bath, Dual Study Desks"),
        ("CV Raman Hall (Boys PG)", "Block R", 3, "R-301", "Single", 1, 1, "FULL", 9500, "AC, Attached Bath, Smart Workstation"),
        ("CV Raman Hall (Boys PG)", "Block R", 3, "R-302", "Double", 2, 2, "FULL", 7500, "AC, Attached Bath, Balcony, Dual Workstations"),

        # Sarojini Naidu Tower (Girls PG)
        ("Sarojini Naidu Tower (Girls PG)", "Block S", 1, "S-101", "Single", 1, 1, "FULL", 9800, "AC, Attached Bath, Refrigerator, Smart Keycard"),
        ("Sarojini Naidu Tower (Girls PG)", "Block S", 1, "S-102", "Double", 2, 2, "FULL", 7800, "AC, Attached Bath, Balcony"),
        ("Sarojini Naidu Tower (Girls PG)", "Block S", 2, "S-201", "Single", 1, 0, "AVAILABLE", 9800, "AC, Attached Bath, Sunset View"),
        ("Sarojini Naidu Tower (Girls PG)", "Block S", 2, "S-202", "Double", 2, 1, "PARTIALLY_OCCUPIED", 7800, "AC, Attached Bath, Study Pods"),
        ("Sarojini Naidu Tower (Girls PG)", "Block S", 3, "S-301", "Single", 1, 1, "FULL", 9800, "AC, Attached Bath, Panoramic Campus View"),

        # Kalam Innovation Block (Boys Tech Hub)
        ("Kalam Innovation Block (Boys)", "Block K", 1, "K-101", "Single", 1, 1, "FULL", 9200, "AC, Dual Monitor Study Desk, Gigabit Ethernet"),
        ("Kalam Innovation Block (Boys)", "Block K", 1, "K-102", "Double", 2, 2, "FULL", 7200, "AC, Attached Bath, Whiteboard Wall"),
        ("Kalam Innovation Block (Boys)", "Block K", 2, "K-201", "Single", 1, 0, "AVAILABLE", 9200, "AC, Attached Bath, Smart Automation"),
        ("Kalam Innovation Block (Boys)", "Block K", 2, "K-202", "Triple", 3, 2, "PARTIALLY_OCCUPIED", 5500, "Attached Bath, High-Speed WiFi"),
        ("Kalam Innovation Block (Boys)", "Block K", 3, "K-301", "Single", 1, 1, "FULL", 9200, "AC, Soundproof Pod, Ergonomic Setup"),
        ("Kalam Innovation Block (Boys)", "Block K", 3, "K-302", "Double", 2, 1, "PARTIALLY_OCCUPIED", 7200, "AC, Attached Bath, High-Speed WiFi"),

        # Tagore Executive Residence (Co-ed)
        ("Tagore Executive Residence (Co-ed)", "Block T", 1, "T-101", "Single", 1, 1, "FULL", 11500, "Luxury AC Studio, Kitchenette, Attached Bath"),
        ("Tagore Executive Residence (Co-ed)", "Block T", 1, "T-102", "Single", 1, 0, "AVAILABLE", 11500, "Luxury AC Studio, Kitchenette, Attached Bath"),
        ("Tagore Executive Residence (Co-ed)", "Block T", 2, "T-201", "Double", 2, 1, "PARTIALLY_OCCUPIED", 8500, "AC Studio Suite, Attached Bath, Balcony"),
        ("Tagore Executive Residence (Co-ed)", "Block T", 2, "T-202", "Double", 2, 1, "PARTIALLY_OCCUPIED", 8500, "AC Studio Suite, Kitchenette, Garden View"),
        ("Tagore Executive Residence (Co-ed)", "Block T", 3, "T-301", "Single", 1, 1, "FULL", 11500, "Penthouse AC Studio, Balcony, Dedicated Kitchenette")
    ]
    cursor.executemany("""
    INSERT INTO rooms (hostel_name, block_name, floor_number, room_number, room_type, capacity, occupied_beds, status, rent_per_month, amenities)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rooms_data)

    # ==============================================================================
    # 3. STUDENTS (50 Diverse Resident Profiles across 12 Departments)
    # ==============================================================================
    students_data = [
        # (student_id_code, name, email, phone, gender, department, year, room_id, sleep_habit, study_habit, cleanliness, dietary_pref, fee_status, parent_name, parent_phone)
        ("STU-1001", "Aarav Sharma", "aarav.sharma@campus.edu", "+91 91234 56781", "Male", "Computer Science", 3, 1, "Night Owl", "Silent / Intensive", "Very High", "Veg", "PAID", "Ramesh Sharma", "+91 98111 22231"),
        ("STU-1002", "Vikramaditya Roy", "vikram.roy@campus.edu", "+91 91234 56782", "Male", "Information Science", 3, 2, "Early Bird", "Moderate", "High", "Non-Veg", "PAID", "Debashis Roy", "+91 98111 22232"),
        ("STU-1003", "Rohan Kulkarni", "rohan.k@campus.edu", "+91 91234 56783", "Male", "Electronics & Comm", 2, 2, "Early Bird", "Moderate", "High", "Veg", "PAID", "Suresh Kulkarni", "+91 98111 22233"),
        ("STU-1004", "Kabir Mehta", "kabir.m@campus.edu", "+91 91234 56784", "Male", "Mechanical Eng", 1, 3, "Night Owl", "Group / Music", "Moderate", "Non-Veg", "OVERDUE", "Alok Mehta", "+91 98111 22234"),
        ("STU-1005", "Tanmay Deshmukh", "tanmay.d@campus.edu", "+91 91234 56785", "Male", "Computer Science", 2, 3, "Flexible", "Silent / Intensive", "High", "Veg", "PAID", "Nitin Deshmukh", "+91 98111 22235"),
        ("STU-1006", "Ananya Sen", "ananya.sen@campus.edu", "+91 91234 56786", "Female", "Computer Science", 4, 18, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PAID", "Pradip Sen", "+91 98111 22236"),
        ("STU-1007", "Pooja Hegde", "pooja.h@campus.edu", "+91 91234 56787", "Female", "Biotechnology", 2, 19, "Night Owl", "Moderate", "High", "Non-Veg", "PAID", "Venkatesh Hegde", "+91 98111 22237"),
        ("STU-1008", "Sneha Iyer", "sneha.iyer@campus.edu", "+91 91234 56788", "Female", "Information Science", 2, 19, "Night Owl", "Moderate", "High", "Veg", "PAID", "Subramanian Iyer", "+91 98111 22238"),
        ("STU-1009", "Meera Nair", "meera.nair@campus.edu", "+91 91234 56789", "Female", "Electrical Eng", 1, 20, "Early Bird", "Silent / Intensive", "Very High", "Veg", "OVERDUE", "Gopal Nair", "+91 98111 22239"),
        ("STU-1010", "Devansh Pandey", "devansh.p@campus.edu", "+91 91234 56790", "Male", "Civil Engineering", 3, 13, "Flexible", "Group / Music", "Moderate", "Non-Veg", "PAID", "Harish Pandey", "+91 98111 22240"),
        ("STU-1011", "Kavya Murthy", "kavya.m@campus.edu", "+91 91234 56791", "Female", "Computer Science", 1, None, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PAID", "Narayana Murthy", "+91 98111 22241"),
        ("STU-1012", "Aryan Gupta", "aryan.gupta@campus.edu", "+91 91234 56792", "Male", "Artificial Intelligence", 1, None, "Night Owl", "Silent / Intensive", "High", "Non-Veg", "PAID", "Rajiv Gupta", "+91 98111 22242"),
        
        # Additional Residents
        ("STU-1013", "Siddharth Verma", "siddharth.v@campus.edu", "+91 91234 56793", "Male", "Data Science", 2, 4, "Night Owl", "Silent / Intensive", "High", "Non-Veg", "PAID", "Mahesh Verma", "+91 98111 22243"),
        ("STU-1014", "Aditya Joshi", "aditya.j@campus.edu", "+91 91234 56794", "Male", "Mechanical Eng", 2, 4, "Night Owl", "Group / Music", "Moderate", "Veg", "PAID", "Prakash Joshi", "+91 98111 22244"),
        ("STU-1015", "Ishaan Malhotra", "ishaan.m@campus.edu", "+91 91234 56795", "Male", "Aerospace Eng", 3, 4, "Flexible", "Moderate", "High", "Non-Veg", "PAID", "Sunil Malhotra", "+91 98111 22245"),
        ("STU-1016", "Rhea Singhania", "rhea.s@campus.edu", "+91 91234 56796", "Female", "Cyber Security", 3, 20, "Night Owl", "Silent / Intensive", "Very High", "Veg", "PAID", "Vijay Singhania", "+91 98111 22246"),
        ("STU-1017", "Divya Menon", "divya.m@campus.edu", "+91 91234 56797", "Female", "Electronics & Comm", 2, 21, "Early Bird", "Moderate", "High", "Veg", "PAID", "Kishore Menon", "+91 98111 22247"),
        ("STU-1018", "Nikhil Chawla", "nikhil.c@campus.edu", "+91 91234 56798", "Male", "Robotics & Automation", 4, 7, "Night Owl", "Silent / Intensive", "High", "Non-Veg", "PAID", "Anil Chawla", "+91 98111 22248"),
        ("STU-1019", "Varun Teja", "varun.t@campus.edu", "+91 91234 56799", "Male", "Artificial Intelligence", 3, 7, "Night Owl", "Silent / Intensive", "Very High", "Non-Veg", "PAID", "Raghavendra Teja", "+91 98111 22249"),
        ("STU-1020", "Priyanka Reddy", "priyanka.r@campus.edu", "+91 91234 56800", "Female", "Biotechnology", 3, 23, "Early Bird", "Silent / Intensive", "High", "Veg", "PAID", "Mallikarjun Reddy", "+91 98111 22250"),
        ("STU-1021", "Shruti Bhattacharya", "shruti.b@campus.edu", "+91 91234 56801", "Female", "Data Science", 2, 23, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PAID", "Somnath Bhattacharya", "+91 98111 22251"),
        ("STU-1022", "Karan Singhal", "karan.s@campus.edu", "+91 91234 56802", "Male", "Computer Science", 1, 5, "Flexible", "Moderate", "High", "Veg", "PAID", "Deepak Singhal", "+91 98111 22252"),
        ("STU-1023", "Abhinav Saxena", "abhinav.s@campus.edu", "+91 91234 56803", "Male", "Information Science", 1, 5, "Flexible", "Moderate", "High", "Non-Veg", "PARTIAL", "Sanjay Saxena", "+91 98111 22253"),
        ("STU-1024", "Tanya Kapoor", "tanya.k@campus.edu", "+91 91234 56804", "Female", "Artificial Intelligence", 1, 21, "Night Owl", "Group / Music", "Moderate", "Non-Veg", "PAID", "Rajesh Kapoor", "+91 98111 22254"),
        ("STU-1025", "Manish Tiwari", "manish.t@campus.edu", "+91 91234 56805", "Male", "Civil Engineering", 2, 8, "Early Bird", "Moderate", "High", "Veg", "PAID", "Brijesh Tiwari", "+91 98111 22255"),
        ("STU-1026", "Gaurav Nambiar", "gaurav.n@campus.edu", "+91 91234 56806", "Male", "Electrical Eng", 4, 10, "Night Owl", "Silent / Intensive", "Very High", "Non-Veg", "PAID", "Madhavan Nambiar", "+91 98111 22256"),
        ("STU-1027", "Sanjana Rao", "sanjana.r@campus.edu", "+91 91234 56807", "Female", "Electronics & Comm", 4, 25, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PAID", "Bhaskar Rao", "+91 98111 22257"),
        ("STU-1028", "Pranav Hegde", "pranav.h@campus.edu", "+91 91234 56808", "Male", "Computer Science", 2, 13, "Night Owl", "Silent / Intensive", "High", "Veg", "PAID", "Sanjay Hegde", "+91 98111 22258"),
        ("STU-1029", "Harshavardhan R", "harsha.r@campus.edu", "+91 91234 56809", "Male", "Aerospace Eng", 3, 15, "Early Bird", "Moderate", "High", "Non-Veg", "PAID", "Ranganath R", "+91 98111 22259"),
        ("STU-1030", "Deepika Pillai", "deepika.p@campus.edu", "+91 91234 56810", "Female", "Computer Science", 3, 27, "Night Owl", "Silent / Intensive", "Very High", "Veg", "PAID", "Muraleedharan Pillai", "+91 98111 22260"),
        ("STU-1031", "Akash Deep", "akash.d@campus.edu", "+91 91234 56811", "Male", "Cyber Security", 2, 16, "Flexible", "Group / Music", "Moderate", "Non-Veg", "OVERDUE", "Kuldeep Singh", "+91 98111 22261"),
        ("STU-1032", "Swati Agarwal", "swati.a@campus.edu", "+91 91234 56812", "Female", "Data Science", 1, 28, "Early Bird", "Silent / Intensive", "High", "Veg", "PAID", "Mukesh Agarwal", "+91 98111 22262"),
        ("STU-1033", "Naveen Jindal", "naveen.j@campus.edu", "+91 91234 56813", "Male", "Mechanical Eng", 3, 12, "Night Owl", "Moderate", "High", "Veg", "PAID", "Omprakash Jindal", "+91 98111 22263"),
        ("STU-1034", "Bhavya Sri", "bhavya.s@campus.edu", "+91 91234 56814", "Female", "Information Science", 2, 28, "Flexible", "Moderate", "High", "Veg", "PAID", "Chandrasekhar Sri", "+91 98111 22264"),
        ("STU-1035", "Suraj Bhanushali", "suraj.b@campus.edu", "+91 91234 56815", "Male", "Robotics & Automation", 1, 12, "Night Owl", "Silent / Intensive", "High", "Veg", "PAID", "Kantilal Bhanushali", "+91 98111 22265"),
        ("STU-1036", "Lavanya Krishnan", "lavanya.k@campus.edu", "+91 91234 56816", "Female", "Biotechnology", 4, 31, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PAID", "Krishnan S", "+91 98111 22266"),
        ("STU-1037", "Mohammed Zaid", "zaid.m@campus.edu", "+91 91234 56817", "Male", "Computer Science", 2, 12, "Night Owl", "Silent / Intensive", "High", "Non-Veg", "PAID", "Tariq Zaid", "+91 98111 22267"),
        ("STU-1038", "Ayesha Khan", "ayesha.k@campus.edu", "+91 91234 56818", "Female", "Electronics & Comm", 3, 32, "Flexible", "Silent / Intensive", "High", "Non-Veg", "PAID", "Nadeem Khan", "+91 98111 22268"),
        ("STU-1039", "Vikas Gowda", "vikas.g@campus.edu", "+91 91234 56819", "Male", "Civil Engineering", 1, 8, "Early Bird", "Moderate", "Moderate", "Veg", "PAID", "Manjunath Gowda", "+91 98111 22269"),
        ("STU-1040", "Neha Deshpande", "neha.d@campus.edu", "+91 91234 56820", "Female", "Artificial Intelligence", 3, 32, "Night Owl", "Silent / Intensive", "Very High", "Veg", "PAID", "Anand Deshpande", "+91 98111 22270"),
        
        # PG Scholars & Tech Seniors
        ("STU-1041", "Dr. Subhash Bose (PhD)", "subhash.b@campus.edu", "+91 91234 56821", "Male", "Computer Science", 4, 33, "Night Owl", "Silent / Intensive", "Very High", "Non-Veg", "PAID", "Amartya Bose", "+91 98111 22271"),
        ("STU-1042", "Rahul Dravid K (MTech)", "rahul.dk@campus.edu", "+91 91234 56822", "Male", "Artificial Intelligence", 4, 34, "Early Bird", "Silent / Intensive", "High", "Veg", "PAID", "Sharad Dravid", "+91 98111 22272"),
        ("STU-1043", "Dr. Aruna Asaf (PhD)", "aruna.a@campus.edu", "+91 91234 56823", "Female", "Biotechnology", 4, 38, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PAID", "Ali Asaf", "+91 98111 22273"),
        ("STU-1044", "Farhan Akhtar (MTech)", "farhan.a@campus.edu", "+91 91234 56824", "Male", "Data Science", 4, 36, "Flexible", "Moderate", "High", "Non-Veg", "PAID", "Javed Akhtar", "+91 98111 22274"),
        ("STU-1045", "Sohail Tanvir (MTech)", "sohail.t@campus.edu", "+91 91234 56825", "Male", "Cyber Security", 4, 36, "Night Owl", "Silent / Intensive", "High", "Non-Veg", "PAID", "Rashid Tanvir", "+91 98111 22275"),
        ("STU-1046", "Ritu Karidhal (PhD)", "ritu.k@campus.edu", "+91 91234 56826", "Female", "Aerospace Eng", 4, 39, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PAID", "Sanjay Karidhal", "+91 98111 22276"),
        ("STU-1047", "Kiran Mazumdar (MS)", "kiran.m@campus.edu", "+91 91234 56827", "Female", "Biotechnology", 4, 39, "Night Owl", "Silent / Intensive", "Very High", "Veg", "PAID", "Rasendra Mazumdar", "+91 98111 22277"),
        ("STU-1048", "Chetan Bhagat (MBA)", "chetan.b@campus.edu", "+91 91234 56828", "Male", "Information Science", 4, 42, "Flexible", "Group / Music", "Moderate", "Veg", "PAID", "Yadvinder Bhagat", "+91 98111 22278"),
        ("STU-1049", "Raghuram Rajan (PhD)", "raghuram.r@campus.edu", "+91 91234 56829", "Male", "Computer Science", 4, 46, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PAID", "Govindarajan R", "+91 98111 22279"),
        ("STU-1050", "Soumya Swaminathan", "soumya.s@campus.edu", "+91 91234 56830", "Female", "Biotechnology", 4, 48, "Early Bird", "Silent / Intensive", "Very High", "Veg", "PAID", "M. S. Swaminathan", "+91 98111 22280")
    ]
    cursor.executemany("""
    INSERT INTO students (student_id_code, name, email, phone, gender, department, year, room_id, sleep_habit, study_habit, cleanliness, dietary_pref, fee_status, parent_name, parent_phone)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, students_data)

    # ==============================================================================
    # 4. USERS (Admin, Wardens, Security, and all 50 Students)
    # ==============================================================================
    users_data = [
        ("admin", "admin123", "ADMIN", "Chief Hostel Administrator", "admin@hostel.edu", None),
        ("warden_rajesh", "warden123", "WARDEN", "Dr. Rajesh Sharma (Boys Warden)", "warden.boys@hostel.edu", None),
        ("warden_sunita", "warden123", "WARDEN", "Dr. Sunita Verma (Girls Warden)", "warden.girls@hostel.edu", None),
        ("warden_anand", "warden123", "WARDEN", "Prof. Anand Nair (PG Warden)", "warden.pg@hostel.edu", None),
        ("warden_meenakshi", "warden123", "WARDEN", "Dr. Meenakshi Sundaram (West Warden)", "warden.west@hostel.edu", None),
        ("security_gate", "security123", "SECURITY", "Head Security Officer (North Gate)", "security.north@hostel.edu", None),
        ("security_turnstile", "security123", "SECURITY", "Turnstile Security Post (South Gate)", "security.south@hostel.edu", None),
        
        # Primary Demo Student Aliases
        ("aarav", "student123", "STUDENT", "Aarav Sharma", "aarav.sharma@campus.edu", 1),
        ("vikram", "student123", "STUDENT", "Vikramaditya Roy", "vikram.roy@campus.edu", 2),
        ("rohan", "student123", "STUDENT", "Rohan Kulkarni", "rohan.k@campus.edu", 3),
        ("kabir", "student123", "STUDENT", "Kabir Mehta", "kabir.m@campus.edu", 4),
        ("tanmay", "student123", "STUDENT", "Tanmay Deshmukh", "tanmay.d@campus.edu", 5),
        ("ananya", "student123", "STUDENT", "Ananya Sen", "ananya.sen@campus.edu", 6),
        ("pooja", "student123", "STUDENT", "Pooja Hegde", "pooja.h@campus.edu", 7),
        ("sneha", "student123", "STUDENT", "Sneha Iyer", "sneha.iyer@campus.edu", 8),
        ("meera", "student123", "STUDENT", "Meera Nair", "meera.nair@campus.edu", 9),
        ("devansh", "student123", "STUDENT", "Devansh Pandey", "devansh.p@campus.edu", 10),
        ("kavya", "student123", "STUDENT", "Kavya Murthy", "kavya.m@campus.edu", 11),
        ("aryan", "student123", "STUDENT", "Aryan Gupta", "aryan.gupta@campus.edu", 12)
    ]
    cursor.executemany("""
    INSERT INTO users (username, password, role, full_name, email, student_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """, users_data)

    # ==============================================================================
    # 5. COMPLAINTS (32 Real-World Maintenance Tickets with AI NLP Triage)
    # ==============================================================================
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M")
    
    complaints_data = [
        # Plumbing
        (1, "Aarav Sharma", "A-101", "Plumbing", "Severe bathroom pipe leakage", "The main washbasin pipe is continuously leaking water creating a slippery floor pool.", "HIGH", "NEGATIVE", "IN_PROGRESS", "Maintenance", "Inspect and replace seal ring on basin connection", (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), None, "Ramu (Plumber)"),
        (4, "Kabir Mehta", "A-103", "Plumbing", "Flush tank valve stuck continuously running water", "Water is non-stop filling in flush tank and overflowing on floor.", "MEDIUM", "NEGATIVE", "OPEN", "Maintenance", "Replace inlet diaphragm assembly", (now - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"), None, "Ramu (Plumber)"),
        (13, "Siddharth Verma", "A-104", "Plumbing", "Hot water geyser not heating in morning", "Geyser switch is on but pilot light is off and water remains ice cold.", "HIGH", "NEGATIVE", "IN_PROGRESS", "Maintenance", "Check heating coil and thermostat element", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), None, "Govind (Electrician)"),
        (17, "Divya Menon", "G-104", "Plumbing", "Shower head calcified with low water pressure", "Hard water scaling has blocked half the shower jet nozzles.", "LOW", "NEUTRAL", "RESOLVED", "Maintenance", "Descaled shower head with citric acid flush", (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), "Ramu (Plumber)"),
        (20, "Priyanka Reddy", "G-201", "Plumbing", "Washbasin drain clogged with hair and stagnant water", "Water takes over 20 minutes to drain out of the sink.", "LOW", "NEUTRAL", "RESOLVED", "Maintenance", "Clean P-trap and apply organic declogger", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "Sunil (Housekeeping)"),
        (43, "Dr. Aruna Asaf", "S-101", "Plumbing", "Balcony drain backing up during rain", "Rainwater pooling on balcony due to external drain leaf debris.", "MEDIUM", "NEGATIVE", "RESOLVED", "Maintenance", "Cleared terrace downspout and fitted leaf filter mesh", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "Ramu (Plumber)"),

        # Electrical
        (6, "Ananya Sen", "G-101", "Electrical", "Tube light flickering and spark near switchboard", "The main room tube light is flickering heavily and buzzing with small sparks.", "URGENT", "NEGATIVE", "OPEN", "Maintenance", "Isolate circuit breaker and replace socket assembly immediately", (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"), None, "Govind (Electrician)"),
        (18, "Nikhil Chawla", "A-202", "Electrical", "AC remote sensor not responding and displaying E4 error", "Split AC turns on for 2 mins then shuts down with error code E4.", "MEDIUM", "NEGATIVE", "IN_PROGRESS", "Maintenance", "Inspect refrigerant gas pressure and clean filter mesh", (now - timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M"), None, "CoolTech AC Vendor"),
        (23, "Abhinav Saxena", "A-105", "Electrical", "Ceiling fan regulator knob broken and spinning freely", "Fan is stuck on max speed 5 cannot be controlled.", "LOW", "NEUTRAL", "IN_PROGRESS", "Maintenance", "Replace 5-step electronic step regulator", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), None, "Govind (Electrician)"),
        (25, "Manish Tiwari", "A-203", "Electrical", "Study table power socket loose and sparking on laptop charger", "Plugging in the charger makes crackling sounds.", "HIGH", "NEGATIVE", "OPEN", "Maintenance", "Replace 16A modular socket and tighten terminal screws", (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"), None, "Govind (Electrician)"),
        (36, "Lavanya Krishnan", "G-301", "Electrical", "Geyser power indicator lamp burnt out", "Geyser is working but the red pilot light indicator is defective.", "LOW", "NEUTRAL", "RESOLVED", "Maintenance", "Replaced neon pilot indicator lamp", (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M"), "Govind (Electrician)"),
        (41, "Dr. Subhash Bose", "R-101", "Electrical", "Exhaust fan in attached bathroom humming loudly without rotation", "Motor seems jammed and smelling warm.", "MEDIUM", "NEGATIVE", "RESOLVED", "Maintenance", "Lubricate fan bearings and replace capacitor", (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), "Govind (Electrician)"),
        (49, "Raghuram Rajan", "T-101", "Electrical", "Smart thermostat temperature sensor miscalibrated", "AC room temperature reading shows 18C when actual room is 26C.", "LOW", "NEUTRAL", "OPEN", "Maintenance", "Recalibrate IoT thermostat sensor and update firmware", (now - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M"), None, "Smart Home Vendor"),

        # Internet & Wi-Fi
        (2, "Vikramaditya Roy", "A-102", "Internet & Wi-Fi", "Wi-Fi disconnecting repeatedly during online exams", "The 5GHz access point in floor 1 hallway is restarting every 15 minutes.", "HIGH", "NEGATIVE", "OPEN", "IT Department", "Check AP firmware PoE power budget and reboot controller", (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"), None, "Suresh (IT Admin)"),
        (16, "Rhea Singhania", "G-103", "Internet & Wi-Fi", "LAN port in wall plate dead no link LED", "Connected CAT6 cable but Ethernet adapter shows cable unplugged.", "MEDIUM", "NEGATIVE", "IN_PROGRESS", "IT Department", "Punch down keystone jack and test continuity on patch panel", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), None, "Suresh (IT Admin)"),
        (19, "Varun Teja", "A-202", "Internet & Wi-Fi", "High packet loss and jitter during remote lab sessions", "Latency spikes up to 450ms when accessing AWS cloud servers.", "HIGH", "NEGATIVE", "OPEN", "IT Department", "Optimize QoS traffic prioritization on hostel VLAN", (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"), None, "Suresh (IT Admin)"),
        (30, "Deepika Pillai", "G-203", "Internet & Wi-Fi", "Wi-Fi signal weak in room corner desk", "RSSI shows -82 dBm near the window desk causing disconnections.", "MEDIUM", "NEUTRAL", "IN_PROGRESS", "IT Department", "Install supplementary Wi-Fi 6 range extender in wing corridor", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), None, "Suresh (IT Admin)"),
        (48, "Chetan Bhagat", "K-102", "Internet & Wi-Fi", "Captive portal redirect loop on Mac and Android", "Page keeps refreshing without granting IP lease.", "MEDIUM", "NEGATIVE", "RESOLVED", "IT Department", "Flush MAC session table on radius auth server", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "Suresh (IT Admin)"),

        # Food & Mess
        (7, "Pooja Hegde", "G-102", "Food & Mess", "Dinner dal was cold and stale smell noticed", "Dinner served yesterday had cold food and rotis were undercooked.", "MEDIUM", "NEGATIVE", "RESOLVED", "Mess Management", "Audit mess supervisor preparation schedule & steam table temp", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "Mess In-charge Chef"),
        (33, "Naveen Jindal", "B-101", "Food & Mess", "Breakfast milk was diluted and water separated", "Milk served during morning breakfast lacked standard consistency.", "LOW", "NEGATIVE", "CLOSED", "Mess Management", "Issue memo to dairy supplier for fat % audit", (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M"), "Chief Food Inspector"),
        (37, "Mohammed Zaid", "B-201", "Food & Mess", "Request for Jain/Pure Veg breakfast counter separation", "Cross-contamination concern during breakfast buffet rush.", "MEDIUM", "NEUTRAL", "OPEN", "Mess Management", "Demarcate separate serving tongs and dedicated pure-veg buffet counter", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), None, "Mess In-charge Chef"),

        # Housekeeping & Cleanliness
        (10, "Devansh Pandey", "B-101", "Housekeeping & Cleanliness", "Corridor dustbin not emptied for 2 days", "Common floor wastebin overflowing near room B-101.", "LOW", "NEUTRAL", "RESOLVED", "Administration", "Dispatch floor housekeeping staff for daily rotation", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "Cleaning Supervisor"),
        (22, "Karan Singhal", "A-105", "Housekeeping & Cleanliness", "Window pigeon net torn allowing birds to nest on balcony", "Pigeon droppings accumulating on AC outdoor unit.", "MEDIUM", "NEGATIVE", "OPEN", "Housekeeping", "Install heavy-duty nylon mesh with anchors", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), None, "Pest Control Team"),
        (27, "Sanjana Rao", "G-202", "Housekeeping & Cleanliness", "Floor mop cleaning missed for two consecutive days", "Housekeeping staff did not attend room G-202 on Wednesday and Thursday.", "MEDIUM", "NEGATIVE", "RESOLVED", "Housekeeping", "Reassigned floor duty roster and signed verification sheet", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "Cleaning Supervisor"),
        
        # Carpentry & Furniture
        (3, "Rohan Kulkarni", "A-102", "Carpentry & Furniture", "Almirah key lock cylinder jammed", "Cannot open wardrobe to access books and clothes.", "HIGH", "NEGATIVE", "RESOLVED", "Carpentry", "Replace brass lock cylinder and provide dual key set", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "Jaggu (Carpenter)"),
        (15, "Ishaan Malhotra", "A-104", "Carpentry & Furniture", "Study chair hydraulic cylinder dropping automatically", "Chair drops to lowest position when seated.", "LOW", "NEUTRAL", "IN_PROGRESS", "Carpentry", "Replace class-4 gas lift cylinder", (now - timedelta(hours=18)).strftime("%Y-%m-%d %H:%M"), None, "Jaggu (Carpenter)"),
        (28, "Pranav Hegde", "B-101", "Carpentry & Furniture", "Bed frame wooden slat cracked", "One mattress support slat cracked when sitting down.", "HIGH", "NEGATIVE", "OPEN", "Carpentry", "Replace reinforced teakwood support plank", (now - timedelta(hours=14)).strftime("%Y-%m-%d %H:%M"), None, "Jaggu (Carpenter)"),

        # Security & Safety
        (9, "Meera Nair", "G-103", "Security & Safety", "Balcony sliding door latch lock broken", "The sliding glass door latch does not lock firmly from inside.", "HIGH", "NEGATIVE", "IN_PROGRESS", "Security & Maintenance", "Install auxiliary deadbolt on aluminum frame", (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M"), None, "Jaggu (Carpenter)"),
        (14, "Aditya Joshi", "A-104", "Noise & Discipline", "Loud music playing in adjacent room past midnight", "Frequent loud speakers and disturbances after 12 AM curfew.", "HIGH", "NEGATIVE", "RESOLVED", "Discipline Committee", "Issued warning memo to room residents regarding quiet hours", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "Dr. Rajesh Sharma"),
        (26, "Gaurav Nambiar", "A-301", "Security & Safety", "Emergency staircase exit light bulb fused", "Stairwell is completely dark during late evening.", "URGENT", "NEGATIVE", "OPEN", "Safety & Electrical", "Fit 18W emergency LED fitting with battery backup", (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"), None, "Govind (Electrician)"),

        # Administration & Smartcard
        (11, "Kavya Murthy", "Unallocated", "Administration", "Room allocation confirmation pending", "Applied for single room in Gargi Bhavan 2 weeks ago, still awaiting room key.", "MEDIUM", "NEUTRAL", "OPEN", "Administration", "Process room allocation workflow in ERP", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), None, "Chief Warden Office"),
        (12, "Aryan Gupta", "Unallocated", "Administration", "Hostel ID Smartcard issuance delayed", "Biometric enrollment completed but physical RFID smartcard not issued.", "LOW", "NEUTRAL", "IN_PROGRESS", "IT Services", "Print RFID card and encode turnstile permissions", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), None, "Suresh (IT Admin)")
    ]
    cursor.executemany("""
    INSERT INTO complaints (student_id, student_name, room_number, category, title, description, priority, sentiment, status, department, suggested_action, created_at, resolved_at, assigned_to)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, complaints_data)

    # ==============================================================================
    # 6. ATTENDANCE (7 Days History x 50 Students = 350 Detailed Biometric Records)
    # ==============================================================================
    today = date.today()
    att_data = []
    
    # Query all students inserted
    cursor.execute("SELECT id, name, room_id FROM students")
    all_inserted_stus = [dict(r) for r in cursor.fetchall()]

    for d_offset in range(6, -1, -1):
        cur_d = (today - timedelta(days=d_offset)).strftime("%Y-%m-%d")
        for s in all_inserted_stus:
            s_id = s["id"]
            s_name = s["name"]
            r_str = f"Room {s['room_id']}" if s["room_id"] else "Pending"

            # Deterministic pseudo randomness for consistent test state
            seed_val = (s_id * 37 + d_offset * 19) % 100
            if seed_val < 78:
                st_code = "PRESENT"
                cin = "20:42" if seed_val % 2 == 0 else "21:10"
                cout = "07:45"
            elif seed_val < 88:
                st_code = "LATE"
                cin = "22:20"
                cout = "07:30"
            elif seed_val < 94:
                st_code = "ON_LEAVE"
                cin = None
                cout = None
            else:
                st_code = "ABSENT"
                cin = None
                cout = None

            turnstile_name = "Turnstile #1 North Gate" if s_id % 2 == 0 else "Turnstile #2 South Turnstile"
            att_data.append((s_id, s_name, r_str, cur_d, st_code, cin, cout, turnstile_name))

    cursor.executemany("""
    INSERT INTO attendance (student_id, student_name, room_number, date, status, check_in_time, check_out_time, marked_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, att_data)

    # ==============================================================================
    # 7. LEAVE REQUESTS & DIGITAL GATE PASSES (22 Comprehensive Records)
    # ==============================================================================
    leaves_data = [
        (1, "Aarav Sharma", "Room 1", "Attending cousin wedding in Mumbai", (today + timedelta(days=1)).strftime("%Y-%m-%d"), (today + timedelta(days=3)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Rajesh Sharma", "GP-2026-9812", now_str),
        (2, "Vikramaditya Roy", "Room 2", "Inter-college basketball championship in Pune", (today - timedelta(days=2)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), "APPROVED", "Dr. Rajesh Sharma", "GP-2026-1194", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M")),
        (3, "Rohan Kulkarni", "Room 2", "Attending elder brother convocation in Bangalore", (today + timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=4)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Rajesh Sharma", "GP-2026-3392", now_str),
        (4, "Kabir Mehta", "Room 3", "Family emergency visit to hometown Nagpur", today.strftime("%Y-%m-%d"), (today + timedelta(days=2)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Rajesh Sharma", "GP-2026-4419", now_str),
        (5, "Tanmay Deshmukh", "Room 3", "Weekend hometown visit to Pune", (today + timedelta(days=1)).strftime("%Y-%m-%d"), (today + timedelta(days=3)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Rajesh Sharma", "GP-2026-5501", now_str),
        (6, "Ananya Sen", "Room 18", "Inter-college AI Hackathon at IISc Bangalore", (today + timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=5)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Sunita Verma", "GP-2026-7731", now_str),
        (7, "Pooja Hegde", "Room 19", "Attending sister engagement in Mangalore", (today + timedelta(days=3)).strftime("%Y-%m-%d"), (today + timedelta(days=6)).strftime("%Y-%m-%d"), "PENDING", None, None, now_str),
        (8, "Sneha Iyer", "Room 19", "Medical dental checkup in home clinic Chennai", (today + timedelta(days=1)).strftime("%Y-%m-%d"), (today + timedelta(days=2)).strftime("%Y-%m-%d"), "PENDING", None, None, now_str),
        (9, "Meera Nair", "Room 20", "Urgent medical appointment at Apollo Hospital", today.strftime("%Y-%m-%d"), (today + timedelta(days=1)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Sunita Verma", "GP-2026-9914", now_str),
        (13, "Siddharth Verma", "Room 4", "IEEE International Conference in Hyderabad", (today + timedelta(days=4)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Rajesh Sharma", "GP-2026-8839", now_str),
        (14, "Aditya Joshi", "Room 4", "Participating in zonal chess tournament in Mumbai", (today + timedelta(days=4)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"), "PENDING", None, None, now_str),
        (15, "Ishaan Malhotra", "Room 4", "Family function in Delhi", (today + timedelta(days=3)).strftime("%Y-%m-%d"), (today + timedelta(days=6)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Rajesh Sharma", "GP-2026-4482", now_str),
        (16, "Rhea Singhania", "Room 20", "Visiting parents in Jaipur for festival", (today + timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=6)).strftime("%Y-%m-%d"), "PENDING", None, None, now_str),
        (18, "Nikhil Chawla", "Room 7", "Robotics workshop at IIT Madras", (today + timedelta(days=1)).strftime("%Y-%m-%d"), (today + timedelta(days=4)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Rajesh Sharma", "GP-2026-2248", now_str),
        (20, "Priyanka Reddy", "Room 23", "Attending national biotechnology seminar", (today + timedelta(days=5)).strftime("%Y-%m-%d"), (today + timedelta(days=8)).strftime("%Y-%m-%d"), "PENDING", None, None, now_str),
        (22, "Karan Singhal", "Room 5", "Attending Google Developer Student Club Summit", (today + timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=5)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Rajesh Sharma", "GP-2026-2219", now_str),
        (25, "Manish Tiwari", "Room 8", "Visiting hometown for festival celebrations", (today + timedelta(days=3)).strftime("%Y-%m-%d"), (today + timedelta(days=8)).strftime("%Y-%m-%d"), "PENDING", None, None, now_str),
        (27, "Sanjana Rao", "Room 25", "Campus placement drive in Electronic City Bangalore", (today + timedelta(days=1)).strftime("%Y-%m-%d"), (today + timedelta(days=2)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Sunita Verma", "GP-2026-7788", now_str),
        (30, "Deepika Pillai", "Room 27", "TCS National CodeVita Grand Finale in Delhi", (today + timedelta(days=3)).strftime("%Y-%m-%d"), (today + timedelta(days=6)).strftime("%Y-%m-%d"), "APPROVED", "Dr. Sunita Verma", "GP-2026-6610", now_str),
        (36, "Lavanya Krishnan", "Room 31", "Attending national bio-genomics workshop in Hyderabad", (today + timedelta(days=5)).strftime("%Y-%m-%d"), (today + timedelta(days=9)).strftime("%Y-%m-%d"), "PENDING", None, None, now_str),
        (41, "Dr. Subhash Bose", "Room 33", "Invited Keynote Speaker at ACM Sigmod", (today + timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=5)).strftime("%Y-%m-%d"), "APPROVED", "Prof. Anand Nair", "GP-2026-9901", now_str),
        (49, "Raghuram Rajan", "Room 46", "Delivering invited guest lecture at IIM Ahmedabad", (today + timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=5)).strftime("%Y-%m-%d"), "APPROVED", "Prof. Sharmila Tagore", "GP-2026-8899", now_str)
    ]
    cursor.executemany("""
    INSERT INTO leave_requests (student_id, student_name, room_number, reason, from_date, to_date, status, approved_by, gate_pass_code, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, leaves_data)

    # ==============================================================================
    # 8. FEE RECORDS (All 50 Students Seeded with Detailed Real-World Ledgers)
    # ==============================================================================
    fee_records_data = []
    base_fee_map = {1: 85000, 2: 65000, 3: 50000, 4: 42000}
    
    # Specific known overdue/partial students
    overdue_set = {4, 9, 31}
    partial_set = {14, 20, 23}

    for s in all_inserted_stus:
        s_id = s["id"]
        s_name = s["name"]
        
        # Calculate fee based on student ID tier
        if s_id in [49, 50]:
            tot = 115000
        elif s_id in [41, 42, 43, 44, 45, 46, 47, 48]:
            tot = 95000
        elif s_id in [1, 6, 11, 12]:
            tot = 85000
        elif s_id in [2, 3, 7, 8, 16, 17, 18, 19]:
            tot = 68000
        else:
            tot = 55000

        if s_id in overdue_set:
            pd_amt = 20000 if s_id == 4 else 0
            due_amt = tot - pd_amt
            st = "OVERDUE"
            l_date = "2026-08-01" if pd_amt > 0 else None
            t_ref = "TXN-UPI-99210" if pd_amt > 0 else None
        elif s_id in partial_set:
            pd_amt = tot // 2
            due_amt = tot - pd_amt
            st = "PARTIAL"
            l_date = "2026-08-14"
            t_ref = f"TXN-PART-{s_id}8819"
        else:
            pd_amt = tot
            due_amt = 0
            st = "PAID"
            bank_tag = ["SBI", "HDFC", "ICICI", "AXIS", "KOTAK", "UPI"][s_id % 6]
            l_date = f"2026-08-{10 + (s_id % 5):02d}"
            t_ref = f"TXN-{bank_tag}-{10000 + s_id * 137}"

        fee_records_data.append((s_id, s_name, tot, pd_amt, due_amt, "2026-08-15", st, l_date, t_ref))

    cursor.executemany("""
    INSERT INTO fee_records (student_id, student_name, total_amount, amount_paid, amount_due, due_date, status, last_payment_date, transaction_ref)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fee_records_data)

    # ==============================================================================
    # 9. MESS MENU (Complete 28 Meals - 7 Days x 4 Meals)
    # ==============================================================================
    menu_data = [
        ("Monday", "Breakfast", "Masala Dosa, Sambar, Coconut Chutney, Boiled Eggs, Tea/Coffee", "Fresh Banana", 450),
        ("Monday", "Lunch", "Chapati, Dal Tadka, Paneer Butter Masala, Steamed Rice, Curd, Green Salad", "Gulab Jamun", 750),
        ("Monday", "Snacks", "Samosa with Mint Chutney, Adrak Chai", "Biscuits", 280),
        ("Monday", "Dinner", "Phulka, Mixed Veg Kurma, Jeera Rice, Tomato Rasam, Butter Milk", "Fruit Custard", 680),

        ("Tuesday", "Breakfast", "Poha with Sev & Peanuts, Sprouts, Bread Toast & Jam, Tea/Coffee", "Watermelon Slices", 380),
        ("Tuesday", "Lunch", "Roti, Rajma Masala, Aloo Gobi, Steamed Basmati Rice, Papad, Curd", "Moong Dal Halwa", 720),
        ("Tuesday", "Snacks", "Veg Cutlet, Tomato Ketchup, South Indian Filter Coffee", "Rusks", 260),
        ("Tuesday", "Dinner", "Methi Paratha, Dal Makhani, Veg Pulao, Fresh Curd, Pickle", "Rice Kheer", 710),

        ("Wednesday", "Breakfast", "Idli & Medu Vada with Chutney & Sambar, Boiled Egg/Fruit, Tea/Coffee", "Apple Slices", 420),
        ("Wednesday", "Lunch", "Chapati, Chana Masala, Bhindi Fry, Steamed Rice, Dal Fry, Curd", "Hot Jalebi", 740),
        ("Wednesday", "Snacks", "Bread Pakora, Green Coriander Chutney, Masala Chai", "Cookies", 310),
        ("Wednesday", "Dinner", "Egg Curry / Kadai Paneer, Roti, Peas Pulao, Yellow Dal, Onion Salad", "Vanilla Ice Cream", 760),

        ("Thursday", "Breakfast", "Aloo Paratha with White Butter, Curd, Pickle, Tea/Coffee", "Fresh Orange", 490),
        ("Thursday", "Lunch", "Poori, Aloo Tamatar Sabzi, Dal Palak, Jeera Rice, Boondi Raita", "Rasgulla", 780),
        ("Thursday", "Snacks", "Bhel Puri with Chutneys, Hot Lemon Tea", "Mixture", 230),
        ("Thursday", "Dinner", "Roti, Soya Chaap Curry, Lemon Rice, Pepper Rasam, Curd", "Fruit Salad", 650),

        ("Friday", "Breakfast", "Upma with Coconut Chutney, Sheera (Kesari Bath), Boiled Eggs, Tea/Coffee", "Fresh Banana", 410),
        ("Friday", "Lunch", "Chapati, Dum Aloo Kashmiri, Dal Maharani, Steamed Rice, Boondi Raita", "Gajar Halwa", 730),
        ("Friday", "Snacks", "Pyaz Kachori with Sweet Tamarind Chutney, Ginger Tea", "Namkeen", 290),
        ("Friday", "Dinner", "South Indian Special Meals: Rice, Sambar, Poriyal, Rasam, Appalam, Payasam", "Semiyan Payasam", 690),

        ("Saturday", "Breakfast", "Uttapam, Sambar, Coriander Chutney, Tea/Coffee", "Papaya Slices", 430),
        ("Saturday", "Lunch", "Roti, Bhindi Masala, Dal Tadka, Lemon Rice, Boondi Raita", "Sweet Boondi", 710),
        ("Saturday", "Snacks", "Veg Grilled Sandwich, Tomato Sauce, Tea", "Biscuits", 260),
        ("Saturday", "Dinner", "Special Schezwan Fried Rice, Veg Manchurian, Spring Rolls, Hot Chocolate Fudge", "Hot Fudge Brownie", 850),

        ("Sunday", "Breakfast", "Chole Bhature with Pickled Onion, Sweet Punjabi Lassi, Coffee", "Fresh Fruit Bowl", 620),
        ("Sunday", "Lunch", "Special Hyderabadi Dum Biryani (Veg/Chicken), Mirchi Ka Salan, Raita", "Shahi Tukda", 920),
        ("Sunday", "Snacks", "Dhokla with Green Chilli & Mustard Tadka, Mint Tea", "Khakhra", 240),
        ("Sunday", "Dinner", "Light Comfort Dinner: Moong Dal Khichdi, Gujarati Kadhi, Papad, Achar, Golden Turmeric Milk", "Sweet Curd", 550)
    ]
    cursor.executemany("""
    INSERT INTO mess_menu (day_of_week, meal_type, items, special_item, calories)
    VALUES (?, ?, ?, ?, ?)
    """, menu_data)

    # ==============================================================================
    # 10. VISITORS (16 Realistic Campus Security Logs)
    # ==============================================================================
    visitors_data = [
        (1, "Aarav Sharma", "Ramesh Sharma", "Father", "+91 98111 22231", (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), None, "Semester fee discussion & family visit", "IN_PREMISES"),
        (2, "Vikramaditya Roy", "Debashis Roy", "Father", "+91 98111 22232", (now - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=1, hours=1)).strftime("%Y-%m-%d %H:%M"), "Delivered sports gear", "CHECKED_OUT"),
        (3, "Rohan Kulkarni", "Suresh Kulkarni", "Father", "+91 98111 22233", (now - timedelta(days=2, hours=4)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=2, hours=2)).strftime("%Y-%m-%d %H:%M"), "Family weekend greeting", "CHECKED_OUT"),
        (6, "Ananya Sen", "Pradip Sen", "Father", "+91 98111 22236", (now - timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=1, hours=1)).strftime("%Y-%m-%d %H:%M"), "Delivered hardware project kit", "CHECKED_OUT"),
        (7, "Pooja Hegde", "Venkatesh Hegde", "Father", "+91 98111 22237", (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"), None, "Dropping off seasonal home snacks", "IN_PREMISES"),
        (8, "Sneha Iyer", "Subramanian Iyer", "Father", "+91 98111 22238", (now - timedelta(days=3, hours=5)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=3, hours=3)).strftime("%Y-%m-%d %H:%M"), "Delivered winter bedding", "CHECKED_OUT"),
        (10, "Devansh Pandey", "Harish Pandey", "Father", "+91 98111 22240", (now - timedelta(days=2, hours=3)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=2, hours=1)).strftime("%Y-%m-%d %H:%M"), "Medical insurance document signing", "CHECKED_OUT"),
        (13, "Siddharth Verma", "Mahesh Verma", "Father", "+91 98111 22243", (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"), None, "College hostel visit", "IN_PREMISES"),
        (16, "Rhea Singhania", "Vijay Singhania", "Father", "+91 98111 22246", (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"), None, "Campus visit and laptop handover", "IN_PREMISES"),
        (18, "Nikhil Chawla", "Anil Chawla", "Father", "+91 98111 22248", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=3, hours=-2)).strftime("%Y-%m-%d %H:%M"), "Semester fee clearance", "CHECKED_OUT"),
        (20, "Priyanka Reddy", "Mallikarjun Reddy", "Father", "+91 98111 22250", (now - timedelta(days=1, hours=6)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=1, hours=3)).strftime("%Y-%m-%d %H:%M"), "Family lunch outing", "CHECKED_OUT"),
        (22, "Karan Singhal", "Deepak Singhal", "Father", "+91 98111 22252", (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"), None, "Dropping off research books", "IN_PREMISES"),
        (25, "Manish Tiwari", "Brijesh Tiwari", "Father", "+91 98111 22255", (now - timedelta(days=2, hours=6)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=2, hours=4)).strftime("%Y-%m-%d %H:%M"), "Health check consultation", "CHECKED_OUT"),
        (30, "Deepika Pillai", "Muraleedharan Pillai", "Father", "+91 98111 22260", (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"), None, "Campus recruitment guidance", "IN_PREMISES"),
        (41, "Dr. Subhash Bose", "Prof. Amartya Bose", "Brother", "+91 98111 22271", (now - timedelta(days=1, hours=3)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=1, hours=1)).strftime("%Y-%m-%d %H:%M"), "Academic paper collaboration", "CHECKED_OUT"),
        (49, "Raghuram Rajan", "Dr. Govindarajan R", "Father", "+91 98111 22279", (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"), None, "Executive suite meeting", "IN_PREMISES")
    ]
    cursor.executemany("""
    INSERT INTO visitors (student_id, student_name, visitor_name, relation, phone, entry_time, exit_time, purpose, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, visitors_data)

    # ==============================================================================
    # 11. NOTICES (10 Official Campus Circulars)
    # ==============================================================================
    notices_data = [
        ("Hostel Annual Fest 'SANSKRITI 2026' Registrations Open!", "All hostel residents are invited to participate in the upcoming cultural & sports tournament scheduled from Sept 5-8. Cash prizes and trophies up for grabs across 20+ events.", "Event", "NORMAL", "All Students", "Hostel Cultural Committee", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")),
        ("Water Tank Cleaning & Maintenance Notice - Aryabhata Block", "Overhead water supply will be temporarily shut down tomorrow between 10:00 AM to 01:00 PM for deep disinfection and maintenance. Please store sufficient water.", "Maintenance", "HIGH", "Aryabhata Block Residents", "Chief Maintenance Warden", (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")),
        ("Mandatory Night Attendance Curfew Timing Reminder", "Strict 09:30 PM biometric night curfew applies to all blocks. Late entries without warden-approved gate pass will lead to disciplinary remarks and automated SMS to parents.", "Emergency", "URGENT", "All Students", "Chief Proctor & Warden Office", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M")),
        ("Special Sunday Feast & Feedback Poll", "Vote on the Student Portal for next Sunday's special dessert choice (Shahi Tukda vs Hot Fudge Brownie with Ice Cream).", "Mess", "NORMAL", "All Students", "Mess Student Representative", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M")),
        ("Campus Wi-Fi Core Router Upgrade Scheduled", "IT Services will be migrating the main optical backbone to 10Gbps mesh on Saturday midnight (01:00 AM – 04:00 AM). Brief internet intermittent downtime expected.", "Maintenance", "NORMAL", "All Hostels", "Chief IT Officer", (now - timedelta(days=1, hours=6)).strftime("%Y-%m-%d %H:%M")),
        ("Annual Inter-Hostel Cricket & Badminton Tournament Fixtures", "Matches commence this Saturday at Campus Sports Complex. View team draws and fixture schedules on the notice board.", "Event", "NORMAL", "All Hostels", "Sports Secretary", (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M")),
        ("Fire Safety Drill & Evacuation Simulation in Girls Hostel", "Mandatory fire evacuation rehearsal scheduled for Gargi Bhavan on Friday 04:30 PM. Fire alarms will sound for 15 minutes.", "Emergency", "HIGH", "Gargi Bhavan Residents", "Campus Disaster Management Cell", (now - timedelta(days=2, hours=5)).strftime("%Y-%m-%d %H:%M")),
        ("Semester Exam Quiet Hours Enforcement (10:00 PM – 06:00 AM)", "In view of mid-term examinations, strict silence hours must be observed across all hostel corridors, balconies, and study rooms.", "General", "HIGH", "All Students", "Chief Warden Office", (now - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M")),
        ("Hostel Gymnasium New Equipment Induction & Timings", "New Olympic squat racks, dumbbells, and cardio treadmills have been added to the Central Sports Gym. Morning: 06:00 - 09:00 AM, Evening: 05:00 - 09:30 PM.", "General", "NORMAL", "All Hostels", "Sports Officer", (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M")),
        ("Laundry Facility Tokens & Smart App Integration", "Automated smart RFID washers in Block A & G basement now accept digital coin recharges through the student hostel portal.", "General", "NORMAL", "All Hostels", "Hostel Facilities Manager", (now - timedelta(days=3, hours=4)).strftime("%Y-%m-%d %H:%M"))
    ]
    cursor.executemany("""
    INSERT INTO notices (title, content, category, priority, target_audience, posted_by, posted_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, notices_data)

    conn.commit()


def ensure_student_users():
    """Ensures that all students registered in the database have corresponding user accounts."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Fetch all students
    cursor.execute("SELECT * FROM students")
    all_students = [dict(r) for r in cursor.fetchall()]
    
    for s in all_students:
        s_id = s["id"]
        code = s["student_id_code"]
        name = s["name"]
        email = s["email"]
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE student_id = ? OR LOWER(username) = ?", (s_id, code.lower()))
        existing = cursor.fetchone()
        if not existing:
            default_uname = code.lower().replace("-", "")
            cursor.execute("""
            INSERT INTO users (username, password, role, full_name, email, student_id)
            VALUES (?, ?, 'STUDENT', ?, ?, ?)
            """, (default_uname, "student123", name, email, s_id))
            
    conn.commit()
    conn.close()


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

# --------------------------------------------------------------------------------------
# Authentication & User Management Helpers
# --------------------------------------------------------------------------------------

def authenticate_user(identifier: str, password: str, allowed_roles=None):
    """
    Authenticates a user via username, email, or Student ID Code (e.g. STU-1001 or STU1001).
    Returns (success: bool, user_dict_or_error: dict|str, student_dict: dict|None)
    """
    if not identifier or not password:
        return False, "Please enter both identifier and password.", None

    clean_id = identifier.strip()
    clean_pass = password.strip()
    conn = get_connection()
    cursor = conn.cursor()

    # 1. First check directly in users table by username or email
    cursor.execute("""
    SELECT * FROM users 
    WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)
    """, (clean_id, clean_id))
    user_row = cursor.fetchone()

    # 2. If not found and identifier might be a student code (e.g. STU-1001 or STU1001)
    if not user_row:
        cursor.execute("""
        SELECT u.* FROM users u 
        JOIN students s ON u.student_id = s.id 
        WHERE LOWER(s.student_id_code) = LOWER(?) OR LOWER(REPLACE(s.student_id_code, '-', '')) = LOWER(?)
        """, (clean_id, clean_id.replace("-", "")))
        user_row = cursor.fetchone()

    # 3. If still not found, check if it directly matches a student record without user link
    if not user_row:
        cursor.execute("""
        SELECT * FROM students 
        WHERE LOWER(student_id_code) = LOWER(?) OR LOWER(email) = LOWER(?)
        """, (clean_id, clean_id))
        stu_match = cursor.fetchone()
        if stu_match:
            s_dict = dict(stu_match)
            default_uname = s_dict["student_id_code"].lower().replace("-", "")
            cursor.execute("""
            INSERT INTO users (username, password, role, full_name, email, student_id)
            VALUES (?, 'student123', 'STUDENT', ?, ?, ?)
            """, (default_uname, s_dict["name"], s_dict["email"], s_dict["id"]))
            conn.commit()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,))
            user_row = cursor.fetchone()

    conn.close()

    if not user_row:
        return False, "Account not found. Please check your username, email, or student ID.", None

    user = dict(user_row)

    # Verify password
    if user["password"] != clean_pass:
        return False, "Incorrect password. Please verify your credentials and try again.", None

    # Role validation
    if allowed_roles:
        if isinstance(allowed_roles, str) and user["role"] != allowed_roles:
            return False, f"Access restricted: This portal is for {allowed_roles} accounts only.", None
        elif isinstance(allowed_roles, (list, tuple)) and user["role"] not in allowed_roles:
            return False, f"Access restricted: Role '{user['role']}' is not authorized for this section.", None

    # If role is student, load full student profile
    student_profile = None
    if user.get("student_id"):
        student_profile = get_student_profile(user["student_id"])

    return True, user, student_profile


def register_student_account(student_data: dict, password: str = "student123"):
    """
    Registers a new student and creates their login user account.
    Returns (success: bool, message: str, user_dict: dict|None)
    """
    conn = get_connection()
    cursor = conn.cursor()

    code = student_data.get("student_id_code", "").strip().upper()
    username = student_data.get("username", "").strip().lower() or code.lower().replace("-", "")
    email = student_data.get("email", "").strip().lower()
    name = student_data.get("name", "").strip()

    if not code or not name or not email:
        conn.close()
        return False, "Student ID code, Full Name, and Email are required fields.", None

    # Check for duplicates
    cursor.execute("SELECT id FROM students WHERE UPPER(student_id_code) = ? OR LOWER(email) = ?", (code, email))
    if cursor.fetchone():
        conn.close()
        return False, f"A student with ID '{code}' or Email '{email}' already exists.", None

    cursor.execute("SELECT id FROM users WHERE LOWER(username) = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, f"Username '{username}' is already taken. Please choose another.", None

    try:
        # Insert student
        cursor.execute("""
        INSERT INTO students (
            student_id_code, name, email, phone, gender, department, year, room_id,
            sleep_habit, study_habit, cleanliness, dietary_pref, fee_status, parent_name, parent_phone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            code,
            name,
            email,
            student_data.get("phone", "+91 91234 00000"),
            student_data.get("gender", "Male"),
            student_data.get("department", "Computer Science"),
            int(student_data.get("year", 1)),
            student_data.get("room_id", None),
            student_data.get("sleep_habit", "Flexible"),
            student_data.get("study_habit", "Moderate"),
            student_data.get("cleanliness", "High"),
            student_data.get("dietary_pref", "Veg"),
            student_data.get("fee_status", "PAID"),
            student_data.get("parent_name", "Guardian Name"),
            student_data.get("parent_phone", "+91 98111 00000")
        ))
        student_id = cursor.lastrowid

        # Insert user account
        cursor.execute("""
        INSERT INTO users (username, password, role, full_name, email, student_id)
        VALUES (?, ?, 'STUDENT', ?, ?, ?)
        """, (username, password or "student123", name, email, student_id))
        user_id = cursor.lastrowid

        # Initialize fee record
        cursor.execute("""
        INSERT INTO fee_records (student_id, student_name, total_amount, amount_paid, amount_due, due_date, status, last_payment_date, transaction_ref)
        VALUES (?, ?, 65000, 65000, 0, '2026-08-15', 'PAID', '2026-08-15', ?)
        """, (student_id, name, f"TXN-REG-{random.randint(10000, 99999)}"))

        conn.commit()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        new_user = dict(cursor.fetchone())
        conn.close()

        student_profile = get_student_profile(student_id)
        return True, "Registration successful!", {"user": new_user, "student": student_profile}

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Registration failed: {str(e)}", None


def get_student_profile(student_id: int) -> dict:
    """Fetches complete student profile including room, roommates, leaves, fee, and complaints."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    s_row = cursor.fetchone()
    if not s_row:
        conn.close()
        return {}

    stu = dict(s_row)

    # Room info
    room_info = None
    roommates = []
    if stu.get("room_id"):
        cursor.execute("SELECT * FROM rooms WHERE id = ?", (stu["room_id"],))
        r_row = cursor.fetchone()
        if r_row:
            room_info = dict(r_row)

        cursor.execute("SELECT id, student_id_code, name, department, year, phone, email FROM students WHERE room_id = ? AND id != ?", (stu["room_id"], student_id))
        roommates = [dict(r) for r in cursor.fetchall()]

    stu["room_details"] = room_info
    stu["roommates"] = roommates

    # Fee details
    cursor.execute("SELECT * FROM fee_records WHERE student_id = ? ORDER BY id DESC LIMIT 1", (student_id,))
    fee_row = cursor.fetchone()
    stu["fee_details"] = dict(fee_row) if fee_row else None

    # Attendance summary
    cursor.execute("SELECT status, COUNT(*) as cnt FROM attendance WHERE student_id = ? GROUP BY status", (student_id,))
    att_rows = cursor.fetchall()
    att_summary = {r["status"]: r["cnt"] for r in att_rows}
    stu["attendance_summary"] = att_summary

    # Active gate passes
    cursor.execute("SELECT * FROM leave_requests WHERE student_id = ? ORDER BY id DESC", (student_id,))
    stu["leaves"] = [dict(r) for r in cursor.fetchall()]

    # Student complaints
    cursor.execute("SELECT * FROM complaints WHERE student_id = ? ORDER BY id DESC", (student_id,))
    stu["complaints"] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return stu
