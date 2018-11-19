from typing import List

import graphene
from django.db import transaction

from tabletop.models import Collection, CollectionGame, Game
from tabletop.schema import CollectionNode


class UpdateCollection(graphene.Mutation):
    class Arguments:
        collection = graphene.UUID(required=True)
        name = graphene.String(required=True)
        games = graphene.List(graphene.UUID, required=False)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    collection = graphene.Field(CollectionNode)

    def mutate(self, info, collection: str, name: str = None, games: List[str] = None):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return UpdateCollection(ok=False, errors=["Authentication required"])

        try:
            collection = Collection.objects.get(id=collection)
        except Collection.DoesNotExist:
            return UpdateCollection(ok=False, errors=["Invalid Collection"])

        if collection.created_by_id != current_user.id:
            return UpdateCollection(ok=False, errors=["Cannot edit this Collection"])

        if games:
            games = Game.objects.filter(id__in=games)

        with transaction.atomic():
            if games:
                for game in games:
                    CollectionGame.objects.get_or_create(
                        collection=collection, game=game
                    )
                CollectionGame.objects.filter(collection=collection).exclude(
                    game__in=games
                ).delete()

            fields = []
            if name and name != collection.name:
                collection.name = name
                fields.append("name")
            if fields:
                collection.save(update_fields=fields)
        return UpdateCollection(ok=True, collection=collection)
