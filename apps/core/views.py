
from django.shortcuts import render

from apps.core.models import Company, Branch
from apps.catalog.models import Product
from apps.inventory.models import Warehouse, StockMovement


def dashboard(request):
    context = {
        "total_companies": Company.objects.count(),
        "total_branches": Branch.objects.count(),
        "total_products": Product.objects.count(),
        "total_warehouses": Warehouse.objects.count(),
        "total_stock_movements": StockMovement.objects.count(),
    }

    return render(request, "dashboard.html", context)
