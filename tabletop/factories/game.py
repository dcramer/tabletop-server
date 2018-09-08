import factory

from .. import models


class GameFactory(factory.django.DjangoModelFactory):
    publisher = factory.Iterator(models.Publisher.objects.all())

    class Meta:
        model = models.Game
