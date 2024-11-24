# import json
# # Import the models from the 'product' app
# from product.models import Product, Review


# def export_data_to_json():
#     """Export Product and Review data to a JSON file."""
#     products = Product.objects.prefetch_related(
#         'reviews').all()  # Ensure 'reviews' is the related_name in Product
#     data = []

#     for product in products:
#         product_data = {
#             "product_id": product.id,
#             "title": product.title,
#             "brand": product.brand,
#             "avg_rating": float(product.avg_rating),
#             "reviews_count": product.reviews_count,
#             "review_summary": product.review_summary,
#             "reviews": [
#                 {
#                     "review_id": review.id,
#                     "text": review.text,
#                     "rating": review.rating,
#                     "username": review.username,
#                     "did_purchase": review.did_purchase,
#                     "do_recommend": review.do_recommend,
#                 }
#                 # Ensure 'reviews' is the related_name in Review's ForeignKey
#                 for review in product.reviews.all()
#             ],
#         }
#         data.append(product_data)

#     # Save data to a JSON file
#     file_path = 'product_reviews.json'
#     with open(file_path, 'w') as json_file:
#         json.dump(data, json_file, indent=4)

#     print(f"Data successfully exported to {file_path}")
