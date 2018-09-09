import graphene
from django.db import IntegrityError, transaction

from tabletop.models import DurationType, Entity, Game
from tabletop.schema import GameNode


class AddGame(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        parent = graphene.UUID(required=False)
        entities = graphene.List(graphene.UUID, required=True)
        min_players = graphene.Int(required=False)
        max_players = graphene.Int(required=False)
        duration = graphene.Int(required=False)
        duration_type = graphene.Argument(graphene.Enum.from_enum(DurationType))

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    game = graphene.Field(GameNode)

    def mutate(
        self,
        info,
        name: str = None,
        parent: str = None,
        entities: str = None,
        min_players: int = None,
        max_players: int = None,
        duration: int = None,
        duration_type: DurationType = None,
    ):
        if not info.context.user.is_authenticated:
            return AddGame(ok=False, errors=["Authentication required"])

        if duration and not duration_type:
            return AddGame(ok=False, errors=["Missing duration_type"])

        if parent:
            try:
                parent = Game.objects.get(id=parent)
            except Game.DoesNotExist:
                return AddGame(ok=False, errors=["Parent game not found"])

        if entities:

            try:
                entities = [Entity.objects.get(id=e) for e in entities]
            except Entity.DoesNotExist:
                return AddGame(ok=False, errors=["Entity not found"])

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
                        result.entities.add(entity)

        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                return AddGame(ok=False, errors=["Game already exists."])
            raise

        return AddGame(ok=True, game=result)
