import graphene

from tabletop.models import Checkin, Follower, Like, Player
from tabletop.schema import CheckinNode


class RemoveLike(graphene.Mutation):
    class Arguments:
        checkin = graphene.UUID(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    checkin = graphene.Field(CheckinNode)

    def mutate(self, info, checkin: str = None):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return RemoveLike(ok=False, errors=["Authentication required"])

        try:
            checkin = Checkin.objects.get(id=checkin)
        except Checkin.DoesNotExist:
            return RemoveLike(ok=False, errors=["Checkin not found"])

        # you can only like if you are friends w/ one of the players
        # or a player in the agme
        player_ids = Player.objects.filter(checkin=checkin).values_list(
            "user", flat=True
        )
        if current_user.id in player_ids:
            pass
        elif Follower.objects.filter(to_user=current_user, from_user_id__in=player_ids):
            pass
        else:
            return RemoveLike(ok=False, errors=["Cannot remove like from Checkin"])

        Like.objects.filter(checkin=checkin, created_by=info.context.user).delete()

        return RemoveLike(ok=True, checkin=checkin)
