from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum


class Product(models.Model):
    title = models.CharField(max_length=100)
    ref_id = models.CharField(max_length=50, unique=True)
    brand = models.CharField(max_length=100)
    manufacture = models.CharField(max_length=100)
    categories = models.CharField(max_length=250)

    # Auto-calculated fields based on reviews
    rating_count = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    review_summary = models.CharField(max_length=250, null=True, blank=True)
    do_recommend_count = models.PositiveIntegerField(default=0)

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
        self.reviews_count = reviews.count()
        self.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        self.rating_count = reviews.aggregate(Count('rating'))['rating__count']
        self.do_recommend_count = reviews.filter(do_recommend=True).count()

        # Generate a review summary if needed (for now using the first review text)
        if reviews.exists():
            self.review_summary = reviews.first().text[:250]

        # Save changes
        self.save()


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    review_date = models.DateField()
    review_date_added = models.DateField()
    did_purchase = models.BooleanField()
    do_recommend = models.BooleanField()
    review_id = models.PositiveIntegerField()
    rating = models.PositiveIntegerField()
    source_url = models.URLField()
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
