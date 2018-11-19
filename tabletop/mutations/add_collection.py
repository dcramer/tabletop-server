from typing import List

import graphene
from django.db import IntegrityError, transaction

from tabletop.models import Collection, CollectionGame, Game
from tabletop.schema import CollectionNode


class AddCollection(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=False)
        games = graphene.List(graphene.UUID, required=False)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    collection = graphene.Field(CollectionNode)

    def mutate(self, info, name: str, description: str = None, games: List[str] = None):
        if not info.context.user.is_authenticated:
            return AddCollection(ok=False, errors=["Authentication required"])

        if games:
            games = Game.objects.filter(id__in=games)

        try:
            with transaction.atomic():
                result = Collection.objects.create(
                    name=name, description=description, created_by=info.context.user
                )
                if games:
                    for game in games:
                        CollectionGame.objects.create(collection=result, game=game)

        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                return AddCollection(ok=False, errors=["Collection already exists."])
            raise

        return AddCollection(ok=True, collection=result)
