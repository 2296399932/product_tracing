from django.contrib import admin
from .models import Warning

@admin.register(Warning)
class WarningAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'is_resolved', 'created_at']
    list_filter = ['level', 'is_resolved']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'
    list_per_page = 20
