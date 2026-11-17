
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models.deletion import ProtectedError

from .models import Warehouse
from .forms import WarehouseForm


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