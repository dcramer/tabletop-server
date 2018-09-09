import graphene
from django.db.models import Q

from tabletop.models import Checkin, Follower
from tabletop.schema import CheckinNode
from tabletop.utils.graphene import optimize_queryset


class CheckinScope(graphene.Enum):
    class Meta:
        name = "CheckinScope"

    public = "public"
    friends = "friends"


class Query(object):
    checkins = graphene.List(
        CheckinNode,
        id=graphene.UUID(),
        scope=graphene.Argument(CheckinScope),
        created_by=graphene.UUID(),
    )

    def resolve_checkins(
        self, info, id: str = None, scope: str = None, created_by: str = None
    ):
        user = info.context.user

        qs = Checkin.objects.all()

        if id:
            qs = qs.filter(id=id)

        if scope == "friends":
            if not user.is_authenticated:
                return qs.none()
            qs = qs.filter(
                Q(
                    players__in=Follower.objects.filter(from_user=user.id).values(
                        "to_user"
                    )
                )
                | Q(players=user)
            ).distinct()
        # there's not yet privacy scope
        elif scope == "public":
            pass
        elif scope:
            raise NotImplementedError

        if created_by:
            qs = qs.filter(created_by=created_by)

        qs = qs.order_by("-created_at")

        qs = optimize_queryset(qs, info, "checkins")

        return qs