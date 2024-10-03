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
    summary_text = summarize_text(request, review_text)
    print(summary_text)
    return render(request, 'pages/product_detail.html', {'product': product, 'summary': summary_text})


def create_db(file_path, username):
    df = pd.read_csv(file_path, delimiter=',')
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


review_text = """
I chose this dress for our family photos. This dress is very flattering and comfortable. 
It’s stretchy around the waist and arms. You don’t have to wear it off the shoulders. 
I was worried about this due to my job and the way that I work my arms are raised all day. 
I wear my sleeves on top of my shoulders. The skirt is very flowy and long enough to cover 
everything so you do not feel concerned when bending over.

The cost isn’t so bad for what you are getting. It has some sheerness to it but it’s still 
thick enough that if you didn’t want to wear a bra underneath you don’t have to.

I definitely think this has versatility. You can wear this to work or special events. 
Loved this dress!! I used it for my senior pictures and it was perfect!! It was true to size 
and held together well. It wasn’t super sheer that you would need extra undergarments. 
Overall a good dress!! This dress is lightweight, great quality for the price, and is not see-through at all.

I purchased this dress in three colors (apricot, brown, and khaki) as I wanted the perfect 
neutral shade for our family photos. The colors in the photos online compared to what came 
were a bit off, which is why I knocked this review down to 4 stars. The apricot color was 
off-white and less yellow than expected. The brown was more reddish than I anticipated, 
and the khaki was lighter than shown. Overall, the dress is great and worked perfectly, 
but the colors were a bit off. The material of this dress is perfect for a summer day, 
and the back is super cute. Would buy from this seller again.

This is a cute dress, but I felt that it was a little too short for me. For curvy women, 
the chest area is not flattering and lacks support. Above the knee length but not too short, I love this dress.
"""


def summarize_text(request, review_text):

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),

    )
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a summarization specialization AI. "
                        "I will provide you with reviews and their summaries. "
                        "Create a short summary as shown in the example. The summary should "
                        "highlight the good and bad aspects of the product, making it a short "
                        "paragraph of no more than 4 sentences. Start the sentence with 'Customer says '"
                    )
                },
                {
                    "role": "user",
                    "content": f"Reviews: {review_text}"
                }
            ],
            temperature=0.4,
            max_tokens=90,
            top_p=1,
        )
        summary = completion.choices[0].message.content
        # print(completion.choices[0].message.content)

        return summary
        # return render(request, 'dashboard.html')
    except Exception as e:
        return f"Error generating summary: {str(e)}"
