from django.db import models


class ProductReview(models.Model):
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.CASCADE, related_name="product_reviews"
    )
    author_name = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(db_index=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name="review_rating_range",
            )
        ]
        indexes = [models.Index(fields=["product", "-created_at"])]

    def __str__(self):
        return f"{self.product.product_id} ★{self.rating} — {self.title[:40]}"
