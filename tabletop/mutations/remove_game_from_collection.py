import graphene

from tabletop.models import Collection, CollectionGame, Game
from tabletop.schema import CollectionNode, GameNode


class RemoveGameFromCollection(graphene.Mutation):
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
            return RemoveGameFromCollection(
                ok=False, errors=["Authentication required"]
            )

        try:
            collection = Collection.objects.get(id=collection)
        except Collection.DoesNotExist:
            return RemoveGameFromCollection(ok=False, errors=["Invalid Collection"])

        if collection.created_by_id != current_user.id:
            return RemoveGameFromCollection(
                ok=False, errors=["Cannot edit this Collection"]
            )

        try:
            game = Game.objects.get(id=game)
        except Game.DoesNotExist:
            return RemoveGameFromCollection(ok=False, errors=["Invalid Game"])

        affected = CollectionGame.objects.filter(
            collection=collection, game=game
        ).delete()
        if not affected:
            return RemoveGameFromCollection(
                ok=False, errors=["Game does not exist in Collection"]
            )

        return RemoveGameFromCollection(ok=True, collection=collection, game=game)
