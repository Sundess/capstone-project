# Replace with your actual model import
from ..product.models import Product, Review


def product_text():
    products = Product.objects.all()  # Get all products
    review_texts = []

    for product in products:
        # Get reviews for each product
        reviews = Review.objects.filter(product=product)
        for review in reviews:
            review_texts.append(review.text)

    return review_texts
# import os
# import json
# from groq import Groq
# from langchain.llms import OpenAI
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.text_splitter import CharacterTextSplitter

# # Initialize Groq client
# client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# # Define a function to split large documents into smaller chunks


# def split_documents(documents, chunk_size=1000):
#     """Split large documents into smaller chunks using LangChain."""
#     splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=200)
#     return splitter.split_documents(documents)

# # Define a function to summarize large documents if necessary


# def summarize_documents(documents):
#     """Summarize large documents using a custom summarization chain."""
#     # Create a simple summarization prompt
#     prompt_template = """Summarize the following text in a concise manner:
#     {text}"""
#     prompt = PromptTemplate(input_variables=["text"], template=prompt_template)

#     # Initialize OpenAI LLM and summarization chain
#     llm = OpenAI(temperature=0.7)
#     summarizer = LLMChain(llm=llm, prompt=prompt)

#     summarized_docs = []
#     for doc in documents:
#         # Summarizing the content of each document
#         summarized_text = summarizer.run(doc['content'])
#         summarized_docs.append(summarized_text)

#     return summarized_docs

# # Function to export data to JSON (as in the previous implementation)


# def export_data_to_json(file_path, product_id=794):
#     from product.models import Product  # Adjusted for product app structure
#     if product_id:
#         products = Product.objects.prefetch_related(
#             'reviews').filter(id=product_id)
#     else:
#         products = Product.objects.prefetch_related('reviews').all()

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
#                 {"review_id": review.id,
#                     "text": review.text[:150], "rating": review.rating}
#                 for review in product.reviews.all()
#             ],
#         }
#         data.append(product_data)

#     with open(file_path, 'w') as json_file:
#         json.dump(data, json_file, indent=4)

#     print(f"Data successfully exported to {file_path}")

# # Function to load JSON data into documents


# def load_json_to_documents(file_path):
#     if not os.path.exists(file_path):
#         print(f"File not found: {file_path}. Generating JSON data...")
#         export_data_to_json(file_path)

#     with open(file_path, 'r') as file:
#         data = json.load(file)

#     documents = []
#     for product in data:
#         product_info = f"""
#         Product: {product['title']}
#         Brand: {product['brand']}
#         Average Rating: {product['avg_rating']}
#         Reviews Count: {product['reviews_count']}
#         Summary: {product['review_summary']}
#         """
#         for review in product['reviews']:
#             documents.append({
#                 "content": f"{product_info} Review: {review['text']}",
#                 "meta": {"product_id": product['product_id'], "review_id": review['review_id'], "rating": review['rating']}
#             })
#     return documents

# # LangChain integration for handling large document queries


# def chat_with_rag_using_langchain(query, documents):
#     """Query Groq's LLM for RAG-based answers using LangChain."""
#     # Split documents into smaller chunks if they are too large
#     split_docs = split_documents(documents)

#     # Optional: Summarize the documents if they're still too large
#     summarized_docs = summarize_documents(split_docs)

#     # Format documents for Groq's RAG model
#     formatted_docs = [{"content": doc, "metadata": doc["meta"]}
#                       for doc in summarized_docs]

#     # Use Groq's completion endpoint with RAG
#     response = client.chat.completions.create(
#         model="gemma2-9b-it",
#         messages=[
#             {"role": "system", "content": "You are an expert product assistant. Answer user queries based on provided reviews and product data."},
#             {"role": "user", "content": f"Here's the context: {
#                 formatted_docs}. Now, answer this: {query}"}
#         ],
#         temperature=0.7,
#         max_tokens=600
#     )

#     return response["choices"][0]["message"]["content"]

# # Main function


# def main():
#     json_file_path = 'product_reviews.json'

#     documents = load_json_to_documents(json_file_path)

#     query = "Which product has the highest rating and is good for gaming?"
#     answer = chat_with_rag_using_langchain(query, documents)
#     print(f"Answer: {answer}")


# if __name__ == "__main__":
#     main()
