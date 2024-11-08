from django.urls import path
from . import views

urlpatterns = [
    path("product_form/", views.product_form_view, name="product_form"),
    path("upload_csv/", views.upload_csv, name="upload_csv"),
    path('product_detail/<int:pk>/', views.product_detail_view, name='product-detail'),
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'),  # Add this line for product edit
]
