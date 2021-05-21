from django.shortcuts import render
from django.views import generic
from store.models import Product, Category
from django_filters.views import FilterView
from store.filters import ProductFilter
from cart.forms import CartForm
from django.db.models import Count

# Create your views here.


class ProductList(FilterView):
    model = Product
    queryset = Product.objects.all()
    paginate_by = 20
    filterset_class = ProductFilter
    context_object_name = 'products'
    template_name = 'store/product_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        if 'category_slug' in self.kwargs:
            qs = qs.filter(category__slug=self.kwargs['category_slug'])
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProdcutDetails(generic.DetailView):
    model = Product
    template_name = 'store/product_details.html'
    context_object_name = 'product'

    def get_queryset(self):
        product = super().get_queryset()
        return product.select_related('category').annotate(
            total_purchases=Count('ordered'))


class CategoriesList(generic.ListView):
    template_name = 'store/categories_list.html'
    context_object_name = 'categories'
    queryset = Category.objects.all().annotate(num_products=Count('products'))
