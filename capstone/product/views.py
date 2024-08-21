from django.shortcuts import render

# Create your views here.


def product_form_view(request):
    return render(request, 'product_form.html')
