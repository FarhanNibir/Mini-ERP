
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

from apps.core.models import Company


class ProductCategory(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="product_categories"
    )
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_category_code_per_company"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.company.code})"


class Unit(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="units"
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    decimal_places = models.PositiveSmallIntegerField(default=2)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_unit_code_per_company"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Product(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="products"
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name="products"
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="products"
    )

    sku = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    barcode = models.CharField(max_length=100, blank=True)

    purchase_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    selling_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "sku"],
                name="unique_product_sku_per_company"
            )
        ]

    def clean(self):
        super().clean()

        if self.company_id and self.category_id:
            if self.company_id != self.category.company_id:
                raise ValidationError({
                    "category": "Category must belong to the selected company."
                })

        if self.company_id and self.unit_id:
            if self.company_id != self.unit.company_id:
                raise ValidationError({
                    "unit": "Unit must belong to the selected company."
                })

    def __str__(self):
        return f"{self.sku} - {self.name}"
