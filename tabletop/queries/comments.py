import graphene

from tabletop.models import Comment
from tabletop.schema import CommentNode
from tabletop.utils.graphene import optimize_queryset


class Query(object):
    comments = graphene.List(
        CommentNode,
        id=graphene.UUID(),
        checkin=graphene.UUID(),
        created_by=graphene.UUID(),
    )

    def resolve_comments(
        self, info, id: str = None, checkin: str = None, created_by: str = None
    ):
        qs = Comment.objects.all()

        if not (id or checkin or created_by):
            return qs.none()

        if id:
            qs = qs.filter(id=id)

        if checkin:
            qs = qs.filter(checkin=checkin)

        if created_by:
            qs = qs.filter(created_by=created_by)

        qs = qs.order_by("-created_at")

        qs = optimize_queryset(qs, info, "comments")

        return qs
