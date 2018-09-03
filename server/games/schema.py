import graphene
from django.db.models import F, Q
from graphene_django.types import DjangoObjectType

from server.utils import optimize_queryset

from .models import DurationType, Game, Publisher, Tag


class GameNode(DjangoObjectType):
    class Meta:
        name = "Game"
        model = Game


class PublisherNode(DjangoObjectType):
    class Meta:
        name = "Publisher"
        model = Publisher


class TagNode(DjangoObjectType):
    class Meta:
        name = "Tag"
        model = Tag


class Query(object):
    games = graphene.List(
        GameNode,
        id=graphene.UUID(),
        query=graphene.String(),
        players=graphene.Int(),
        max_duration=graphene.Int(),
    )
    publishers = graphene.List(
        PublisherNode, id=graphene.UUID(), query=graphene.String()
    )
    tags = graphene.List(TagNode, id=graphene.UUID(), query=graphene.String())

    def resolve_games(
        self,
        info,
        id: str = None,
        query: str = None,
        players: int = None,
        max_duration: int = None,
    ):
        qs = Game.objects.all()
        if id:
            qs = qs.filter(id=id)
        if query:
            qs = qs.filter(
                Q(name__istartswith=query) | Q(publisher__name__istartswith=query)
            )
        if players:
            qs = qs.filter(min_players__lte=players, max_players__gte=players)
        if max_duration:
            qs = qs.filter(
                Q(duration__lte=max_duration, duration_type=DurationType.total)
                | Q(
                    duration__lte=max_duration
                    / (players if players else F("max_players")),
                    duration_type=DurationType.per_player,
                )
            )
        qs = optimize_queryset(qs, info, "games")
        return qs.order_by("name")

    def resolve_publishers(self, info, id: str = None, query: str = None):
        qs = Publisher.objects.all()
        if id:
            qs = qs.filter(id=id)
        if query:
            qs = qs.filter(name__istartswith=query)
        qs = optimize_queryset(qs, info, "publishers")
        return qs.order_by("name")

    def resolve_tags(self, info, id: str = None, query: str = None):
        qs = Tag.objects.all()
        if id:
            qs = qs.filter(id=id)
        if query:
            qs = qs.filter(name__istartswith=query)
        qs = optimize_queryset(qs, info, "tags")
        return qs.order_by("name")
