"""Catalogue models: Category -> SubCategory -> Product -> ProductVariant.

All product data here is ORIGINAL/SYNTHETIC, generated for development.
It is designed to be replaceable with licensed product data later without
changing the schema.
"""
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, db_index=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, db_index=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories"
    )
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "name"], name="uniq_subcat_per_category"
            )
        ]
        indexes = [models.Index(fields=["category", "is_active"])]

    def __str__(self):
        return f"{self.category.name} / {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.category.slug}-{self.name}")
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, db_index=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    AVAILABILITY_CHOICES = [
        ("in_stock", "In Stock"),
        ("low_stock", "Low Stock"),
        ("out_of_stock", "Out of Stock"),
        ("preorder", "Pre-order"),
    ]

    # Unique identifiers (DB-enforced: no duplicate products/SKUs)
    product_id = models.CharField(max_length=32, unique=True, db_index=True)
    sku = models.CharField(max_length=64, unique=True, db_index=True)

    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=280, unique=True, db_index=True)
    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT, related_name="products"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.PROTECT, related_name="products"
    )
    seller = models.ForeignKey(
        "sellers.Seller", on_delete=models.PROTECT, related_name="products"
    )
    product_type = models.CharField(max_length=120, db_index=True)

    short_description = models.CharField(max_length=500)
    detailed_description = models.TextField()

    # Pricing (base; per-variant overrides live on ProductVariant)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    gst_pct = models.DecimalField(max_digits=5, decimal_places=2, default=18)

    # Aggregates (denormalized for fast listing; updated on review/variant change)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, db_index=True)
    review_count = models.PositiveIntegerField(default=0)
    availability_status = models.CharField(
        max_length=16, choices=AVAILABILITY_CHOICES, default="in_stock", db_index=True
    )

    warranty = models.CharField(max_length=255, blank=True)
    return_policy = models.CharField(max_length=255, blank=True)
    weight_kg = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    dimensions = models.CharField(max_length=120, blank=True)  # "LxWxH cm"
    material = models.CharField(max_length=120, blank=True, null=True)

    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0), name="product_price_non_negative"
            ),
            models.CheckConstraint(
                condition=models.Q(discount_pct__gte=0)
                & models.Q(discount_pct__lte=90),
                name="product_discount_range",
            ),
        ]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["subcategory", "is_active"]),
            models.Index(fields=["brand", "is_active"]),
            models.Index(fields=["seller", "is_active"]),
            models.Index(fields=["price"]),
            models.Index(fields=["-rating"]),
        ]

    def __str__(self):
        return f"{self.product_id} — {self.name}"

    @property
    def final_price(self):
        return round(float(self.price) * (1 - float(self.discount_pct) / 100), 2)


class ProductVariant(models.Model):
    variant_id = models.CharField(max_length=32, unique=True, db_index=True)
    sku = models.CharField(max_length=64, unique=True, db_index=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    # Variant axes — NULL where not applicable (never fake values)
    color = models.CharField(max_length=60, null=True, blank=True, db_index=True)
    size = models.CharField(max_length=60, null=True, blank=True, db_index=True)
    storage = models.CharField(max_length=60, null=True, blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0), name="variant_price_non_negative"
            ),
            models.UniqueConstraint(
                fields=["product", "color", "size", "storage"],
                name="uniq_variant_axes",
            ),
        ]
        indexes = [models.Index(fields=["product", "is_active"])]

    def __str__(self):
        axes = "/".join(a for a in [self.color, self.size, self.storage] if a)
        return f"{self.variant_id} ({axes or 'base'})"

    @property
    def final_price(self):
        return round(float(self.price) * (1 - float(self.discount_pct) / 100), 2)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images",
        null=True, blank=True,
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="images",
        null=True, blank=True,
    )
    url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=255, blank=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(product__isnull=False)
                    | models.Q(variant__isnull=False)
                ),
                name="image_needs_owner",
            )
        ]
        indexes = [
            models.Index(fields=["product", "position"]),
            models.Index(fields=["variant", "position"]),
        ]


class ProductSpecification(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="specifications"
    )
    name = models.CharField(max_length=120)
    value = models.CharField(max_length=500)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "name"], name="uniq_spec_per_product"
            )
        ]
        indexes = [models.Index(fields=["product"])]
