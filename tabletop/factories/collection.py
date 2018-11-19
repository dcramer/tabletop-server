import factory

from .. import models
from .user import UserFactory


class CollectionFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    created_by = factory.SubFactory(UserFactory)
    is_default = False

    class Meta:
        model = models.Collection
