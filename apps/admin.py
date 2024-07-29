from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from apps.models import Product, ProductImage, Review, Category, Tag, User, CreditCard, Order
import csv

from apps.models import Address


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    min = 1
    max = 3


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    min = 1
    max = 3


class CreditCardInline(admin.TabularInline):
    model = CreditCard
    extra = 1
    min = 1
    max = 3


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = AddressInline,


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = CreditCardInline,


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]


@admin.register(Tag)
class TagModelAdmin(admin.ModelAdmin):
    pass


@admin.register(CreditCard)
class CreditCardModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass
