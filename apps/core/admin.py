
from django.contrib import admin
from .models import Company, Branch, FinancialYear


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "code", "name", "phone", "email", "is_active"
    )
    search_fields = ("code", "name", "phone", "email")
    list_filter = ("is_active", "country")
    ordering = ("name",)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = (
        "code", "name", "company",
        "is_head_office", "is_active"
    )
    search_fields = ("code", "name", "company__name")
    list_filter = ("company", "is_head_office", "is_active")


@admin.register(FinancialYear)
class FinancialYearAdmin(admin.ModelAdmin):
    list_display = (
        "name", "company", "start_date",
        "end_date", "is_active", "is_closed"
    )
    search_fields = ("name", "company__name")
    list_filter = ("company", "is_active", "is_closed")
