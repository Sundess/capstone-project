from django.urls import path
from . import views

urlpatterns = [
    path("product_form/", views.product_form_view, name="product_form"),

]
