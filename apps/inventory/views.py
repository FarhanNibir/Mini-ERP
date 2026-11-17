
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models.deletion import ProtectedError

from .models import Warehouse
from .forms import WarehouseForm
import uuid

from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

from .models import StockMovement, StockMovementItem
from .forms import StockMovementForm, StockMovementItemFormSet
from .services import post_stock_movement

from decimal import Decimal

from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce

from apps.core.models import Company
from apps.catalog.models import Product

from .models import StockLedger

def warehouse_list(request):
    search_query = request.GET.get("search", "").strip()

    warehouses = Warehouse.objects.select_related(
        "branch",
        "branch__company"
    ).order_by("branch__company__name", "name")

    if search_query:
        warehouses = warehouses.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(branch__name__icontains=search_query) |
            Q(branch__company__name__icontains=search_query)
        )

    context = {
        "warehouses": warehouses,
        "search_query": search_query,
        "total_warehouses": warehouses.count(),
    }

    return render(request, "inventory/warehouse_list.html", context)

def warehouse_create(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)

        if form.is_valid():
            warehouse = form.save()

            messages.success(
                request,
                f"Warehouse '{warehouse.name}' created successfully."
            )

            return redirect("inventory:warehouse_list")

    else:
        form = WarehouseForm()

    return render(request, "inventory/warehouse_form.html", {
        "form": form,
        "page_title": "Add Warehouse",
    })
def warehouse_edit(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)

    if request.method == "POST":
        form = WarehouseForm(request.POST, instance=warehouse)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Warehouse '{warehouse.name}' updated successfully."
            )
            return redirect("inventory:warehouse_list")
    else:
        form = WarehouseForm(instance=warehouse)

    return render(request, "inventory/warehouse_form.html", {
        "form": form,
        "page_title": "Edit Warehouse",
    })
@require_POST
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    warehouse_name = warehouse.name

    try:
        warehouse.delete()
        messages.success(
            request,
            f"Warehouse '{warehouse_name}' deleted successfully."
        )
    except ProtectedError:
        messages.error(
            request,
            f"Cannot delete '{warehouse_name}' because it is already used in stock movements."
        )

    return redirect("inventory:warehouse_list")

# =====================================================
# STOCK MOVEMENT LIST
# =====================================================

def stock_movement_list(request):
    search_query = request.GET.get("search", "").strip()
    movement_type = request.GET.get("type", "")
    status = request.GET.get("status", "")

    movements = StockMovement.objects.select_related(
        "company",
        "source_warehouse",
        "destination_warehouse",
    ).order_by("-movement_date", "-id")

    if search_query:
        movements = movements.filter(
            Q(movement_no__icontains=search_query) |
            Q(reference_no__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )

    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    if status:
        movements = movements.filter(status=status)

    context = {
        "movements": movements,
        "search_query": search_query,
        "selected_type": movement_type,
        "selected_status": status,
        "movement_types": StockMovement.MovementType.choices,
        "statuses": StockMovement.Status.choices,
        "total_movements": movements.count(),
    }

    return render(request, "inventory/stock_movement_list.html", context)


# =====================================================
# CREATE STOCK MOVEMENT
# =====================================================

@transaction.atomic
def stock_movement_create(request):
    if request.method == "POST":
        form = StockMovementForm(request.POST)

        if form.is_valid():
            movement = form.save(commit=False)

            movement.movement_no = (
                f"SM-{movement.movement_date:%Y%m%d}-"
                f"{uuid.uuid4().hex[:8].upper()}"
            )

            formset = StockMovementItemFormSet(
                request.POST,
                instance=movement,
                prefix="items",
            )

            if formset.is_valid():
                try:
                    movement.full_clean()
                    movement.save()
                    formset.save()

                    messages.success(
                        request,
                        f"Stock movement '{movement.movement_no}' created successfully."
                    )

                    return redirect("inventory:stock_movement_detail", pk=movement.pk)

                except ValidationError as error:
                    form.add_error(None, error)

        else:
            movement = form.instance
            formset = StockMovementItemFormSet(
                request.POST,
                instance=movement,
                prefix="items",
            )

    else:
        form = StockMovementForm()
        formset = StockMovementItemFormSet(prefix="items")

    return render(request, "inventory/stock_movement_form.html", {
        "form": form,
        "formset": formset,
        "page_title": "Create Stock Movement",
    })


# =====================================================
# EDIT DRAFT MOVEMENT
# =====================================================

@transaction.atomic
def stock_movement_edit(request, pk):
    movement = StockMovement.objects.select_for_update().get(pk=pk)

    if movement.status != StockMovement.Status.DRAFT:
        messages.error(request, "Only draft movements can be edited.")
        return redirect("inventory:stock_movement_detail", pk=pk)

    if request.method == "POST":
        form = StockMovementForm(request.POST, instance=movement)
        formset = StockMovementItemFormSet(
            request.POST,
            instance=movement,
            prefix="items",
        )

        if form.is_valid() and formset.is_valid():
            try:
                updated_movement = form.save(commit=False)
                updated_movement.full_clean()
                updated_movement.save()
                formset.save()

                messages.success(request, "Stock movement updated successfully.")
                return redirect("inventory:stock_movement_detail", pk=pk)

            except ValidationError as error:
                form.add_error(None, error)

    else:
        form = StockMovementForm(instance=movement)
        formset = StockMovementItemFormSet(
            instance=movement,
            prefix="items",
        )

    return render(request, "inventory/stock_movement_form.html", {
        "form": form,
        "formset": formset,
        "page_title": "Edit Stock Movement",
        "movement": movement,
    })


# =====================================================
# STOCK MOVEMENT DETAIL
# =====================================================

def stock_movement_detail(request, pk):
    movement = get_object_or_404(
        StockMovement.objects.select_related(
            "company",
            "source_warehouse",
            "destination_warehouse",
        ).prefetch_related("items__product"),
        pk=pk,
    )

    items = list(movement.items.all())
    total_cost = 0

    for item in items:
        item.line_total = item.quantity * item.unit_cost
        total_cost += item.line_total

    return render(request, "inventory/stock_movement_detail.html", {
        "movement": movement,
        "items": items,
        "total_cost": total_cost,
    })


# =====================================================
# POST STOCK MOVEMENT
# =====================================================

@require_POST
def stock_movement_post(request, pk):
    try:
        movement = post_stock_movement(pk)

        messages.success(
            request,
            f"Stock movement '{movement.movement_no}' posted successfully."
        )

    except (ValidationError, StockMovement.DoesNotExist) as error:
        messages.error(request, str(error))

    return redirect("inventory:stock_movement_detail", pk=pk)


# =====================================================
# DELETE DRAFT MOVEMENT
# =====================================================

@require_POST
def stock_movement_delete(request, pk):
    movement = get_object_or_404(StockMovement, pk=pk)

    if movement.status != StockMovement.Status.DRAFT:
        messages.error(request, "Only draft movements can be deleted.")
    else:
        movement_no = movement.movement_no
        movement.delete()

        messages.success(
            request,
            f"Stock movement '{movement_no}' deleted successfully."
        )

    return redirect("inventory:stock_movement_list")

# =====================================================
# STOCK BALANCE
# =====================================================

def stock_balance_list(request):
    company_id = request.GET.get("company", "")
    warehouse_id = request.GET.get("warehouse", "")
    product_id = request.GET.get("product", "")
    search_query = request.GET.get("search", "").strip()

    balances = (
        StockLedger.objects
        .values(
            "product_id",
            "product__sku",
            "product__name",
            "product__category__name",
            "product__unit__symbol",
            "warehouse_id",
            "warehouse__name",
            "warehouse__branch__company_id",
            "warehouse__branch__company__name",
        )
        .annotate(
            total_in=Coalesce(
                Sum("quantity", filter=Q(entry_type=StockLedger.EntryType.IN)),
                Value(Decimal("0.000")),
                output_field=DecimalField(max_digits=14, decimal_places=3),
            ),
            total_out=Coalesce(
                Sum("quantity", filter=Q(entry_type=StockLedger.EntryType.OUT)),
                Value(Decimal("0.000")),
                output_field=DecimalField(max_digits=14, decimal_places=3),
            ),
        )
        .order_by("product__name", "warehouse__name")
    )

    if company_id:
        balances = balances.filter(
            warehouse__branch__company_id=company_id
        )

    if warehouse_id:
        balances = balances.filter(warehouse_id=warehouse_id)

    if product_id:
        balances = balances.filter(product_id=product_id)

    if search_query:
        balances = balances.filter(
            Q(product__name__icontains=search_query) |
            Q(product__sku__icontains=search_query) |
            Q(warehouse__name__icontains=search_query)
        )

    balance_rows = []

    for row in balances:
        row["balance"] = row["total_in"] - row["total_out"]
        balance_rows.append(row)

    context = {
        "balances": balance_rows,
        "companies": Company.objects.filter(is_active=True).order_by("name"),
        "warehouses": Warehouse.objects.filter(is_active=True).order_by("name"),
        "products": Product.objects.filter(is_active=True).order_by("name"),
        "selected_company": company_id,
        "selected_warehouse": warehouse_id,
        "selected_product": product_id,
        "search_query": search_query,
        "total_records": len(balance_rows),
    }

    return render(request, "inventory/stock_balance_list.html", context)


# =====================================================
# STOCK LEDGER
# =====================================================

def stock_ledger_list(request):
    company_id = request.GET.get("company", "")
    warehouse_id = request.GET.get("warehouse", "")
    product_id = request.GET.get("product", "")
    entry_type = request.GET.get("entry_type", "")
    search_query = request.GET.get("search", "").strip()

    ledger_entries = (
        StockLedger.objects
        .select_related(
            "product",
            "product__unit",
            "warehouse",
            "warehouse__branch",
            "warehouse__branch__company",
            "movement_item",
            "movement_item__movement",
        )
        .order_by(
            "movement_item__movement__movement_date",
            "id",
        )
    )

    if company_id:
        ledger_entries = ledger_entries.filter(
            warehouse__branch__company_id=company_id
        )

    if warehouse_id:
        ledger_entries = ledger_entries.filter(
            warehouse_id=warehouse_id
        )

    if product_id:
        ledger_entries = ledger_entries.filter(
            product_id=product_id
        )

    if search_query:
        ledger_entries = ledger_entries.filter(
            Q(product__name__icontains=search_query) |
            Q(product__sku__icontains=search_query) |
            Q(warehouse__name__icontains=search_query) |
            Q(movement_item__movement__movement_no__icontains=search_query) |
            Q(movement_item__movement__reference_no__icontains=search_query)
        )

    # Calculate running balance before applying the entry type filter.
    # This ensures that IN/OUT filters do not produce incorrect balances.
    running_balances = {}
    displayed_entries = []

    for entry in ledger_entries:
        balance_key = (entry.product_id, entry.warehouse_id)

        current_balance = running_balances.get(
            balance_key,
            Decimal("0.000")
        )

        if entry.entry_type == StockLedger.EntryType.IN:
            current_balance += entry.quantity
        else:
            current_balance -= entry.quantity

        running_balances[balance_key] = current_balance
        entry.running_balance = current_balance

        if not entry_type or entry.entry_type == entry_type:
            displayed_entries.append(entry)

    # Show newest entries first, retaining their calculated balances.
    displayed_entries.reverse()

    context = {
        "ledger_entries": displayed_entries,
        "companies": Company.objects.filter(is_active=True).order_by("name"),
        "warehouses": Warehouse.objects.filter(is_active=True).order_by("name"),
        "products": Product.objects.filter(is_active=True).order_by("name"),
        "selected_company": company_id,
        "selected_warehouse": warehouse_id,
        "selected_product": product_id,
        "selected_entry_type": entry_type,
        "search_query": search_query,
        "entry_types": StockLedger.EntryType.choices,
        "total_entries": len(displayed_entries),
    }

    return render(request, "inventory/stock_ledger_list.html", context)
