from datetime import datetime
from django.shortcuts import redirect, render, get_object_or_404
from .forms import ProductForm
from .models import Product, File, Review
from django.contrib.auth.decorators import login_required
from groq import Groq
from dotenv import load_dotenv
import pandas as pd
from collections import Counter
from collections import Counter
from textblob import TextBlob
from django.shortcuts import render, get_object_or_404

import os
from textblob import TextBlob


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
    product = get_object_or_404(
        Product.objects.prefetch_related('reviews'), pk=pk)
    reviews = product.reviews.all()

    # Perform sentiment analysis based on both rating and review text
    for review in reviews:
        if review.rating < 3:
            # If rating is less than 3, set sentiment as Negative
            review.sentiment = "Negative"
        else:
            # Use TextBlob to analyze sentiment based on review text
            sentiment = TextBlob(review.title).sentiment.polarity
            if sentiment > 0.1:
                review.sentiment = "Positive"
            elif sentiment < -0.1:
                review.sentiment = "Negative"
            else:
                review.sentiment = "Neutral"

    return render(request, 'pages/product_detail.html', {'product': product, 'reviews': reviews})


def create_db(file_path, username):
    df = pd.read_csv(file_path, delimiter=',')
    df = df.dropna()
    list_of_csv = [list(row) for row in df.values]
    reviews_objects = []
    products_to_update = set()  # Track products for which we need to recalculate stats

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

            # Add product to the update set
            products_to_update.add(product_instance)

            # Create the review associated with the product
            review_instance = Review(
                product=product_instance,
                review_date=datetime.strptime(
                    entry[5], "%Y-%m-%dT%H:%M:%S.%fZ"),
                review_date_added=datetime.strptime(
                    entry[6], "%Y-%m-%dT%H:%M:%SZ"),
                did_purchase=entry[7],
                do_recommend=entry[8],
                review_id=entry[9],
                rating=entry[10],
                text=entry[11],
                title=entry[12],
                username=entry[13],
            )
            reviews_objects.append(review_instance)
            print(f"Review created for product: {product_instance.ref_id}")

        except Exception as e:
            print(f"An exception occurred: {e}")

    # Bulk create all review objects to minimize database hits
    Review.objects.bulk_create(reviews_objects)
    print(f"Successfully created {len(reviews_objects)} reviews.")

    # Calculate review stats for each unique product
    for product in products_to_update:
        product.calculate_review_stats()
        print(f"Updated review stats for product: {product.ref_id}")


def upload_csv(request):
    if request.method == "POST":
        file = request.FILES['file']
        obj = File.objects.create(file=file)
        create_db(obj.file, request.user)

    return render(request, 'pages/csv_input.html')


def product_edit(request, pk):
    # Fetch the product by its primary key (product_id)
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Save the product and update its details
            product = form.save()
            product.updated_by = request.user  # Optionally track the user who updated
            product.save()

            # Redirect to the product detail or list view after successful edit
            # Change this to the appropriate URL for your app
            return redirect('product_detail', pk=product.pk)
    else:
        # Prepopulate the form with the current product data
        form = ProductForm(instance=product)

    # Render the product form template with the form context
    return render(request, 'pages/product_form.html', {'form': form})


def product_detail_view(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related('reviews'), pk=pk)
    reviews = product.reviews.all()

    # Set sentiment for each review
    for review in reviews:
        if review.rating < 3:
            review.sentiment = "Negative"
        else:
            sentiment = TextBlob(review.title).sentiment.polarity
            if sentiment > 0.1:
                review.sentiment = "Positive"
            elif sentiment < -0.1:
                review.sentiment = "Negative"
            else:
                review.sentiment = "Neutral"

    # Count the sentiment types
    sentiment_counts = Counter(review.sentiment for review in reviews)
    total_reviews = len(reviews)

    # Calculate percentages if there are reviews
    if total_reviews > 0:
        positive_percentage = (sentiment_counts.get(
            'Positive', 0) / total_reviews) * 100
        negative_percentage = (sentiment_counts.get(
            'Negative', 0) / total_reviews) * 100
        neutral_percentage = (sentiment_counts.get(
            'Neutral', 0) / total_reviews) * 100
    else:
        positive_percentage = negative_percentage = neutral_percentage = 0

    context = {
        'product': product,
        'reviews': reviews,
        'positive_percentage': positive_percentage,
        'negative_percentage': negative_percentage,
        'neutral_percentage': neutral_percentage
    }
    return render(request, 'pages/product_detail.html', context)
