import graphene

from tabletop.models import Collection
from tabletop.schema import CollectionNode
from tabletop.utils.graphene import optimize_queryset


def fix_collections_query(queryset, selected_fields, **kwargs):
    if "games.image" in selected_fields:
        queryset = queryset.prefetch_related("games__image")
    return queryset


class Query(object):
    collections = graphene.List(
        CollectionNode,
        id=graphene.UUID(),
        game=graphene.UUID(),
        query=graphene.String(),
        created_by=graphene.UUID(),
    )

    def resolve_collections(
        self,
        info,
        id: str = None,
        game: str = None,
        query: str = None,
        created_by: str = None,
    ):
        qs = Collection.objects.all()

        if not (id or created_by):
            return qs.none()

        if id:
            qs = qs.filter(id=id)

        if game:
            qs = qs.filter(games=game)

        if query:
            qs = qs.filter(name__istartswith=query)

        if created_by:
            qs = qs.filter(created_by=created_by)

        qs = qs.order_by("-created_at")

        qs = optimize_queryset(qs, info, "collections", fix_collections_query)

        return qs
