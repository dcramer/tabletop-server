import graphene

from tabletop.models import Follower, User
from tabletop.schema import UserNode
from tabletop.utils.graphene import optimize_queryset


class UserScope(graphene.Enum):
    class Meta:
        name = "UserScope"

    followers = "followers"
    following = "following"


class Query(object):
    users = graphene.List(
        UserNode,
        id=graphene.UUID(),
        query=graphene.String(),
        scope=graphene.Argument(UserScope),
        include_self=graphene.Boolean(),
    )

    def resolve_users(
        self,
        info,
        id: str = None,
        query: str = None,
        scope: str = None,
        include_self: bool = False,
        **kwargs
    ):
        user = info.context.user
        qs = User.objects.all()

        if id:
            qs = qs.filter(id=id)

        if query:
            qs = qs.filter(name__istartswith=query)

        if not include_self:
            qs = qs.exclude(id=user.id)

        if scope == "followers":
            if not user.is_authenticated:
                qs = qs.none()
            else:
                qs = qs.filter(
                    id__in=Follower.objects.filter(to_user_id=user.id).values_list(
                        "from_user_id"
                    )
                )
        elif scope == "following":
            if not user.is_authenticated:
                qs = qs.none()
            else:
                qs = qs.filter(
                    id__in=Follower.objects.filter(from_user_id=user.id).values_list(
                        "to_user_id"
                    )
                )
        elif scope:
            qs = qs.none()

        qs = optimize_queryset(qs, info, "users")

        return qs
