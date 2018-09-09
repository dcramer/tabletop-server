from graphene_django.types import DjangoObjectType

from tabletop.models import Entity


class EntityNode(DjangoObjectType):
    class Meta:
        name = "Entity"
        model = Entity
