import graphene
from django.db.models import F, Q

from tabletop.models import DurationType, Game
from tabletop.schema import GameNode
from tabletop.utils.graphene import optimize_queryset


class Query(object):
    games = graphene.List(
        GameNode,
        id=graphene.UUID(),
        query=graphene.String(),
        players=graphene.Int(),
        entity=graphene.UUID(),
        max_duration=graphene.Int(),
        parent=graphene.UUID(),
    )

    def resolve_games(
        self,
        info,
        id: str = None,
        query: str = None,
        parent: str = None,
        players: int = None,
        entity: str = None,
        max_duration: int = None,
    ):
        qs = Game.objects.select_related("image").distinct()
        if id:
            qs = qs.filter(id=id)
        if parent:
            qs = qs.filter(parent=parent)
        if query:
            qs = qs.filter(name__istartswith=query)
        if entity:
            qs = qs.filter(entities=entity)
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
