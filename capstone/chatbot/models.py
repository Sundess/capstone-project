import os
import json
from product.models import Product


def export_data_to_json(file_path='product_reviews.json'):
    # Check if the file already exists
    if not os.path.exists(file_path):
        print(f"{file_path} does not exist. Creating the file...")

        # Query the database for all products and their reviews
        products = Product.objects.prefetch_related('reviews').all()

        data = []
        for product in products:
            product_data = {
                "product_id": product.id,
                "title": product.title,
                "brand": product.brand,
                "avg_rating": float(product.avg_rating),
                "reviews_count": product.reviews_count,
                "review_summary": product.review_summary,
                "reviews": [
                    {"review_id": review.id,
                     # Limiting review text to first 150 characters
                     "text": review.text[:150],
                     "rating": review.rating}
                    for review in product.reviews.all()
                ],
            }
            data.append(product_data)

        # Create and write to the JSON file
        try:
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Data successfully exported to {file_path}")
        except Exception as e:
            print(f"Error writing to file: {e}")
    else:
        print(f"{file_path} already exists.")
