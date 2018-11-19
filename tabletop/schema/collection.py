import graphene
from graphene_django.types import DjangoObjectType

from tabletop.models import Collection, CollectionGame


class CollectionNode(DjangoObjectType):
    num_games = graphene.Int(required=False)

    class Meta:
        name = "Collection"
        model = Collection

    def resolve_num_games(self, info):
        if not self.id:
            return 0
        if hasattr(self, "num_games"):
            return self.num_games
        return CollectionGame.objects.filter(collection=self.id).count()
