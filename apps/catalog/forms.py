
from django import forms
from .models import Product, ProductCategory, Unit
from apps.core.models import Company


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            "company",
            "category",
            "unit",
            "sku",
            "name",
            "description",
            "barcode",
            "purchase_price",
            "selling_price",
            "image",
            "is_active",
        ]

        widgets = {
            "company": forms.Select(attrs={
                "class": "form-select"
            }),
            "category": forms.Select(attrs={
                "class": "form-select"
            }),
            "unit": forms.Select(attrs={
                "class": "form-select"
            }),
            "sku": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter product SKU"
            }),
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter product name"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
            "barcode": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter barcode"
            }),
            "purchase_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0"
            }),
            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["company"].queryset = Company.objects.filter(
            is_active=True
        )

        self.fields["category"].queryset = ProductCategory.objects.filter(
            is_active=True
        )

        self.fields["unit"].queryset = Unit.objects.filter(
            is_active=True
        )
from django import forms
from apps.core.models import Company
from .models import ProductCategory, Unit


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ["company", "code", "name", "description", "is_active"]
        widgets = {
            "company": forms.Select(attrs={"class": "form-select"}),
            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter category code",
            }),
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter category name",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter description",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].queryset = Company.objects.filter(
            is_active=True
        ).order_by("name")


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = [
            "company", "code", "name", "symbol",
            "decimal_places", "is_active",
        ]
        widgets = {
            "company": forms.Select(attrs={"class": "form-select"}),
            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. PCS",
            }),
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Pieces",
            }),
            "symbol": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. pcs",
            }),
            "decimal_places": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "max": 3,
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].queryset = Company.objects.filter(
            is_active=True
        ).order_by("name")