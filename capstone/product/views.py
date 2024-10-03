from datetime import datetime
from django.shortcuts import render, get_object_or_404
from .forms import ProductForm
from .models import Product, File, Review
from django.contrib.auth.decorators import login_required
from groq import Groq
from dotenv import load_dotenv
import pandas as pd
import os

# GROQ_API_KEY = os.getenv('GROQ_API_KEY ')
load_dotenv()  # take environment variables from .env.


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
            return render(request, 'pages/product_form.html', {'form': form, 'success_message': success_message})
        else:
            print("Form errors:", form.errors)  # Print form validation errors
            return render(request, 'pages/product_form.html', {'form': form})
    else:
        form = ProductForm()

    return render(request, 'pages/product_form.html', {'form': form})


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'pages/product_detail.html', {'product': product})


def create_db(file_path, username):
    df = pd.read_csv(file_path, delimiter=',')
    df = df.dropna()
    list_of_csv = [list(row) for row in df.values]
    reviews_objects = []
    print(file_path, username)

    for entry in list_of_csv:
        try:
            # Attempt to get the product by ref_id
            product_instance = Product.objects.filter(ref_id=entry[0]).first()

            # If the product does not exist, create it
            if not product_instance:
                product_instance = Product.objects.create(
                    ref_id=entry[0],
                    brand=entry[1],
                    categories=entry[2],
                    manufacture=entry[3],
                    title=entry[4],
                    created_by=username
                )
                print(f"Product created: {product_instance.ref_id}")
            else:
                print(f"Product found: {product_instance.ref_id}")

            # Create the review associated with the product
            review_instance = Review(
                product=product_instance,
                review_date=datetime.strptime(
                    entry[5], "%Y-%m-%dT%H:%M:%S.%fZ"),
                review_date_added=datetime.strptime(
                    entry[6], "%Y-%m-%dT%H:%M:%SZ"),

                did_purchase=entry[7],  # Adjust index
                do_recommend=entry[8],  # Adjust index
                review_id=entry[9],  # Adjust index
                rating=entry[10],  # Adjust index
                text=entry[11],  # Adjust index
                title=entry[12],  # Adjust index
                username=entry[13],  # Adjust index
            )
            reviews_objects.append(review_instance)
            print(f"Review created for product: {product_instance.ref_id}")

        except Exception as e:
            print(f"An exception occurred: {e}")

    # Bulk create all review objects to minimize database hits
    Review.objects.bulk_create(reviews_objects)
    print(f"Successfully created {len(reviews_objects)} reviews.")

    product_instance.calculate_review_stats()


def upload_csv(request):
    if request.method == "POST":
        file = request.FILES['file']
        obj = File.objects.create(file=file)
        create_db(obj.file, request.user)

    return render(request, 'pages/csv_input.html')
