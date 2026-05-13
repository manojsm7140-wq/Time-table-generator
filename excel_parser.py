"""
Excel Parser for JSS College Timetable Generator
Parses both:
1. Room_Numbers_with_class.xlsx - Room-based schedule (per day sheet)
2. TIME_TABLE_2025-26_STUDENT.xls - Class-wise timetable (SUBJECT-ROOM format)
"""
import re
import pandas as pd
from collections import defaultdict

TIME_SLOT_MAP = {
    0: '08:00-09:00',
    1: '09:00-10:00',
    2: '10:00-11:00',
    3: '11:00-12:00',
    4: '12:00-13:00',
    5: '13:00-14:00',
    6: '14:00-14:30',  # LUNCH BREAK col
    7: '14:30-15:30',
    8: '15:30-16:30',
    9: '16:30-17:30',
}

DAY_SHEET_MAP = {
    'MON': 'MON', 'TUE': 'TUE', 'WED': 'WED',
    'THRU': 'THU', 'FRI': 'FRI', 'SAT': 'SAT',
}

DAYS_ORDERED = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
DAY_NAMES = {
    'MONDAY': 'MON', 'TUESDAY': 'TUE', 'WEDNESDAY': 'WED',
    'THURSDAY': 'THU', 'FRIDAY': 'FRI', 'SATURDAY': 'SAT',
}


def parse_entry(cell_value):
    """
    Parse a timetable cell like 'COM - 215', 'COM-215', 'COM 215', 'EVS-127'
    Returns (subject_code, room_number) or (None, None)
    """
    if not cell_value or str(cell_value).strip() in ('', 'nan', 'NaN', 'LUNCH BREAK'):
        return None, None
    val = str(cell_value).strip()
    # Match: SUBJ - ROOM or SUBJ-ROOM (dash separator, optional spaces)
    match = re.match(r'^(.+?)\s*[-–]\s*(\d{3,})\s*$', val)
    if match:
        return match.group(1).strip().upper(), match.group(2).strip()
    # Match: SUBJ ROOM (space-separated, room is 3+ trailing digits)
    match2 = re.match(r'^([A-Za-z][A-Za-z0-9 /]+?)\s{1,3}(\d{3,})\s*$', val)
    if match2:
        return match2.group(1).strip().upper(), match2.group(2).strip()
    # No room number - just subject code
    if val and val not in ('nan',):
        return val.strip().upper(), None
    return None, None


def parse_student_timetable(filepath):
    """
    Parse TIME_TABLE_2025-26_STUDENT.xls
    Returns list of dicts: {class_label, day, time_slot, raw_entry, subject_code, room_number}
    """
    results = []
    errors = []

    try:
        df = pd.read_excel(filepath, sheet_name=0, header=None, dtype=str)
    except Exception as e:
        return results, [f"Failed to read file: {e}"]

    df = df.fillna('')

    # Find time slot columns: scan for row with '8.00' or 'WEEK'
    time_cols = {}
    header_row_idx = None

    for i, row in df.iterrows():
        row_vals = [str(v).strip() for v in row.values]
        if any('8.00' in v or '9.00' in v or 'WEEK' in v for v in row_vals):
            # This is a header row - extract column mapping
            for col_idx, val in enumerate(row_vals):
                val = val.replace('\n', ' ').strip()
                if '8.00' in val or '8:00' in val:
                    time_cols[col_idx] = '08:00-09:00'
                elif '9.00' in val or '9:00' in val:
                    time_cols[col_idx] = '09:00-10:00'
                elif '10.00' in val or '10:00' in val:
                    time_cols[col_idx] = '10:00-11:00'
                elif '11.00' in val or '11:00' in val:
                    time_cols[col_idx] = '11:00-12:00'
                elif '12.00' in val or '12:00' in val:
                    time_cols[col_idx] = '12:00-13:00'
                elif '1.00' in val or '13:00' in val or '1.00 - 2' in val:
                    time_cols[col_idx] = '13:00-14:00'
                elif '2.30' in val or '14:30' in val or '2.30 - 3' in val:
                    time_cols[col_idx] = '14:30-15:30'
                elif '3.30' in val or '15:30' in val:
                    time_cols[col_idx] = '15:30-16:30'
                elif '4.30' in val or '16:30' in val:
                    time_cols[col_idx] = '16:30-17:30'
            break

    # Default column mapping if header not found clearly
    if not time_cols:
        # Based on observed structure: cols 4,6,8,10,12,14,16,18
        defaults = {4:'10:00-11:00', 6:'11:00-12:00', 8:'12:00-13:00',
                    10:'13:00-14:00', 14:'14:30-15:30', 16:'15:30-16:30', 18:'16:30-17:30'}
        time_cols = defaults

    current_class = None
    current_day = None

    for i, row in df.iterrows():
        col0 = str(row.iloc[0]).strip()

        # Detect class label rows
        if any(keyword in col0.upper() for keyword in ['YEAR', 'BCom', 'BCA', 'B.SC', 'BA', 'B.COM', 'SECTION']):
            current_class = col0.strip()
            current_day = None
            continue

        # Detect day rows
        col0_upper = col0.upper()
        if col0_upper in DAY_NAMES:
            current_day = DAY_NAMES[col0_upper]

            if current_class and current_day:
                # Parse all time slots in this row
                for col_idx, slot in time_cols.items():
                    if col_idx < len(row):
                        cell = str(row.iloc[col_idx]).strip()
                        if cell and cell not in ('', 'nan', 'NaN'):
                            if 'LUNCH' in cell.upper():
                                continue
                            subject_code, room_number = parse_entry(cell)
                            results.append({
                                'class_label': current_class,
                                'day': current_day,
                                'time_slot': slot,
                                'raw_entry': cell,
                                'subject_code': subject_code or '',
                                'room_number': room_number or '',
                            })
                # Also check subsequent rows for same day (multiple entries per slot)
                for next_i in range(i + 1, min(i + 4, len(df))):
                    next_row = df.iloc[next_i]
                    next_col0 = str(next_row.iloc[0]).strip()
                    if next_col0 and next_col0 not in ('', 'nan') and next_col0.upper() not in DAY_NAMES:
                        # continuation row
                        for col_idx, slot in time_cols.items():
                            if col_idx < len(next_row):
                                cell = str(next_row.iloc[col_idx]).strip()
                                if cell and cell not in ('', 'nan', 'NaN'):
                                    if 'LUNCH' in cell.upper():
                                        continue
                                    subject_code, room_number = parse_entry(cell)
                                    if subject_code:
                                        results.append({
                                            'class_label': current_class,
                                            'day': current_day,
                                            'time_slot': slot,
                                            'raw_entry': cell,
                                            'subject_code': subject_code or '',
                                            'room_number': room_number or '',
                                        })
    return results, errors


def parse_room_mapping(filepath):
    """
    Parse Room_Numbers_with_class.xlsx
    Returns dict: {day: [{room_number, time_slot, subject_code}]}
    """
    results = defaultdict(list)
    errors = []

    try:
        xl = pd.ExcelFile(filepath)
    except Exception as e:
        return results, [f"Failed to read file: {e}"]

    SLOT_COL_MAP = {
        1: '08:00-09:00',
        2: '09:00-10:00',
        3: '10:00-11:00',
        4: '11:00-12:00',
        5: '12:00-13:00',
        6: '13:00-14:00',
        7: '14:00-14:30',
        8: '14:30-15:30',
        9: '15:30-16:30',
        10: '16:30-17:30',
    }

    for sheet_name in xl.sheet_names:
        day_key = DAY_SHEET_MAP.get(sheet_name.upper(), sheet_name[:3].upper())
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name, header=None, dtype=str)
            df = df.fillna('')

            for i, row in df.iterrows():
                col0 = str(row.iloc[0]).strip()
                if not col0 or col0 in ('ROOM NO', 'MONDAY', 'TUESDAY', 'WEDNESDAY',
                                         'THURSDAY', 'FRIDAY', 'SATURDAY', 'nan'):
                    continue
                # col0 is room number
                room_num = col0.replace(' S', '').strip()
                for col_idx, slot in SLOT_COL_MAP.items():
                    if col_idx < len(row):
                        cell = str(row.iloc[col_idx]).strip()
                        if cell and cell not in ('', 'nan', 'NaN') and 'LUNCH' not in cell.upper():
                            subject_code = cell.upper().replace('\n', ' ')
                            results[day_key].append({
                                'room_number': room_num,
                                'time_slot': slot,
                                'subject_code': subject_code,
                            })
        except Exception as e:
            errors.append(f"Sheet {sheet_name}: {e}")

    return dict(results), errors


def detect_conflicts(entries):
    """
    Detect scheduling conflicts in parsed entries.
    Returns list of conflict dicts.
    """
    conflicts = []
    # Group by day+time_slot+room
    room_slots = defaultdict(list)
    for entry in entries:
        if entry.get('room_number'):
            key = (entry['day'], entry['time_slot'], entry['room_number'])
            room_slots[key].append(entry)

    for (day, slot, room), slot_entries in room_slots.items():
        if len(slot_entries) > 1:
            classes = [e['class_label'] for e in slot_entries]
            conflicts.append({
                'conflict_type': 'room_double_booking',
                'day': day,
                'time_slot': slot,
                'detail': f"Room {room} double-booked on {day} at {slot}: {', '.join(classes)}",
                'entry_1': str(slot_entries[0]),
                'entry_2': str(slot_entries[1]),
            })

    return conflicts


def build_timetable_grid(entries, class_label=None):
    """
    Build a 2D grid dict for template rendering.
    Returns: {day: {time_slot: entry_or_list}}
    """
    grid = {day: {} for day in DAYS_ORDERED}
    for entry in entries:
        if class_label and entry.get('class_label') != class_label:
            continue
        day = entry.get('day')
        slot = entry.get('time_slot')
        if day in grid:
            if slot not in grid[day]:
                grid[day][slot] = []
            grid[day][slot].append(entry)
    return grid
