from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.db.models.deletion import ProtectedError

from .models import Product, ProductCategory, Unit
from .forms import ProductForm, ProductCategoryForm, UnitForm

def product_list(request):
    search_query = request.GET.get("search", "").strip()

    products = Product.objects.select_related(
        "company",
        "category",
        "unit"
    ).order_by("name")

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(barcode__icontains=search_query)
        )

    context = {
        "products": products,
        "search_query": search_query,
        "total_products": products.count(),
    }

    return render(request, "catalog/product_list.html", context)


def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save()
            messages.success(
                request,
                f"Product '{product.name}' created successfully."
            )
            return redirect("catalog:product_list")
    else:
        form = ProductForm()

    return render(request, "catalog/product_form.html", {
        "form": form,
        "page_title": "Add Product",
    })

def product_edit(request, pk):
    product = Product.objects.get(pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Product '{product.name}' updated successfully."
            )
            return redirect("catalog:product_list")
    else:
        form = ProductForm(instance=product)

    return render(request, "catalog/product_form.html", {
        "form": form,
        "page_title": "Edit Product",
        "product": product,
    })
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product_name = product.name
        product.delete()

        messages.success(
            request,
            f"Product '{product_name}' deleted successfully."
        )

    return redirect("catalog:product_list")
# =====================================================
# PRODUCT CATEGORY
# =====================================================

def category_list(request):
    search_query = request.GET.get("search", "").strip()

    categories = ProductCategory.objects.select_related(
        "company"
    ).order_by("company__name", "name")

    if search_query:
        categories = categories.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )

    return render(request, "catalog/category_list.html", {
        "categories": categories,
        "search_query": search_query,
        "total_categories": categories.count(),
    })


def category_create(request):
    form = ProductCategoryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(
            request,
            f"Category '{category.name}' created successfully."
        )
        return redirect("catalog:category_list")

    return render(request, "catalog/category_form.html", {
        "form": form,
        "page_title": "Add Category",
    })


def category_edit(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    form = ProductCategoryForm(request.POST or None, instance=category)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            f"Category '{category.name}' updated successfully."
        )
        return redirect("catalog:category_list")

    return render(request, "catalog/category_form.html", {
        "form": form,
        "page_title": "Edit Category",
    })


@require_POST
def category_delete(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    name = category.name

    try:
        category.delete()
        messages.success(request, f"Category '{name}' deleted successfully.")
    except ProtectedError:
        messages.error(
            request,
            f"Cannot delete '{name}' because products are using this category."
        )

    return redirect("catalog:category_list")


# =====================================================
# UNITS
# =====================================================

def unit_list(request):
    search_query = request.GET.get("search", "").strip()

    units = Unit.objects.select_related(
        "company"
    ).order_by("company__name", "name")

    if search_query:
        units = units.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(symbol__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )

    return render(request, "catalog/unit_list.html", {
        "units": units,
        "search_query": search_query,
        "total_units": units.count(),
    })


def unit_create(request):
    form = UnitForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        unit = form.save()
        messages.success(
            request,
            f"Unit '{unit.name}' created successfully."
        )
        return redirect("catalog:unit_list")

    return render(request, "catalog/unit_form.html", {
        "form": form,
        "page_title": "Add Unit",
    })


def unit_edit(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    form = UnitForm(request.POST or None, instance=unit)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            f"Unit '{unit.name}' updated successfully."
        )
        return redirect("catalog:unit_list")

    return render(request, "catalog/unit_form.html", {
        "form": form,
        "page_title": "Edit Unit",
    })


@require_POST
def unit_delete(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    name = unit.name

    try:
        unit.delete()
        messages.success(request, f"Unit '{name}' deleted successfully.")
    except ProtectedError:
        messages.error(
            request,
            f"Cannot delete '{name}' because products are using this unit."
        )

    return redirect("catalog:unit_list")