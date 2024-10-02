from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=100)
    rating_count = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2)

    reviews_count = models.PositiveIntegerField(default=0)
    reviews = models.TextField(null=True)

    quantity = models.PositiveIntegerField(default=0)
    review_summary = models.CharField(max_length=250, null=True)

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products")

    photo = models.ImageField(default='fallback.png',
                              upload_to='photo/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
