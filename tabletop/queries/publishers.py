import graphene

from tabletop.models import Publisher
from tabletop.schema import PublisherNode
from tabletop.utils.graphene import optimize_queryset


class Query(object):
    publishers = graphene.List(
        PublisherNode, id=graphene.UUID(), query=graphene.String()
    )

    def resolve_publishers(self, info, id: str = None, query: str = None):
        qs = Publisher.objects.all()
        if id:
            qs = qs.filter(id=id)
        if query:
            qs = qs.filter(name__istartswith=query)
        qs = optimize_queryset(qs, info, "publishers")
        return qs.order_by("name")
