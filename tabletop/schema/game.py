from graphene_django.types import DjangoObjectType

from tabletop.models import Game


class GameNode(DjangoObjectType):
    class Meta:
        name = "Game"
        model = Game
