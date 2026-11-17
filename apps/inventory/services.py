
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Sum

from .models import StockMovement, StockLedger, Warehouse


def get_stock_balance(product, warehouse):
    """
    Calculate available stock for a product in a warehouse.
    Balance = Total IN - Total OUT
    """

    ledger = StockLedger.objects.filter(
        product=product,
        warehouse=warehouse,
    ).aggregate(
        total_in=Sum(
            "quantity",
            filter=Q(entry_type=StockLedger.EntryType.IN),
        ),
        total_out=Sum(
            "quantity",
            filter=Q(entry_type=StockLedger.EntryType.OUT),
        ),
    )

    total_in = ledger["total_in"] or Decimal("0")
    total_out = ledger["total_out"] or Decimal("0")

    return total_in - total_out


@transaction.atomic
def post_stock_movement(movement_id):
    """
    Post a draft movement and generate stock ledger entries.
    """

    movement = (
        StockMovement.objects
        .select_for_update()
        .get(pk=movement_id)
    )

    if movement.status != StockMovement.Status.DRAFT:
        raise ValidationError("Only draft movements can be posted.")

    items = list(
        movement.items.select_related("product").all()
    )

    if not items:
        raise ValidationError("Cannot post a movement without products.")

    warehouse_ids = set()

    if movement.source_warehouse_id:
        warehouse_ids.add(movement.source_warehouse_id)

    if movement.destination_warehouse_id:
        warehouse_ids.add(movement.destination_warehouse_id)

    # Lock warehouses to serialize stock posting operations.
    locked_warehouses = list(
        Warehouse.objects.select_for_update()
        .filter(pk__in=warehouse_ids)
        .order_by("pk")
    )

    if len(locked_warehouses) != len(warehouse_ids):
        raise ValidationError("One or more warehouses could not be found.")

    for warehouse in locked_warehouses:
        if warehouse.branch.company_id != movement.company_id:
            raise ValidationError(
                "Warehouse does not belong to the movement company."
            )

        if not warehouse.is_active:
            raise ValidationError(
                f"Warehouse '{warehouse.name}' is inactive."
            )

    movement_type = movement.movement_type

    inbound_types = [
        StockMovement.MovementType.OPENING,
        StockMovement.MovementType.IN,
        StockMovement.MovementType.ADJUSTMENT_IN,
    ]

    outbound_types = [
        StockMovement.MovementType.OUT,
        StockMovement.MovementType.ADJUSTMENT_OUT,
    ]

    # Validate all products and quantities before creating ledger entries.
    for item in items:
        if item.product.company_id != movement.company_id:
            raise ValidationError(
                f"Product '{item.product.name}' belongs to another company."
            )

        if item.quantity <= 0:
            raise ValidationError("Product quantity must be greater than zero.")

        if movement_type in outbound_types or (
            movement_type == StockMovement.MovementType.TRANSFER
        ):
            source = movement.source_warehouse

            available = get_stock_balance(item.product, source)

            if available < item.quantity:
                raise ValidationError(
                    f"Insufficient stock for '{item.product.name}' "
                    f"in '{source.name}'. Available: {available}, "
                    f"Required: {item.quantity}."
                )

    # Generate ledger entries.
    for item in items:

        if movement_type in inbound_types:
            StockLedger.objects.create(
                movement_item=item,
                warehouse=movement.destination_warehouse,
                product=item.product,
                entry_type=StockLedger.EntryType.IN,
                quantity=item.quantity,
                unit_cost=item.unit_cost,
            )

        elif movement_type in outbound_types:
            StockLedger.objects.create(
                movement_item=item,
                warehouse=movement.source_warehouse,
                product=item.product,
                entry_type=StockLedger.EntryType.OUT,
                quantity=item.quantity,
                unit_cost=item.unit_cost,
            )

        elif movement_type == StockMovement.MovementType.TRANSFER:

            # Remove stock from source warehouse.
            StockLedger.objects.create(
                movement_item=item,
                warehouse=movement.source_warehouse,
                product=item.product,
                entry_type=StockLedger.EntryType.OUT,
                quantity=item.quantity,
                unit_cost=item.unit_cost,
            )

            # Add stock to destination warehouse.
            StockLedger.objects.create(
                movement_item=item,
                warehouse=movement.destination_warehouse,
                product=item.product,
                entry_type=StockLedger.EntryType.IN,
                quantity=item.quantity,
                unit_cost=item.unit_cost,
            )

    movement.status = StockMovement.Status.POSTED
    movement.save(update_fields=["status", "updated_at"])

    return movement
