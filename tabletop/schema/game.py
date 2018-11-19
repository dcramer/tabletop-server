import graphene
from graphene_django.types import DjangoObjectType

from tabletop.models import Collection, Game, GameImage

from .collection import CollectionNode


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
    collections = graphene.List(CollectionNode)

    class Meta:
        name = "Game"
        model = Game

    def resolve_collections(self, info):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return []
        if not hasattr(self, "collections"):
            return list(
                Collection.objects.filter(created_by=current_user, game=self.id)
            )
        # TODO(dcramer): need to confirm this is always pre-filtered
        return list(self.collections.all())
