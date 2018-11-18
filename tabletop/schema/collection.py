from graphene_django.types import DjangoObjectType

from tabletop.models import Collection


class CollectionNode(DjangoObjectType):
    class Meta:
        name = "Collection"
        model = Collection
