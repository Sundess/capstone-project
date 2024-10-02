from django.urls import path
from . import views

urlpatterns = [
    path("product_form/", views.product_form_view, name="product_form"),
    path("product_csv_add/", views.upload_csv, name="product_csv_add"),
    path('product_detail/<int:pk>/',
         views.product_detail_view, name='product-detail'),
]
