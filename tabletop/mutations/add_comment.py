import graphene
from django.db import IntegrityError, transaction

from tabletop.models import Checkin, Comment, Follower, Player
from tabletop.schema import CheckinNode, CommentNode


class AddComment(graphene.Mutation):
    class Arguments:
        checkin = graphene.UUID(required=True)
        text = graphene.String(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    comment = graphene.Field(CommentNode)
    checkin = graphene.Field(CheckinNode)

    def mutate(self, info, checkin: str = None, text: str = None):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return AddComment(ok=False, errors=["Authentication required"])

        try:
            checkin = Checkin.objects.get(id=checkin)
        except Checkin.DoesNotExist:
            return AddComment(ok=False, errors=["Checkin not found"])

        # you can only comment if you are friends w/ one of the players
        # or a player in the agme
        player_ids = Player.objects.filter(checkin=checkin).values_list(
            "user", flat=True
        )
        if current_user.id in player_ids:
            pass
        elif Follower.objects.filter(to_user=current_user, from_user_id__in=player_ids):
            pass
        else:
            return AddComment(ok=False, errors=["Cannot add comment to Checkin"])

        try:
            with transaction.atomic():
                result = Comment.objects.create(
                    checkin=checkin, text=text, created_by=info.context.user
                )

        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                return AddComment(ok=False, errors=["Comment already exists."])
            raise

        return AddComment(ok=True, comment=result, checkin=checkin)
