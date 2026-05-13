from django.db import models
from management.models import Subject, Room, Class, StaffProfile

TIME_SLOTS = [
    ('08:00-09:00', '08:00 - 09:00 AM'),
    ('09:00-10:00', '09:00 - 10:00 AM'),
    ('10:00-11:00', '10:00 - 11:00 AM'),
    ('11:00-12:00', '11:00 - 12:00 NOON'),
    ('12:00-13:00', '12:00 - 01:00 PM'),
    ('13:00-14:00', '01:00 - 02:00 PM'),
    ('14:00-14:30', 'LUNCH BREAK'),
    ('14:30-15:30', '02:30 - 03:30 PM'),
    ('15:30-16:30', '03:30 - 04:30 PM'),
    ('16:30-17:30', '04:30 - 05:30 PM'),
]

DAYS = [
    ('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'),
    ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'),
]

class TimetableEntry(models.Model):
    class_ref = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timetable_entries', null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    staff = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True)
    day = models.CharField(max_length=3, choices=DAYS)
    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS)
    # Raw data from Excel (before mapping)
    raw_subject_code = models.CharField(max_length=20, blank=True)
    raw_room_number = models.CharField(max_length=20, blank=True)
    raw_entry = models.CharField(max_length=50, blank=True)
    # Section/class label from Excel
    class_label = models.CharField(max_length=100, blank=True)
    has_conflict = models.BooleanField(default=False)
    conflict_detail = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['class_label', 'day', 'time_slot']
    
    def __str__(self):
        return f"{self.class_label} | {self.day} | {self.time_slot} | {self.raw_entry}"

class ConflictLog(models.Model):
    CONFLICT_TYPE = [
        ('room_double_booking', 'Room Double Booking'),
        ('staff_clash', 'Staff Clash'),
        ('invalid_format', 'Invalid Format'),
        ('unmapped_subject', 'Unmapped Subject'),
    ]
    conflict_type = models.CharField(max_length=30, choices=CONFLICT_TYPE)
    day = models.CharField(max_length=3, choices=DAYS, blank=True)
    time_slot = models.CharField(max_length=20, blank=True)
    detail = models.TextField()
    entry_1 = models.CharField(max_length=100, blank=True)
    entry_2 = models.CharField(max_length=100, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.conflict_type} - {self.day} {self.time_slot}"
