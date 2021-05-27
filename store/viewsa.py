from django.shortcuts import render
from django.views import generic
from store.models import Product, Category
from django_filters.views import FilterView
from store.filters import ProductFilter
from cart.forms import CartForm
from django.db.models import Count


class CategoriesList(generic.ListView):
    template_name = 'store/categories_list.html'
    context_object_name = 'categories'
    queryset = Category.objects.all().annotate(num_products=Count('products'))
