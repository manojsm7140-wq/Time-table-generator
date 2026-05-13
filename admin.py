from django.contrib import admin
from .models import TimetableEntry, ConflictLog

@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ('class_label', 'day', 'time_slot', 'raw_entry', 'has_conflict')
    list_filter = ('day', 'has_conflict')
    search_fields = ('class_label', 'raw_entry')

@admin.register(ConflictLog)
class ConflictLogAdmin(admin.ModelAdmin):
    list_display = ('conflict_type', 'day', 'time_slot', 'resolved', 'detected_at')
    list_filter = ('conflict_type', 'resolved')
