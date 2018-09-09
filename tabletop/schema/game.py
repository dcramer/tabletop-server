import graphene
from graphene_django.types import DjangoObjectType

from tabletop.models import Game, GameImage


class GameImageNode(DjangoObjectType):
    url = graphene.String()

    class Meta:
        name = "GameImage"
        model = GameImage
        only_fields = ("width", "height")

    def resolve_url(self, args):
        if not self.file:
            return None
        url = self.file.url
        if not url.startswith(("http:", "https:")):
            if not url.startswith("/"):
                url = "/" + url
            url = args.context.build_absolute_uri(url)
        return url


class GameNode(DjangoObjectType):
    image = GameImageNode()

    class Meta:
        name = "Game"
        model = Game
