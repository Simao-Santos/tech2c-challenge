from django.contrib import admin
from .models import EmissionRecord

@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
    list_display = ("company", "year", "sector", "energy_consumption_mwh", "co2_emissions_tons")
    list_filter = ("year", "sector")
    search_fields = ("company",)
