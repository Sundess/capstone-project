from datetime import datetime
from django.shortcuts import redirect, render, get_object_or_404
from .forms import ProductForm
from .models import Product, File, Review
from django.contrib.auth.decorators import login_required
from groq import Groq
from dotenv import load_dotenv
import pandas as pd
from collections import Counter
from textblob import TextBlob
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import csv
from io import TextIOWrapper
from django.contrib import messages


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
            sentiment = TextBlob(review.text).sentiment.polarity
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


# Define the required column names and order
REQUIRED_COLUMNS = [
    "id", "brand", "categories", "manufacturer", "name",
    "reviews.date", "reviews.dateAdded", "reviews.didPurchase",
    "reviews.doRecommend", "reviews.id", "reviews.rating",
    "reviews.text", "reviews.title", "reviews.username"
]


def upload_csv(request):
    if request.method == "POST":
        file = request.FILES.get('file')

        # Check if a file was uploaded
        if not file:
            messages.error(request, "No file selected. Please upload a file.")
            return render(request, 'pages/csv_input.html')

        # Check if the file is a CSV
        if not file.name.endswith('.csv'):
            messages.error(
                request, "Invalid file type. Please upload a CSV file.")
            return render(request, 'pages/csv_input.html')

        try:
            # Read and validate the CSV file
            file_wrapper = TextIOWrapper(file.file, encoding='utf-8')
            reader = csv.reader(file_wrapper)
            header = next(reader)  # Get the header row

            # Validate the header columns
            if header != REQUIRED_COLUMNS:
                messages.error(
                    request,
                    f"Invalid CSV format. Columns must be: {
                        ', '.join(REQUIRED_COLUMNS)}"
                )
                return render(request, 'pages/csv_input.html')

            # Save the file to the model
            obj = File.objects.create(file=file)

            # Call your custom function to process the file
            create_db(obj.file, request.user)
            messages.success(
                request, "File uploaded and processed successfully!")

        except Exception as e:
            # Handle unexpected errors gracefully
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'pages/csv_input.html')

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
    # Order reviews by review date descending
    reviews = product.reviews.all().order_by('-review_date')

    # Perform sentiment analysis on reviews
    for review in reviews:
        if review.rating < 3:
            review.sentiment = "Negative"
        else:
            sentiment_polarity = TextBlob(review.title).sentiment.polarity
            review.sentiment = (
                "Positive" if sentiment_polarity > 0.1 else
                "Negative" if sentiment_polarity < -0.1 else
                "Neutral"
            )

    # Calculate sentiment type counts
    sentiment_counts = Counter(review.sentiment for review in reviews)
    total_reviews = len(reviews)

    # Calculate sentiment percentages
    if total_reviews > 0:
        positive_percentage = (
            sentiment_counts['Positive'] / total_reviews) * 100
        negative_percentage = (
            sentiment_counts['Negative'] / total_reviews) * 100
        neutral_percentage = (
            sentiment_counts['Neutral'] / total_reviews) * 100
    else:
        positive_percentage = negative_percentage = neutral_percentage = 0

    # Pagination Part

    paginator = Paginator(reviews, 5)
    page = request.GET.get('page')

    try:
        # Convert page to an integer and check if it’s valid
        page = int(page)
        if page < 1:  # If page is less than 1, reset to the first page
            page = 1
        paginated_reviews = paginator.page(page)
    except (ValueError, TypeError):
        # Handle cases where page is not a number or is None
        paginated_reviews = paginator.page(1)
    except EmptyPage:
        # If the page number is too high, show the last page
        paginated_reviews = paginator.page(paginator.num_pages)

    context = {
        'product': product,
        'reviews': paginated_reviews,
        'positive_percentage': positive_percentage,
        'negative_percentage': negative_percentage,
        'neutral_percentage': neutral_percentage,
    }
    return render(request, 'pages/product_detail.html', context)
