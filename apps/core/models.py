
from django.db import models
from django.db.models import Q


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Company(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    legal_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Bangladesh")

    tax_number = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=3, default="BDT")

    logo = models.ImageField(
        upload_to="companies/logos/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Branch(TimeStampedModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="branches"
    )

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=150)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    is_head_office = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_branch_code_per_company"
            ),
            models.UniqueConstraint(
                fields=["company"],
                condition=Q(is_head_office=True),
                name="unique_head_office_per_company"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.company.code})"


class FinancialYear(TimeStampedModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="financial_years"
    )

    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gte=models.F("start_date")),
                name="financial_year_valid_dates"
            ),
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_financial_year_per_company"
            ),
            models.UniqueConstraint(
                fields=["company"],
                condition=Q(is_active=True),
                name="unique_active_financial_year_per_company"
            ),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"
