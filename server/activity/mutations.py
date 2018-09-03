from decimal import Decimal
from typing import List

import graphene
from django.db import IntegrityError, transaction
from graphql.language.ast import FloatValue, IntValue

from server.accounts.models import Follower, User
from server.games.models import Game, Tag

from .models import CheckIn, Player
from .schema import CheckInNode


class DecimalField(graphene.Scalar):
    class Meta:
        name = "Decimal"

    @staticmethod
    def coerce_decimal(value):
        return Decimal(str(value))

    serialize = coerce_decimal
    parse_value = coerce_decimal

    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, IntValue) or isinstance(ast, FloatValue):
            num = Decimal(str(ast.value))
            return num


class AddCheckIn(graphene.Mutation):
    class Arguments:
        game = graphene.UUID(required=True)
        notes = graphene.String(required=False)
        rating = DecimalField(required=False)
        tags = graphene.List(graphene.String, required=False)
        players = graphene.List(graphene.UUID, required=False)
        winners = graphene.List(graphene.UUID, required=False)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    checkIn = graphene.Field(CheckInNode)

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
            return AddCheckIn(ok=False, errors=["Authentication required"])

        with transaction.atomic():
            result = CheckIn.objects.create(
                game=Game.objects.get(id=game), created_by=current_user
            )
            players = set(players or [])
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
                    return AddCheckIn(
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
        return AddCheckIn(ok=True, checkIn=result)


class AddPlayer(graphene.Mutation):
    class Arguments:
        checkIn = graphene.UUID(required=True)
        user = graphene.UUID(required=True)
        notes = graphene.String(required=False)
        rating = DecimalField(required=False)
        tags = graphene.List(graphene.String, required=False)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    checkIn = graphene.Field(CheckInNode)

    def mutate(
        self,
        info,
        checkIn: str,
        user: str,
        notes: str = None,
        rating: Decimal = None,
        tags: List[str] = None,
    ):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return CheckIn(ok=False, errors=["Authentication required"])

        try:
            checkin = CheckIn.objects.get(id=checkIn)
        except CheckIn.DoesNotExist:
            return CheckIn(ok=False, errors=["Invalid CheckIn"])

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
                return AddPlayer(ok=False, errors=["Cannot add player to CheckIn"])

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

        return AddPlayer(ok=True, checkIn=checkin)


class UpdateCheckIn(graphene.Mutation):
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
    checkIn = graphene.Field(CheckInNode)

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
            return UpdateCheckIn(ok=False, errors=["Authentication required"])

        try:
            checkin = CheckIn.objects.get(id=checkIn)
        except CheckIn.DoesNotExist:
            return UpdateCheckIn(ok=False, errors=["Invalid CheckIn"])

        if not Player.objects.filter(
            checkin=checkin, user=current_user, confirmed=True
        ).exists():
            return UpdateCheckIn(ok=False, errors=["Cannot edit this CheckIn"])

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
                        return UpdateCheckIn(
                            ok=False,
                            errors=[
                                "Must be friends with {} to add as player".format(
                                    player_id
                                )
                            ],
                        )
                    player, created = Player.objects.get_or_create(
                        checkin=checkin,
                        user=current_user
                        if is_user
                        else User.objects.get(id=player_id),
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
        return UpdateCheckIn(ok=True, checkIn=checkin)


class Mutation(graphene.ObjectType):
    addCheckIn = AddCheckIn.Field()
    addPlayer = AddPlayer.Field()
    updateCheckIn = UpdateCheckIn.Field()
