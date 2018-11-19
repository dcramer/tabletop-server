import factory

from .. import models
from .user import UserFactory


class EntityFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    confirmed = True
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Entity
