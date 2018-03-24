from django.contrib import admin
from .models import *

# Register your models here.
class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1

class CarpoolAdmin(admin.ModelAdmin):
    inlines = [MembershipInline]
    fieldsets = [
        (None, {"fields": ["name", "desc", "active"]}),
        ("Locations", {"fields": ["loc_a", "loc_b"]})
    ]

admin.site.register(Carpool, CarpoolAdmin)
admin.site.register(Car)
