
from django.contrib import admin
from .models import Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = (
        "code", "name", "branch",
        "is_default", "is_active"
    )
    search_fields = (
        "code", "name", "branch__name"
    )
    list_filter = (
        "branch__company", "branch", "is_default", "is_active"
    )
    list_select_related = ("branch", "branch__company")
    ordering = ("branch", "name")

from django.contrib import admin
from .models import (
    Warehouse,
    StockMovement,
    StockMovementItem,
)


class StockMovementItemInline(admin.TabularInline):
    model = StockMovementItem
    extra = 1
    autocomplete_fields = ("product",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "movement_no",
        "movement_type",
        "company",
        "movement_date",
        "status",
    )

    search_fields = (
        "movement_no",
        "reference_no",
        "company__name",
    )

    list_filter = (
        "company",
        "movement_type",
        "status",
        "movement_date",
    )

    date_hierarchy = "movement_date"

    inlines = [StockMovementItemInline]

    readonly_fields = ("created_at", "updated_at")

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != StockMovement.Status.DRAFT:
            return [
                field.name
                for field in self.model._meta.fields
            ]
        return self.readonly_fields


@admin.register(StockMovementItem)
class StockMovementItemAdmin(admin.ModelAdmin):
    list_display = (
        "movement",
        "product",
        "quantity",
        "unit_cost",
    )

    search_fields = (
        "movement__movement_no",
        "product__name",
        "product__sku",
    )
