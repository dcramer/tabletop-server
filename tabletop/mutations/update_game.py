from typing import List

import graphene
from django.db import transaction

from tabletop.models import Collection, CollectionGame, Game
from tabletop.schema import GameNode


class UpdateGame(graphene.Mutation):
    class Arguments:
        game = graphene.UUID(required=True)
        collections = graphene.List(graphene.UUID, required=False)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    game = graphene.Field(GameNode)

    def mutate(self, info, game: str, collections: List[str] = None):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return UpdateGame(ok=False, errors=["Authentication required"])

        try:
            game = Game.objects.get(id=game)
        except Game.DoesNotExist:
            return UpdateGame(ok=False, errors=["Invalid Game"])

        if collections:
            collections = Collection.objects.filter(
                id__in=collections, created_by=current_user
            )

        with transaction.atomic():
            if collections is not None:
                for collection in collections:
                    CollectionGame.objects.get_or_create(
                        collection=collection, game=game
                    )
                CollectionGame.objects.filter(
                    game=game, collection__created_by=current_user
                ).exclude(collection__in=collections).delete()
        return UpdateGame(ok=True, game=game)
