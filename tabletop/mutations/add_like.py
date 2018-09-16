import graphene
from django.db import IntegrityError, transaction

from tabletop.models import Checkin, Follower, Like, Player
from tabletop.schema import LikeNode


class AddLike(graphene.Mutation):
    class Arguments:
        checkin = graphene.UUID(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    like = graphene.Field(LikeNode)

    def mutate(self, info, checkin: str = None):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return AddLike(ok=False, errors=["Authentication required"])

        try:
            checkin = Checkin.objects.get(id=checkin)
        except Checkin.DoesNotExist:
            return AddLike(ok=False, errors=["Checkin not found"])

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
            return AddLike(ok=False, errors=["Cannot add like to Checkin"])

        try:
            with transaction.atomic():
                result = Like.objects.create(
                    checkin=checkin, created_by=info.context.user
                )

        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                result = Like.objects.get(checkin=checkin, created_by=info.context.user)
            else:
                raise

        return AddLike(ok=True, like=result)
