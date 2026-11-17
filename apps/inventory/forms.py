
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
