import graphene

from tabletop.models import Entity
from tabletop.schema import EntityNode
from tabletop.utils.graphene import optimize_queryset


class Query(object):
    entities = graphene.List(EntityNode, id=graphene.UUID(), query=graphene.String())

    def resolve_entities(self, info, id: str = None, query: str = None):
        qs = Entity.objects.all()
        if id:
            qs = qs.filter(id=id)
        if query:
            qs = qs.filter(name__istartswith=query)
        qs = optimize_queryset(qs, info, "entities")
        return qs.order_by("name")
