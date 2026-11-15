
from django.contrib import admin
from .models import ProductCategory, Unit, Product


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "code", "name", "company", "is_active"
    )
    search_fields = (
        "code", "name", "company__name"
    )
    list_filter = ("company", "is_active")
    ordering = ("company", "name")
    list_select_related = ("company",)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = (
        "code", "name", "symbol",
        "company", "decimal_places", "is_active"
    )
    search_fields = (
        "code", "name", "symbol", "company__name"
    )
    list_filter = ("company", "is_active")
    ordering = ("company", "name")
    list_select_related = ("company",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "sku", "name", "company",
        "category", "unit", "selling_price", "is_active"
    )
    search_fields = (
        "sku", "name", "barcode", "company__name"
    )
    list_filter = (
        "company", "category", "is_active"
    )
    ordering = ("company", "name")
    list_select_related = (
        "company", "category", "unit"
    )
