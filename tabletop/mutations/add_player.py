from decimal import Decimal
from typing import List

import graphene
from django.db import IntegrityError, transaction

from tabletop.models import Checkin, Follower, Player, Tag, User
from tabletop.schema import CheckinNode, DecimalField


class AddPlayer(graphene.Mutation):
    class Arguments:
        checkin = graphene.UUID(required=True)
        user = graphene.UUID(required=True)
        notes = graphene.String(required=False)
        rating = DecimalField(required=False)
        tags = graphene.List(graphene.String, required=False)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    checkin = graphene.Field(CheckinNode)

    def mutate(
        self,
        info,
        checkin: str,
        user: str,
        notes: str = None,
        rating: Decimal = None,
        tags: List[str] = None,
    ):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return Checkin(ok=False, errors=["Authentication required"])

        try:
            checkin = Checkin.objects.get(id=checkin)
        except Checkin.DoesNotExist:
            return Checkin(ok=False, errors=["Invalid Checkin"])

        # you can only add someone else to a check-in if you were already
        # added to the check-in or you are mutual friends with an existing player
        if user != current_user.id:
            player_ids = Player.objects.filter(checkin=checkin).values_list(
                "user", flat=True
            )
            is_user = False
            if current_user.id in player_ids:
                pass
            elif Follower.objects.filter(
                to_user=current_user, from_user_id__in=player_ids
            ):
                pass
            else:
                return AddPlayer(ok=False, errors=["Cannot add player to Checkin"])

            if notes:
                return AddPlayer(ok=False, errors=["Cannot add notes for other player"])

            if rating:
                return AddPlayer(
                    ok=False, errors=["Cannot add rating for other player"]
                )

            if tags:
                return AddPlayer(ok=False, errors=["Cannot add tags for other player"])

            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                return AddPlayer(ok=False, errors=["Invalid user"])
        else:
            is_user = True
            user = current_user

        try:
            with transaction.atomic():
                player = Player.objects.create(
                    checkin=checkin,
                    user=user,
                    notes=notes if is_user else None,
                    rating=rating if is_user else None,
                    confirmed=False,
                )
                if is_user and tags:
                    for tag in tags:
                        player.tags.add(Tag.objects.get(name=tag))
        except IntegrityError:
            return AddPlayer(ok=False, errors=["Player already exists"])

        return AddPlayer(ok=True, checkin=checkin)
