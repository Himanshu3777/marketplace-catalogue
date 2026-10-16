# Security hardening: idempotency key (no duplicate orders) + payment
# verification fields (backend is the only source of truth for "paid").
# Tables are empty in all environments, so defaults are safe.
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='idempotency_key',
            field=models.CharField(db_index=True, default=uuid.uuid4,
                                   max_length=36, unique=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('FAILED', 'Failed'), ('REFUNDED', 'Refunded')], db_index=True, default='PENDING', max_length=10),
        ),
        migrations.AddField(
            model_name='order',
            name='gateway_order_id',
            field=models.CharField(blank=True, db_index=True, max_length=64),
        ),
        migrations.AddField(
            model_name='order',
            name='gateway_payment_id',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='order',
            name='gateway_signature',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
