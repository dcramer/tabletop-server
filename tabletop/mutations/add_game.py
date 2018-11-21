from decimal import Decimal
from typing import List

import graphene
from django.db import IntegrityError, transaction

from tabletop.models import DurationType, Entity, Game, GameEntity, GameRating
from tabletop.schema import DecimalField, EntityTypeEnum, GameNode


class EntityInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    type = graphene.Argument(EntityTypeEnum, required=True)


class AddGame(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        parent = graphene.UUID(required=False)
        entities = graphene.List(EntityInput, required=False)
        min_players = graphene.Int(required=False)
        max_players = graphene.Int(required=False)
        duration = graphene.Int(required=False)
        duration_type = graphene.Argument(graphene.Enum.from_enum(DurationType))
        rating = DecimalField(required=False)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    game = graphene.Field(GameNode)

    def mutate(
        self,
        info,
        name: str = None,
        parent: str = None,
        entities: List[EntityInput] = None,
        min_players: int = None,
        max_players: int = None,
        duration: int = None,
        duration_type: DurationType = None,
        rating: Decimal = None,
    ):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return AddGame(ok=False, errors=["Authentication required"])

        if duration and not duration_type:
            return AddGame(ok=False, errors=["Missing duration_type"])

        if parent:
            try:
                parent = Game.objects.get(id=parent)
            except Game.DoesNotExist:
                return AddGame(ok=False, errors=["Parent game not found"])

        try:
            with transaction.atomic():
                result = Game.objects.create(
                    name=name,
                    parent=parent,
                    min_players=min_players,
                    max_players=max_players,
                    duration=duration,
                    duration_type=duration_type,
                    created_by=info.context.user,
                )
                if entities:
                    for entity in entities:
                        GameEntity.objects.create(
                            entity=Entity.objects.get_or_create(name=entity.name)[0],
                            game=result,
                            type=entity.type,
                        )

                if rating:
                    GameRating.objects.create(
                        game=result, user=current_user, rating=rating
                    )

        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                return AddGame(ok=False, errors=["Game already exists."])
            raise

        return AddGame(ok=True, game=result)
