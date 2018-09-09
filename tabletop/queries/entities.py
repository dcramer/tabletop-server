import graphene

from tabletop.models import Entity, EntityType
from tabletop.schema import EntityNode, EntityTypeEnum
from tabletop.utils.graphene import optimize_queryset


class Query(object):
    entities = graphene.List(
        EntityNode,
        id=graphene.UUID(),
        query=graphene.String(),
        _type=graphene.Argument(EntityTypeEnum, name="type"),
    )

    def resolve_entities(
        self, info, id: str = None, query: str = None, _type: EntityType = None
    ):
        qs = Entity.objects.all()
        if id:
            qs = qs.filter(id=id)
        if query:
            qs = qs.filter(name__istartswith=query)
        if _type:
            qs = qs.filter(type=_type)
        qs = optimize_queryset(qs, info, "entities")
        return qs.order_by("name")
