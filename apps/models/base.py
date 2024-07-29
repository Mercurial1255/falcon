from django.db.models import Model, CharField, DateTimeField, SlugField
from django.utils.text import slugify


class CreatedBaseModel(Model):
    updated_at = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class SlugBaseModel(Model):
    name = CharField(max_length=100)
    slug = SlugField(max_length=255, unique=True, editable=False)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        while self.__class__.objects.filter(slug=self.slug).exists():
            self.slug += '-1'
        super().save(force_insert, force_update, using, update_fields)
