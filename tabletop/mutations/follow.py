import graphene

from tabletop.models import Follower, User
from tabletop.schema import UserNode


class Follow(graphene.Mutation):
    """
    Follow a user
    """

    class Arguments:
        user = graphene.UUID(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    token = graphene.String()
    user = graphene.Field(UserNode)

    def mutate(self, info, user: str):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return Follow(ok=False, errors=["Requires authentication"])

        user = User.objects.exclude(id=info.context.user.id).get(id=user)
        Follower.objects.create(from_user=current_user, to_user=user)
        return Follow(ok=True, user=user)
