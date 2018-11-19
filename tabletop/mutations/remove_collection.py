import graphene
from django.db import transaction

from tabletop.models import Collection


class RemoveCollection(graphene.Mutation):
    class Arguments:
        collection = graphene.UUID(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, collection: str):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return RemoveCollection(ok=False, errors=["Authentication required"])

        try:
            collection = Collection.objects.get(id=collection)
        except Collection.DoesNotExist:
            return RemoveCollection(ok=False, errors=["Invalid Collection"])

        if collection.is_default:
            return RemoveCollection(
                ok=False, errors=["Cannot remove your default Collection"]
            )

        if collection.created_by_id != current_user.id:
            return RemoveCollection(ok=False, errors=["Cannot remove this Collection"])

        with transaction.atomic():
            collection.delete()

        return RemoveCollection(ok=True)
