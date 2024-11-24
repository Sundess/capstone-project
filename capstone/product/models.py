import random
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum
import os
from groq import Groq


class Product(models.Model):
    title = models.CharField(max_length=100)
    ref_id = models.CharField(max_length=50)
    brand = models.CharField(max_length=100)
    manufacture = models.CharField(max_length=100)
    categories = models.CharField(max_length=250)

    # Auto-calculated fields based on reviews
    rating_count = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    review_summary = models.CharField(max_length=250, null=True, blank=True)
    do_recommend_count = models.PositiveIntegerField(default=0)

    # Fields to store the count of reviews by rating
    one_star_count = models.PositiveIntegerField(default=0)
    two_star_count = models.PositiveIntegerField(default=0)
    three_star_count = models.PositiveIntegerField(default=0)
    four_star_count = models.PositiveIntegerField(default=0)
    five_star_count = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products")

    photo = models.ImageField(default='fallback.png',
                              upload_to='photo/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def calculate_review_stats(self):
        """
        A method to calculate the total review count, average rating,
        review summary, and recommendation count based on associated reviews.
        """
        reviews = self.reviews.all()  # Get all reviews associated with this product
        print(reviews)
        self.reviews_count = reviews.count()
        self.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        self.rating_count = reviews.aggregate(Count('rating'))['rating__count']
        self.do_recommend_count = reviews.filter(do_recommend=True).count()

        # Calculate counts for each star rating
        self.one_star_count = reviews.filter(rating=1).count()
        self.two_star_count = reviews.filter(rating=2).count()
        self.three_star_count = reviews.filter(rating=3).count()
        self.four_star_count = reviews.filter(rating=4).count()
        self.five_star_count = reviews.filter(rating=5).count()

        # Generate a review summary if needed (for now using the first review text)
        if reviews.exists():
            review_text = self.get_reviews_for_summary()
            print(review_text)

            self.review_summary = summarize_text(review_text)
            print(self.review_summary)

        # Save changes
        self.save()

    def get_reviews_for_summary(self):
        try:
            # Fetch all reviews associated with the product
            all_reviews = self.reviews.all()

            # Check the total number of reviews
            total_reviews = all_reviews.count()

            if total_reviews < 10:
                # If fewer than 10 reviews exist, summarize all reviews
                review_texts = [review.text for review in all_reviews]
            else:
                # Otherwise, select 3 reviews from each rating (1, 2, 3, 4, 5)
                selected_reviews = []
                for rating in range(1, 6):
                    rating_reviews = list(all_reviews.filter(rating=rating))
                    if len(rating_reviews) == 0:
                        print(f"No reviews found for rating {rating}")
                    else:
                        # Randomly select up to 3 reviews for the current rating
                        selected_reviews.extend(random.sample(
                            rating_reviews, min(len(rating_reviews), 3)))

                # Check if we have fewer than 15 reviews, and if so, randomly select more
                if len(selected_reviews) < 15:
                    remaining_count = 15 - len(selected_reviews)
                    # Exclude already selected reviews from remaining selection
                    remaining_reviews = all_reviews.exclude(
                        id__in=[review.id for review in selected_reviews])
                    if remaining_reviews.exists():
                        selected_reviews.extend(random.sample(list(remaining_reviews), min(
                            remaining_count, remaining_reviews.count())))

                # Collect review texts from the selected reviews
                review_texts = [review.text for review in selected_reviews]

            # If no reviews were found at all, return a message
            if not review_texts:
                return "No reviews available for summarization."

            # Combine texts for summarization
            combined_reviews = " ".join(review_texts)

            # Return the combined reviews for summarization
            return combined_reviews

        except Exception as e:
            # Catch any unforeseen errors
            print(f"An error occurred while processing reviews: {e}")
            return "An error occurred during review processing."


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    review_date = models.DateField()
    review_date_added = models.DateField()
    did_purchase = models.BooleanField()
    do_recommend = models.BooleanField()
    review_id = models.PositiveIntegerField()
    rating = models.PositiveIntegerField()
    # source_url = models.URLField()
    text = models.TextField()
    title = models.CharField(max_length=200)
    username = models.CharField(max_length=100)

    def __str__(self):
        return f"Review by {self.username} for {self.product.title}"

    def save(self, *args, **kwargs):
        """
        Override the save method to update the related product's stats
        whenever a review is created or updated.
        """
        super().save(*args, **kwargs)
        self.product.calculate_review_stats()  # Recalculate product stats


class File(models.Model):
    file = models.FileField(upload_to="files")


def summarize_text(review_text):

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),

    )
    try:
        completion = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {
                    "role": "user",
                            "content": " You are a summarization specialization AI. I will provide you with reviews and their summaries. \nCreate a short summary as shown in the example. \nThe summary should highlight the good and bad aspects of the product, \nmaking it a short paragraph of no more than 4 sentences. \nStart the sentence with 'Customer says   "
                },
                {
                    "role": "assistant",
                    "content": "Okay"
                },
                {
                    "role": "user",
                    "content": "Generate summary for this\n\nThis gaming headset is fantastic! The sound quality is top-notch, delivering immersive audio with clear highs, deep bass, and precise surround sound, which is perfect for gaming. The microphone is crystal clear, making communication with teammates seamless. I also love the comfortable fit—the ear cushions are soft and breathable, and I can wear them for hours without any discomfort. The build quality feels solid and durable, and the design looks sleek and stylish. Whether for casual gamDing or intense competitive play, this headset has exceeded my expectations. Highly recommended for any gamer looking for great performance and comfort!\n\nI bought this headset for my son to use with his Xbox series X as he likes to play games with his friends. I like that they were very reasonably priced as he is very rough on items. So far they have worked well for him, he says he can hear his friends clearly and they can hear him clearly so the mic is good. They are also comfortable to wear and don’t hurt his ears. He also likes that there is a mute button on them so if I walk in to talk to him he can mute the mic real quick. Overall they are a good headset for playing online gaming.\n\nHad a headset just like this one that lasted me for years, but it was finally time to replace it. The cushions are thick, and great for long gaming sessions, volume is great, and the mic sounds good. Definitely a good headset for the price. It is a little bulky if that’s something that bothers you. Works well with my PC and Xbox. Please get yourself one if you’re in need!\n\nI got this in a rush when I needed a new headset. In hindsight a bit more research would have had me getting something else. As a precursor to the review I feel that it is worth noting that I am very rough on audio peripherals. I don't know why, but they usually last me about 6 months regardless of the quality and price. This is why I choose to buy at a cheaper price point more frequently rather than high-end less frequently.\n\nPros:\nPrice for the quality is great\nDecent speaker/mic sound\nGood quality cable that is at least 6' long\nSits comfortably on the head\nStereo/mic to separate stereo and mic connector included\nIn-line mic mute switch and audio volume adjustment\n\nMy son needed headphones for his school laptop and also uses them for his gaming. He really likes them the sound quality is great. The microphone works well. They are made well and seem to hold up for his daily uses. He loves the color too. Shipping was great they came rather quickly. Overall very happy with this purchase\n\nIt's nice looking - if you like things glowing. It fit very well - for the short time I got to use it. It seemed well made or at least as well made as other brands in this price category - I got mine on sale for $18. I purchased to use with my PC and it comes with a few ways to plug into the PC However...\n\nThe second I plugged this into my PC, it didn't work. I tried with both the plug, with and without the Y shaped plug piece AND the USB. I tried the plug in the front of as well as the back of my computer and I really wish I hadn't been so cheap when shopping for a headset! This headset has really messed up the sound on my computer! I can no longer hear videos when streaming. I couldn't get it to work with Discord and it completely screwed up sound when I play any games - some will work, some will not. I just don't understand what happened. I've tried doing self diagnostic and updating drivers but nothing helped. Now I'm left with a PC that has sound issues and no idea on how to fix it. My sound worked fine and then it didn't and the only thing that happened in between was this headset. Yes, I read the instructions. Little good that did. Hopefully you will have better luck but, I wouldn't chance it.\n\nThis was my main headset that I purchased in the middle of December. Right out of the box I plugged everything in and had an annoying echo in Discord. Whenever anything would come through my headset it would be played back to my friends in Discord. After troubleshooting for about an hour it just stopped on it's own. Chalked it up to a mild annoyance and carried on.\n\nOnly two months into owning this product the right headphone is almost non existent as far as producing sound. I untangled the chord and was able to have normal sound for only a couple of more weeks until it stopped working all together. I am going to spend a little more and buy a wireless headset. If you're looking for something that will only last you for a couple of months then this is fine but I had two major issues with this product in only three months time.\n\nUpdate 3/27 - Found out my issue is with the volume adjuster and mic mute module that basically splits the headphone from the top to the bottom of the chord. If I physically push the volume wheel into the module the connection briefly comes back in my right earphone. Unacceptable for the wiring and device to physically break like this without any physical damage or dropping of the product. Even for a cheaper alternative like this product it should not just wear down, tangle, and break as easily as this does. Spend a little extra money and get something that won't fall apart after only 2-3 months of use."
                },
                {
                    "role": "assistant",
                    "content": "Customers like the sound quality, headset quality, and value for money of the headphones. They mention they can hear their friends well, are comfortable to wear, and well worth the price. Some are also happy with the comfort and looks. However, some customers have different opinions on functionality, build quality, and mic functionality."
                },
                {
                    "role": "user",
                    "content": f"Now generate review summary for this: {review_text}"
                }
            ],
            temperature=0.8,
            max_tokens=600,
            top_p=1,
            stream=False,
            stop=None,
        )
        summary = completion.choices[0].message.content
        # print(completion.choices[0].message.content)

        return summary
        # return render(request, 'dashboard.html')
    except Exception as e:
        return f"Error generating summary: {str(e)}"
