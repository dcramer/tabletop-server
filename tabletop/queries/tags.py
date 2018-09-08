import graphene

from tabletop.models import Tag
from tabletop.schema import TagNode
from tabletop.utils.graphene import optimize_queryset


class Query(object):
    tags = graphene.List(TagNode, id=graphene.UUID(), query=graphene.String())

    def resolve_tags(self, info, id: str = None, query: str = None):
        qs = Tag.objects.all()
        if id:
            qs = qs.filter(id=id)
        if query:
            qs = qs.filter(name__istartswith=query)
        qs = optimize_queryset(qs, info, "tags")
        return qs.order_by("name")
