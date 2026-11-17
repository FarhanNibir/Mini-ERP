
from django import forms

from apps.core.models import Branch
from .models import Warehouse


class WarehouseForm(forms.ModelForm):

    class Meta:
        model = Warehouse

        fields = [
            "branch",
            "code",
            "name",
            "address",
            "is_default",
            "is_active",
        ]

        widgets = {
            "branch": forms.Select(attrs={
                "class": "form-select",
            }),

            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter warehouse code",
            }),

            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter warehouse name",
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter warehouse address",
            }),

            "is_default": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["branch"].queryset = Branch.objects.filter(
            is_active=True
        ).select_related("company").order_by(
            "company__name", "name"
        )

from django import forms
from django.forms import inlineformset_factory

from apps.core.models import Branch, Company
from apps.catalog.models import Product

from .models import (
    Warehouse,
    StockMovement,
    StockMovementItem,
)


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "company",
            "movement_type",
            "movement_date",
            "source_warehouse",
            "destination_warehouse",
            "reference_no",
            "notes",
        ]

        widgets = {
            "company": forms.Select(attrs={"class": "form-select"}),
            "movement_type": forms.Select(attrs={"class": "form-select"}),
            "movement_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "source_warehouse": forms.Select(attrs={"class": "form-select"}),
            "destination_warehouse": forms.Select(attrs={"class": "form-select"}),
            "reference_no": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Optional reference"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["company"].queryset = Company.objects.filter(
            is_active=True
        ).order_by("name")

        self.fields["source_warehouse"].queryset = Warehouse.objects.filter(
            is_active=True
        ).select_related("branch", "branch__company").order_by("name")

        self.fields["destination_warehouse"].queryset = Warehouse.objects.filter(
            is_active=True
        ).select_related("branch", "branch__company").order_by("name")


class StockMovementItemForm(forms.ModelForm):
    class Meta:
        model = StockMovementItem
        fields = ["product", "quantity", "unit_cost"]

        widgets = {
            "product": forms.Select(attrs={"class": "form-select product-select"}),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.001",
                "min": "0.001",
            }),
            "unit_cost": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["product"].queryset = Product.objects.filter(
            is_active=True
        ).select_related("company").order_by("name")


StockMovementItemFormSet = inlineformset_factory(
    StockMovement,
    StockMovementItem,
    form=StockMovementItemForm,
    extra=1,
    can_delete=True,
)
