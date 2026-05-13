# 📅 JSS College Timetable Generator
**JSS College, Ooty Road, Mysore – 570025**  
**Academic Year 2025–26 | Even Semester**

A production-ready Django web application that reads timetable data directly from uploaded Excel files and displays conflict-free, role-based schedules.

---

## 🚀 Quick Start

```bash
# Clone / extract project
cd timetable_project

# Install dependencies (dev mode - SQLite)
pip install -r requirements_dev.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver

# Open in browser
# http://127.0.0.1:8000
```

---

## 🔐 Default Login Credentials

| Role    | Username  | Password   |
|---------|-----------|------------|
| Admin   | `admin`   | `admin123` |
| Staff   | `staff1`  | `staff123` |
| Student | `student1`| `student123`|

---

## 📂 Project Structure

```
timetable_project/
├── accounts/               # User auth (Admin / Staff / Student)
│   ├── models.py           # Custom User model with roles
│   ├── views.py            # Login, logout, register
│   └── urls.py
├── timetable/              # Core timetable app
│   ├── models.py           # TimetableEntry, ConflictLog
│   ├── views.py            # Dashboard, upload, view, conflicts
│   ├── excel_parser.py     # ⭐ Excel parsing engine
│   ├── urls.py
│   └── templatetags/
│       └── timetable_tags.py  # get_item, split template filters
├── management/             # Admin management app
│   ├── models.py           # Subject, Room, Class, StaffProfile
│   ├── views.py            # CRUD for subjects/rooms/staff/classes
│   └── urls.py
├── templates/
│   ├── base.html           # Dark sidebar layout
│   ├── accounts/           # Login, register pages
│   ├── timetable/          # Dashboard, grid view, upload, conflicts
│   └── management/         # Subjects, rooms, staff, classes
├── media/uploads/          # Uploaded Excel files
├── static/                 # CSS, JS, images
├── requirements.txt        # Production dependencies
├── requirements_dev.txt    # Dev dependencies (SQLite)
└── setup.sh                # Auto setup script
```

---

## 📊 Excel File Formats Supported

### 1. Student Timetable File (`TIME_TABLE_2025-26_STUDENT.xls`)
- Multiple class sections in one sheet
- Each section starts with a class header (e.g., `I YEAR BCom - A SECTION`)
- Days listed as `MONDAY`, `TUESDAY`, etc.
- Cells contain: `SUBJECT_CODE - ROOM_NUMBER` (e.g., `COM - 215`)

### 2. Room Mapping File (`Room_Numbers_with_class.xlsx`)
- 6 sheets: `MON`, `TUE`, `WED`, `THRU`, `FRI`, `SAT`
- Column A: Room number
- Columns B–K: Time slots (8 AM – 5:30 PM) with subject codes

---

## 🏗️ Django Models

```
User (accounts)
  └── role: admin | staff | student

Subject (management)
  └── code, name, type, hours_per_week

Room (management)
  └── room_number, room_type, capacity

Department → Class (management)
  └── year, section, semester

StaffProfile (management)
  └── user ↔ subjects (M2M)

TimetableEntry (timetable)
  └── class_label, day, time_slot
  └── raw_entry, raw_subject_code, raw_room_number
  └── subject (FK), room (FK), staff (FK)
  └── has_conflict, conflict_detail

ConflictLog (timetable)
  └── conflict_type, day, time_slot, detail
  └── entry_1, entry_2, resolved
```

---

## 👥 User Roles

| Feature                    | Admin | Staff | Student |
|----------------------------|:-----:|:-----:|:-------:|
| Upload Excel               | ✅    | ❌    | ❌      |
| Process & generate         | ✅    | ❌    | ❌      |
| Manage subjects/rooms/staff| ✅    | ❌    | ❌      |
| View all timetables        | ✅    | ✅    | ✅      |
| View own schedule (staff)  | ✅    | ✅    | ❌      |
| View conflicts             | ✅    | ❌    | ❌      |
| Resolve conflicts          | ✅    | ❌    | ❌      |
| Regenerate timetable       | ✅    | ❌    | ❌      |

---

## ⚙️ MySQL (Production) Setup

1. Create MySQL database:
```sql
CREATE DATABASE jss_timetable CHARACTER SET utf8mb4;
CREATE USER 'jss_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON jss_timetable.* TO 'jss_user'@'localhost';
```

2. Edit `timetable_project/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jss_timetable',
        'USER': 'jss_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

3. Install mysqlclient: `pip install mysqlclient`

---

## 🧠 Excel Parser Logic

The parser (`timetable/excel_parser.py`) does:

1. **Reads** the Excel file using pandas
2. **Detects** class section headers (e.g., `I YEAR BCom - A SECTION`)
3. **Identifies** day rows (MONDAY, TUESDAY...)
4. **Maps** columns to time slots (8AM → 5:30PM)
5. **Parses** each cell: `COM - 215` → subject=`COM`, room=`215`
6. **Maps** subject codes to `Subject` model objects
7. **Maps** room numbers to `Room` model objects
8. **Detects conflicts**: same room at same time for different classes
9. **Stores** all entries in `TimetableEntry` table

---

## 🌟 Key Features

- ✅ **Real data only** – No random generation; reads your actual Excel files
- ✅ **Conflict detection** – Room double-booking detected automatically
- ✅ **Role-based access** – Admin, Staff, Student views
- ✅ **Dark UI** – Professional Bootstrap 5 dark theme
- ✅ **38 subjects** pre-seeded from your Excel data
- ✅ **40 rooms** pre-seeded from room numbers (106–227)
- ✅ **1071+ timetable entries** parsed from your uploaded file
- ✅ **38 class sections** displayed in grid view

---
![image alt](https://github.com/manojsm7140-wq/Time-table-generator/blob/235dd7cb207ccf4d5f984a1725c4cacfce65c849/WhatsApp%20Image%202026-04-24%20at%2012.10.32.jpeg)
                    

![image alt](https://github.com/manojsm7140-wq/Time-table-generator/blob/7e92f023f90e2589f2cde5923616f5cb1a42b7e7/WhatsApp%20Image%202026-04-24%20at%2012.10.49.jpeg)
                      

![image alt](https://github.com/manojsm7140-wq/Time-table-generator/blob/dbb2c0302fa9fede20968e0368f1f24e6434354c/WhatsApp%20Image%202026-04-24%20at%2012.11.10.jpeg)


![image alt](https://github.com/manojsm7140-wq/Time-table-generator/blob/a4626fae25f520ec00dec6308672f21488a3460d/WhatsApp%20Image%202026-04-24%20at%2012.11.37.jpeg)


![image alt](https://github.com/manojsm7140-wq/Time-table-generator/blob/a1d8117fa065f5ab3bf6f5ea2697410ee4817a60/WhatsApp%20Image%202026-04-24%20at%2012.11.24.jpeg)


![image alt](https://github.com/manojsm7140-wq/Time-table-generator/blob/8dca950e9c76ae0a45c391cd23594cc2a6759d67/WhatsApp%20Image%202026-04-24%20at%2012.11.50.jpeg)



