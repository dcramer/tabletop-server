import graphene
from django.db.models import Count, Q

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
        game=graphene.UUID(),
        created_by=graphene.UUID(),
    )

    def resolve_checkins(
        self,
        info,
        id: str = None,
        scope: str = None,
        game: str = None,
        created_by: str = None,
    ):
        current_user = info.context.user

        qs = Checkin.objects.all()

        if id:
            qs = qs.filter(id=id)

        if game:
            qs = qs.filter(game=game)

        if scope == "friends":
            if not current_user.is_authenticated:
                return qs.none()
            qs = qs.filter(
                Q(
                    players__in=Follower.objects.filter(
                        from_user=current_user.id
                    ).values("to_user")
                )
                | Q(players=current_user)
            ).distinct()
        # there's not yet privacy scope
        elif scope == "public":
            pass
        elif scope:
            raise NotImplementedError

        if created_by:
            qs = qs.filter(created_by=created_by)

        qs = qs.annotate(total_likes=Count("likes"), total_comments=Count("comments"))
        if current_user.is_authenticated:
            qs = qs.extra(
                select={
                    "is_liked": "select exists(select 1 from tabletop_like where user_id = %s and checkin_id = tabletop_checkin.id)"
                },
                select_params=[current_user.id],
            )

        qs = qs.order_by("-created_at")

        qs = optimize_queryset(qs, info, "checkins")

        return qs
