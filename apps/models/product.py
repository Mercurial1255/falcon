from django.db.models import CASCADE, ForeignKey, Model, CharField, ImageField, IntegerField, EmailField, TextField, \
    JSONField, ManyToManyField, PositiveIntegerField, BooleanField, TextChoices, PositiveSmallIntegerField
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from mptt.models import MPTTModel, TreeForeignKey

from apps.models.base import SlugBaseModel, CreatedBaseModel


class Category(SlugBaseModel, MPTTModel):
    parent = TreeForeignKey('self', CASCADE, related_name='children', null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Tag(SlugBaseModel):

    def __str__(self):
        return self.name


class Product(CreatedBaseModel):
    title = CharField(max_length=100)
    is_premium = BooleanField(default=False)
    price = IntegerField()
    discount = IntegerField(default=0)
    category = ForeignKey('apps.Category', CASCADE)
    shipping_cost = IntegerField(default=0)
    quantity = IntegerField(default=0)
    tags = ManyToManyField('apps.Tag', blank=True)
    specifications = JSONField(default=dict)
    short_description = CKEditor5Field('Short description', config_name='extends')
    description = CKEditor5Field('Long description', config_name='extends')

    def __str__(self):
        return self.title

    @property
    def discount_price(self):
        return self.price - self.price * self.discount // 100

    @property
    def is_available(self) -> object:
        return self.quantity > 0

    @property
    def is_new(self):
        return timezone.now() - self.created_at <= timezone.timedelta(days=7)

    @property
    def get_specifications(self):
        return list(self.specifications.values())[:5]


class ProductImage(Model):
    image = ImageField(upload_to='products/')
    product = ForeignKey('apps.Product', CASCADE, related_name='images')


class Review(CreatedBaseModel):
    product = ForeignKey('apps.Product', CASCADE, related_name='reviews')
    rating = IntegerField()
    name = CharField(max_length=255)
    email = EmailField()
    review = TextField()

    def __str__(self):
        return self.name


class Cart(Model):
    user = ForeignKey('apps.User', CASCADE)
    product = ForeignKey('apps.Product', CASCADE)
    quantity = PositiveIntegerField(default=1)
    is_active = BooleanField(default=True)

    @property
    def get_total_price(self):
        return self.product.discount_price * self.quantity


class Order(CreatedBaseModel):
    class Status(TextChoices):
        COMPLETED = 'completed', 'Completed'
        PROCESSING = 'processing', 'Processing'
        ON_HOLD = 'on_hold', 'On Hold'
        PENDING = 'pending', 'Pending'

    class PaymentMethod(TextChoices):
        PAYPAL = 'paypal', 'Paypal'
        CREDIT_CARD = 'credit_card', 'Credit Card'

    payment_method = CharField(max_length=25, choices=PaymentMethod.choices)
    address = ForeignKey('apps.Address', CASCADE)
    owner = ForeignKey('apps.User', CASCADE)
    status = CharField(max_length=50, choices=Status.choices)


class OrderItem(Model):
    product = ForeignKey('apps.Product', CASCADE)
    order = ForeignKey('apps.Order', CASCADE, related_name='items')
    quantity = PositiveSmallIntegerField(default=1, db_default=1)


class Favourite(CreatedBaseModel):
    user = ForeignKey('apps.User', CASCADE)
    product = ForeignKey('apps.Product', CASCADE, related_name='likes')
    is_liked = BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'product')
