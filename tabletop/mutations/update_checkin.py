from decimal import Decimal
from typing import List

import graphene
from django.db import IntegrityError, transaction

from tabletop.models import Checkin, Follower, Player, Tag, User
from tabletop.schema import CheckinNode, DecimalField


class UpdateCheckin(graphene.Mutation):
    class Arguments:
        checkIn = graphene.UUID(required=True)
        game = graphene.UUID(required=True)
        notes = graphene.String(required=False)
        rating = DecimalField(required=False)
        tags = graphene.List(graphene.String, required=False)
        players = graphene.List(graphene.UUID, required=False)
        winners = graphene.List(graphene.UUID, required=False)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    checkIn = graphene.Field(CheckinNode)

    def mutate(
        self,
        info,
        checkIn: str,
        notes: str = None,
        rating: Decimal = None,
        players: List[str] = None,
        winners: List[str] = None,
        tags: List[str] = None,
    ):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return UpdateCheckin(ok=False, errors=["Authentication required"])

        try:
            checkin = Checkin.objects.get(id=checkIn)
        except Checkin.DoesNotExist:
            return UpdateCheckin(ok=False, errors=["Invalid Checkin"])

        if not Player.objects.filter(
            checkin=checkin, user=current_user, confirmed=True
        ).exists():
            return UpdateCheckin(ok=False, errors=["Cannot edit this Checkin"])

        winners = set(winners) if winners else None

        with transaction.atomic():
            if players:
                players = set(players)
                for player_id in players:
                    is_user = player_id == current_user.id
                    if not (
                        is_user
                        or Follower.objects.filter(
                            to_user=current_user, from_user=player_id
                        ).exists()
                    ):
                        return UpdateCheckin(
                            ok=False,
                            errors=[
                                "Must be friends with {} to add as player".format(
                                    player_id
                                )
                            ],
                        )
                    player, created = Player.objects.get_or_create(
                        checkin=checkin,
                        user=(
                            current_user if is_user else User.objects.get(id=player_id)
                        ),
                        defaults={
                            "notes": notes if is_user else None,
                            "rating": rating if is_user else None,
                            "tags": tags if is_user else None,
                            "winner": player_id in winners if winners else None,
                            "confirmed": True,
                        },
                    )
            elif notes or rating or tags:
                player = Player.objects.get(checkin=checkin, user=current_user)
                fields = []
                if notes:
                    player.notes = notes
                    fields.append("notes")
                if rating:
                    player.rating = rating
                    fields.append("rating")
                if winners is not None:
                    player.winner = player_id in winners
                    fields.append("winner")
                if fields:
                    player.save(update_fields=fields)

                if tags:
                    for tag in tags:
                        try:
                            with transaction.atomic():
                                player.tags.add(Tag.objects.get(name=tag))
                        except IntegrityError:
                            pass
        return UpdateCheckin(ok=True, checkIn=checkin)
