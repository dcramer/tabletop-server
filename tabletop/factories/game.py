import factory

from .. import models
from .user import UserFactory


class GameFactory(factory.django.DjangoModelFactory):
    confirmed = True
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Game
