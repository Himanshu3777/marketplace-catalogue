# Security hardening: price snapshot on cart items (detect price drift at checkout).
# Tables are empty in all environments (session carts), so a plain default is safe.
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='price_at_add',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
