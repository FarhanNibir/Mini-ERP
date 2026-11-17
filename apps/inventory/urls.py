from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("warehouses/", views.warehouse_list, name="warehouse_list"),
    path("warehouses/create/", views.warehouse_create, name="warehouse_create"),
    path("warehouses/<int:pk>/edit/", views.warehouse_edit, name="warehouse_edit"),
    path("warehouses/<int:pk>/delete/", views.warehouse_delete, name="warehouse_delete"),
]