from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products")
    # rating_count = models.IntegerField()
    # reviews = models.TextField()
    # reviews_count = models.IntegerField()
    # review_summary = models.CharField(max_length=250, null=True)

    def __str__(self):
        return self.title
