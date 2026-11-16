
from django.db import models
from django.db.models import Q

from apps.core.models import Branch, TimeStampedModel
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from apps.core.models import Branch, Company, TimeStampedModel
from apps.catalog.models import Product

class Warehouse(TimeStampedModel):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="warehouses"
    )

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True)

    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["branch", "code"],
                name="unique_warehouse_code_per_branch"
            ),
            models.UniqueConstraint(
                fields=["branch"],
                condition=Q(is_default=True),
                name="unique_default_warehouse_per_branch"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.branch.code})"


class StockMovement(TimeStampedModel):

    class MovementType(models.TextChoices):
        OPENING = "OPENING", "Opening Stock"
        IN = "IN", "Stock In"
        OUT = "OUT", "Stock Out"
        TRANSFER = "TRANSFER", "Stock Transfer"
        ADJUSTMENT_IN = "ADJ_IN", "Adjustment In"
        ADJUSTMENT_OUT = "ADJ_OUT", "Adjustment Out"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        POSTED = "POSTED", "Posted"
        CANCELLED = "CANCELLED", "Cancelled"

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="stock_movements"
    )

    movement_no = models.CharField(max_length=50)
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices
    )
    movement_date = models.DateField()

    source_warehouse = models.ForeignKey(
        "Warehouse",
        on_delete=models.PROTECT,
        related_name="outgoing_movements",
        blank=True,
        null=True
    )

    destination_warehouse = models.ForeignKey(
        "Warehouse",
        on_delete=models.PROTECT,
        related_name="incoming_movements",
        blank=True,
        null=True
    )

    reference_no = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    class Meta:
        ordering = ["-movement_date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "movement_no"],
                name="unique_movement_no_per_company"
            )
        ]

    def clean(self):
        super().clean()

        inbound_types = [
            self.MovementType.OPENING,
            self.MovementType.IN,
            self.MovementType.ADJUSTMENT_IN,
        ]

        outbound_types = [
            self.MovementType.OUT,
            self.MovementType.ADJUSTMENT_OUT,
        ]

        if self.movement_type == self.MovementType.TRANSFER:
            if not self.source_warehouse or not self.destination_warehouse:
                raise ValidationError(
                    "A transfer requires both source and destination warehouses."
                )

            if self.source_warehouse_id == self.destination_warehouse_id:
                raise ValidationError(
                    "Source and destination warehouses must be different."
                )

        elif self.movement_type in inbound_types:
            if not self.destination_warehouse or self.source_warehouse:
                raise ValidationError(
                    "This transaction requires only a destination warehouse."
                )

        elif self.movement_type in outbound_types:
            if not self.source_warehouse or self.destination_warehouse:
                raise ValidationError(
                    "This transaction requires only a source warehouse."
                )

        warehouses = [
            self.source_warehouse,
            self.destination_warehouse,
        ]

        for warehouse in warehouses:
            if warehouse and warehouse.branch.company_id != self.company_id:
                raise ValidationError(
                    "Warehouse must belong to the selected company."
                )

    def __str__(self):
        return f"{self.movement_no} - {self.get_movement_type_display()}"


class StockMovementItem(TimeStampedModel):

    movement = models.ForeignKey(
        StockMovement,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_movement_items"
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        validators=[MinValueValidator(0.001)]
    )

    unit_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movement", "product"],
                name="unique_product_per_stock_movement"
            )
        ]

    def clean(self):
        super().clean()

        if self.movement_id and self.product_id:
            if self.movement.company_id != self.product.company_id:
                raise ValidationError(
                    "Product must belong to the same company as the movement."
                )

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class StockLedger(TimeStampedModel):

    class EntryType(models.TextChoices):
        IN = "IN", "Stock In"
        OUT = "OUT", "Stock Out"

    movement_item = models.ForeignKey(
        StockMovementItem,
        on_delete=models.PROTECT,
        related_name="ledger_entries"
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="stock_ledger_entries"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_ledger_entries"
    )

    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        validators=[MinValueValidator(0.001)]
    )

    unit_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    class Meta:
        ordering = ["created_at", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "movement_item",
                    "warehouse",
                    "entry_type",
                ],
                name="unique_stock_ledger_entry"
            )
        ]
        indexes = [
            models.Index(
                fields=["product", "warehouse"],
                name="idx_ledger_product_wh"
            ),
        ]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.warehouse.name} - "
            f"{self.entry_type}"
        )
