from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F
from django.http import FileResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from apps.models import Product, Category, User, Cart, Address
from .forms import UserRegisterModelForm, OrderCreateModelForm
from .models.product import Favourite, Order
from .tasks import send_to_email
from .utils import make_pdf


class CategoryMixin:
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductList(CategoryMixin, ListView):
    queryset = Product.objects.all()
    template_name = 'apps/product/product-list.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().filter(is_premium=False)
        if user.is_authenticated and user.is_pro:
            qs = super().get_queryset()

        tag_name = self.request.GET.get('tag')
        category_slug = self.request.GET.get('category')
        search_query = self.request.GET.get('search')

        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if tag_name:
            qs = qs.filter(tags__name=tag_name)
        if search_query:
            qs = qs.filter(title__icontains=search_query)

        return qs


class ProductDetailView(CategoryMixin, DetailView):
    queryset = Product.objects.all()
    template_name = 'apps/product/product-details.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        all_likes = product.likes.filter(is_liked=True).count()
        user_liked = product.likes.filter(user=self.request.user, is_liked=True).exists()

        context.update(
            all_likes=all_likes,
            user_has_liked=user_liked
        )
        return context


class SettingsUpdateView(CategoryMixin, LoginRequiredMixin, UpdateView):
    queryset = User.objects.all()
    template_name = 'apps/auth/settings.html'
    fields = 'first_name', 'last_name', 'email',
    success_url = reverse_lazy('settings_page')

    def get_object(self, queryset=None):
        return self.request.user


class RegisterCreateView(CreateView):
    template_name = 'apps/auth/register.html'
    form_class = UserRegisterModelForm
    success_url = reverse_lazy('product_list_page')

    def form_valid(self, form):
        form.save()
        send_to_email.delay(msg='Sizning akkauntingiz yaratildi!', email=form.data['email'])
        return super().form_valid(form)


class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('product_list_page')


class LikeView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, id=pk)
        favourite, created = Favourite.objects.get_or_create(user=request.user, product=product)

        favourite.is_liked = not favourite.is_liked
        favourite.save()

        return redirect('product_detail_page', pk=product.pk)


class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, id=pk)

        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect('shopping_cart_page')


class CartListView(LoginRequiredMixin, CategoryMixin, ListView):
    queryset = Cart.objects.all()
    template_name = 'apps/carts/shopping-cart.html'
    context_object_name = 'carts'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_user = self.request.user

        cart_total = Cart.objects.filter(user=cart_user, is_active=True).aggregate(
            total_sum=Sum(F('product__price') * (100 - F('product__discount')) / 100 * F('quantity')))['total_sum'] or 0
        context['total_sum'] = cart_total

        return context

    def post(self, request, *args, **kwargs):
        cart_user = self.request.user
        action = request.POST.get('action')
        cart_item = get_object_or_404(Cart, user=cart_user)

        if action == 'plus':
            cart_item.quantity += 1
        elif action == 'minus' and cart_item.quantity > 1:
            cart_item.quantity -= 1

        cart_item.save()
        return redirect('shopping_cart_page')


class CartDeleteView(LoginRequiredMixin, CategoryMixin, View):
    def get(self, request, pk):
        cart_item = get_object_or_404(Cart, product_id=pk)
        cart_item.delete()
        return redirect('shopping_cart_page')


class CheckoutListView(LoginRequiredMixin, CategoryMixin, ListView):
    queryset = Cart.objects.all()
    template_name = 'apps/carts/checkout.html'
    context_object_name = 'cart_items'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        qs = self.get_queryset()

        context.update(
            **qs.aggregate(
                sub_total=Sum(F('quantity') * F('product__discount') * (100 - F('product__discount')) / 100),
                sub_shipping_cost=Sum(F('product__shipping_cost')),
                all_total=Sum((F('quantity') * F('product__price') * (100 - F('product__discount')) / 100) + F(
                    'product__shipping_cost'))
            )
        )
        return context

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class OrderCreateView(LoginRequiredMixin, CategoryMixin, CreateView):
    model = Order
    template_name = 'apps/orders/order-list.html'
    form_class = OrderCreateModelForm
    success_url = reverse_lazy('order_list_page')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class OrderDetailView(LoginRequiredMixin, CategoryMixin, DetailView):
    queryset = Order.objects.all()
    template_name = 'apps/orders/order-details.html'
    context_object_name = 'order'

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        total_shipping_cost = \
        order.items.aggregate(total_shipping_cost=Sum(F('product__shipping_cost') * F('quantity')))[
            'total_shipping_cost']
        context['total_shipping_cost'] = total_shipping_cost
        return context


class OrderListView(LoginRequiredMixin, CategoryMixin, ListView):
    model = Order
    template_name = 'apps/orders/order-list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=self.request.user)


# address
class AddressCreateView(LoginRequiredMixin, CategoryMixin, CreateView):
    model = Address
    template_name = 'apps/auth/address_form.html'
    fields = ['full_name', 'street', 'zip_code', 'city', 'phone', 'user']
    success_url = reverse_lazy('checkout_page')


class AddressUpdateView(LoginRequiredMixin, CategoryMixin, UpdateView):
    model = Address
    template_name = 'apps/auth/address_form.html'
    fields = ['full_name', 'street', 'zip_code', 'city', 'phone', 'user']
    success_url = reverse_lazy('checkout_page')


class OrderPdfCreateView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)
        if not order.pdf_file:
            make_pdf(order)
        # return FileResponse(order.pdf_file.open(), as_attachment=True)
        return FileResponse(order.pdf_file, as_attachment=True)


class OrderDeleteView(LoginRequiredMixin, CategoryMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        order.delete()
        return redirect('order_list_page')
