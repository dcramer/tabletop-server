import graphene
from django.db import IntegrityError, transaction

from tabletop.models import Collection, CollectionGame, Game
from tabletop.schema import CollectionNode, GameNode


class AddGameToCollection(graphene.Mutation):
    class Arguments:
        collection = graphene.UUID(required=True)
        game = graphene.UUID(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    collection = graphene.Field(CollectionNode)
    game = graphene.Field(GameNode)

    def mutate(self, info, collection: str, game: str):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return AddGameToCollection(ok=False, errors=["Authentication required"])

        try:
            collection = Collection.objects.get(id=collection)
        except Collection.DoesNotExist:
            return AddGameToCollection(ok=False, errors=["Invalid Collection"])

        if collection.created_by_id != current_user.id:
            return AddGameToCollection(ok=False, errors=["Cannot edit this Collection"])

        try:
            game = Game.objects.get(id=game)
        except Game.DoesNotExist:
            return AddGameToCollection(ok=False, errors=["Invalid Game"])

        try:
            with transaction.atomic():
                CollectionGame.objects.create(collection=collection, game=game)
        except IntegrityError:
            return AddGameToCollection(
                ok=False, errors=["Game already exists in Collection"]
            )

        return AddGameToCollection(ok=True, collection=collection, game=game)
