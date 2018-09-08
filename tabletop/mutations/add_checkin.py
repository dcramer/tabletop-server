from decimal import Decimal
from typing import List

import graphene
from django.db import transaction

from tabletop.models import Checkin, Follower, Game, Player, Tag, User
from tabletop.schema import CheckinNode, DecimalField


class AddCheckin(graphene.Mutation):
    class Arguments:
        game = graphene.UUID(required=True)
        notes = graphene.String(required=False)
        rating = DecimalField(required=False)
        tags = graphene.List(graphene.String, required=False)
        players = graphene.List(graphene.UUID, required=False)
        winners = graphene.List(graphene.UUID, required=False)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    checkin = graphene.Field(CheckinNode)

    def mutate(
        self,
        info,
        game: str = None,
        notes: str = None,
        rating: Decimal = None,
        tags: List[str] = None,
        players: List[str] = None,
        winners: List[str] = None,
    ):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return AddCheckin(ok=False, errors=["Authentication required"])

        with transaction.atomic():
            result = Checkin.objects.create(
                game=Game.objects.get(id=game), created_by=current_user
            )
            players = set(players or [])
            # current user is always a player
            players.add(current_user.id)
            winners = set(winners) if winners is not None else None
            for player_id in players:
                is_user = player_id == current_user.id
                if not (
                    is_user
                    or Follower.objects.filter(
                        to_user=current_user, from_user=player_id
                    ).exists()
                ):
                    return AddCheckin(
                        ok=False,
                        errors=[
                            "Must be friends with {} to add as player".format(player_id)
                        ],
                    )

                player = Player.objects.create(
                    checkin=result,
                    user=current_user if is_user else User.objects.get(id=player_id),
                    notes=notes if is_user else None,
                    rating=rating if is_user else None,
                    winner=player_id in winners if winners is not None else None,
                    confirmed=True,
                )
                if is_user and tags:
                    for tag in tags:
                        player.tags.add(Tag.objects.get(name=tag))
        return AddCheckin(ok=True, checkin=result)
