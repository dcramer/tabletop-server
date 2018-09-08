from graphene_django.types import DjangoObjectType

from tabletop.models import Player


class PlayerNode(DjangoObjectType):
    class Meta:
        model = Player
        name = "Player"
