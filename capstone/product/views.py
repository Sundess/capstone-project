from django.shortcuts import render
from .forms import ProductForm
from django.contrib.auth.decorators import login_required


@login_required(login_url="login")
def product_form_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user  # Set the current user as the creator
            product.save()

            # Prepare a success message
            success_message = f'Product "{product.title}" added successfully!'

            # Reinitialize the form to clear the fields
            form = ProductForm()

            # Render the template with the success message and a new empty form
            return render(request, 'product_form.html', {'form': form, 'success_message': success_message})
        else:
            print("Form errors:", form.errors)  # Print form validation errors
            return render(request, 'product_form.html', {'form': form})
    else:
        form = ProductForm()

    return render(request, 'product_form.html', {'form': form})
