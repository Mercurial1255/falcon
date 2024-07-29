from django.contrib.auth.models import AbstractUser
from django.db.models import OneToOneField, Model, PositiveSmallIntegerField, PositiveIntegerField, ForeignKey, CASCADE, \
    Sum, CharField, DateField, BooleanField

from apps.models import CreatedBaseModel


class User(AbstractUser):
    is_pro = BooleanField(default=False)

    @property
    def get_total_products(self):
        return self.cart_set.filter(is_active=True).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    @property
    def get_cart_count(self):
        return self.cart_set.count()


class CreditCard(CreatedBaseModel):
    owner = ForeignKey('apps.User', CASCADE)
    order = OneToOneField('apps.Order', CASCADE)
    number = CharField(max_length=16)
    cvv = CharField(max_length=3)
    expire_date = DateField()


class SiteSettings(Model):
    tax = PositiveSmallIntegerField()


class Address(CreatedBaseModel):
    full_name = CharField(max_length=255)
    street = CharField(max_length=255)
    zip_code = PositiveIntegerField()
    city = CharField(max_length=255)
    phone = CharField(max_length=255)
    user = ForeignKey('apps.User', CASCADE, related_name='addresses')

    def __str__(self):
        return self.full_name
