import graphene

from tabletop.models import Like
from tabletop.schema import LikeNode
from tabletop.utils.graphene import optimize_queryset


class Query(object):
    likes = graphene.List(
        LikeNode,
        id=graphene.UUID(),
        checkin=graphene.UUID(),
        created_by=graphene.UUID(),
    )

    def resolve_likes(
        self, info, id: str = None, checkin: str = None, created_by: str = None
    ):
        qs = Like.objects.all()

        if not (id or checkin or created_by):
            return qs.none()

        if id:
            qs = qs.filter(id=id)

        if checkin:
            qs = qs.filter(checkin=checkin)

        if created_by:
            qs = qs.filter(created_by=created_by)

        qs = qs.order_by("-created_at")

        qs = optimize_queryset(qs, info, "likes")

        return qs
