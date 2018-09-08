import factory

from .. import models


class PublisherFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Publisher
