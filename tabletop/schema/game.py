from graphene_django.types import DjangoObjectType

from tabletop.models import Game


class GameNode(DjangoObjectType):
    class Meta:
        name = "Game"
        model = Game

    def resolve_image(self, args):
        if not self.image:
            return None
        url = self.image.url
        if not url.startswith(("http:", "https:")):
            if not url.startswith("/"):
                url = "/" + url
            return args.context.build_absolute_uri(url)
        return self.image.url
