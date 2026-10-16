"""Scalable product filtering. All filters hit indexed columns."""
import django_filters
from django.db.models import Q

from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__slug", lookup_expr="iexact")
    subcategory = django_filters.CharFilter(field_name="subcategory__slug", lookup_expr="iexact")
    brand = django_filters.CharFilter(field_name="brand__slug", lookup_expr="iexact")
    seller = django_filters.CharFilter(field_name="seller__slug", lookup_expr="iexact")
    product_type = django_filters.CharFilter(lookup_expr="iexact")

    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_rating = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")
    min_discount = django_filters.NumberFilter(field_name="discount_pct", lookup_expr="gte")

    availability = django_filters.CharFilter(field_name="availability_status")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    # Variant axes (join to variants — indexed)
    color = django_filters.CharFilter(field_name="variants__color", lookup_expr="iexact")
    size = django_filters.CharFilter(field_name="variants__size", lookup_expr="iexact")

    is_featured = django_filters.BooleanFilter()

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(availability_status="in_stock") | Q(availability_status="low_stock")
            ).distinct()
        return queryset.filter(availability_status="out_of_stock").distinct()

    class Meta:
        model = Product
        fields = []
