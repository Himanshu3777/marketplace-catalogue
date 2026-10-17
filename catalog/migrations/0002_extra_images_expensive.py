"""Add extra images (4th & 5th) to expensive products (₹5000+).

Products seeded before this change have 3 images. Expensive products
deserve a multi-angle view, so we add 2 more.
"""
from django.db import migrations


def add_extra_images(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    ProductImage = apps.get_model("catalog", "ProductImage")

    # Products with max variant price >= 5000 and fewer than 5 images
    expensive = Product.objects.filter(
        variants__price__gte=5000,
    ).distinct()
    to_create = []
    for p in expensive.iterator(chunk_size=500):
        existing = p.images.count()
        if existing >= 5:
            continue
        slug = p.slug[:40]
        for i in range(existing, 5):
            to_create.append(ProductImage(
                product=p,
                url=f"https://picsum.photos/seed/{slug}-{i}/600/600",
                position=i,
            ))
    ProductImage.objects.bulk_create(to_create, batch_size=500)


def remove_extra_images(apps, schema_editor):
    ProductImage = apps.get_model("catalog", "ProductImage")
    # Remove images at position 3 and 4 (the ones we added)
    ProductImage.objects.filter(position__gte=3).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_extra_images, remove_extra_images),
    ]
