import graphene
from django.db import IntegrityError, transaction

from .models import DurationType, Game, Publisher, Tag
from .schema import GameNode, PublisherNode, TagNode


class AddGame(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        parent = graphene.UUID(required=False)
        publisher = graphene.UUID(required=True)
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
        publisher: str = None,
        min_players: int = None,
        max_players: int = None,
        duration: int = None,
        duration_type: str = None,
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

        if publisher:
            try:
                publisher = Publisher.objects.get(id=publisher)
            except Publisher.DoesNotExist:
                return AddGame(ok=False, errors=["Publisher not found"])

        try:
            with transaction.atomic():
                result = Game.objects.create(
                    name=name,
                    publisher=publisher,
                    parent=parent,
                    min_players=min_players,
                    max_players=max_players,
                    duration=duration,
                    duration_type=duration_type,
                    created_by=info.context.user,
                )
        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                return AddGame(ok=False, errors=["Game already exists."])
            raise

        return AddGame(ok=True, game=result)


class AddPublisher(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    publisher = graphene.Field(PublisherNode)

    def mutate(self, info, name: str = None, country: str = None, region: str = None):
        if not info.context.user.is_authenticated:
            return AddPublisher(ok=False, errors=["Authentication required"])

        try:
            with transaction.atomic():
                result = Publisher.objects.create(
                    name=name, created_by=info.context.user
                )
        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                return AddPublisher(ok=False, errors=["Publisher already exists."])
            raise
        return AddPublisher(ok=True, publisher=result)


class AddTag(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    tag = graphene.Field(TagNode)

    def mutate(self, info, name: str = None, country: str = None, region: str = None):
        if not info.context.user.is_authenticated:
            return AddTag(ok=False, errors=["Authentication required"])

        try:
            with transaction.atomic():
                result = Tag.objects.create(name=name, created_by=info.context.user)
        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                return AddTag(ok=False, errors=["Tag already exists."])
            raise
        return AddTag(ok=True, tag=result)


class Mutation(graphene.ObjectType):
    addGame = AddGame.Field()
    addPublisher = AddPublisher.Field()
    addTag = AddTag.Field()
