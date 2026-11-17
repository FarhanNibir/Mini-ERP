
from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    # Warehouses
    path("warehouses/", views.warehouse_list, name="warehouse_list"),
    path("warehouses/create/", views.warehouse_create, name="warehouse_create"),
    path("warehouses/<int:pk>/edit/", views.warehouse_edit, name="warehouse_edit"),
    path("warehouses/<int:pk>/delete/", views.warehouse_delete, name="warehouse_delete"),

    # Stock Movements
    path("stock-movements/", views.stock_movement_list, name="stock_movement_list"),
    path("stock-movements/create/", views.stock_movement_create, name="stock_movement_create"),
    path("stock-movements/<int:pk>/", views.stock_movement_detail, name="stock_movement_detail"),
    path("stock-movements/<int:pk>/edit/", views.stock_movement_edit, name="stock_movement_edit"),
    path("stock-movements/<int:pk>/post/", views.stock_movement_post, name="stock_movement_post"),
    path("stock-movements/<int:pk>/delete/", views.stock_movement_delete, name="stock_movement_delete"),

    path("stock-balances/", views.stock_balance_list, name="stock_balance_list"),
    path("stock-ledger/", views.stock_ledger_list, name="stock_ledger_list"),
]
