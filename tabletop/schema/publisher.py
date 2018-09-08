from graphene_django.types import DjangoObjectType

from tabletop.models import Publisher


class PublisherNode(DjangoObjectType):
    class Meta:
        name = "Publisher"
        model = Publisher
