import graphene
from django.db.models import Aggregate, Avg, Count, F, FloatField, Prefetch, Q

from tabletop.models import Collection, DurationType, Game
from tabletop.schema import GameNode
from tabletop.utils.graphene import optimize_queryset


# http://www.evanmiller.org/how-not-to-sort-by-average-rating.html
class WilsonScore(Aggregate):
    name = "WilsonScore"
    template = (
        "CASE WHEN COUNT(%(expressions)s) > 0 THEN ((COUNT(CASE WHEN %(expressions)s > 3 THEN 1 END) + 1.9208) / (COUNT(%(expressions)s)) - "
        "1.96 * SQRT((COUNT(%(expressions)s)) / (COUNT(%(expressions)s)) + 0.9604) / "
        "(COUNT(%(expressions)s))) / (1 + 3.8416 / (COUNT(%(expressions)s))) ELSE 0 END"
    )
    output_field = FloatField()

    def convert_value(self, value, expression, connection):
        return 0.0 if value is None else value


def fix_games_queryset(queryset, selected_fields, info):
    current_user = info.context.user
    if "rating" in selected_fields:
        if "rating.averageScore" in selected_fields:
            queryset = queryset.annotate(rating_average_score=Avg("ratings__rating"))
        if "rating.totalVotes" in selected_fields:
            queryset = queryset.annotate(rating_total_votes=Count("ratings"))
        if "rating.wilsonLowerBound" in selected_fields:
            queryset = queryset.annotate(
                rating_wilson_lower_bound=WilsonScore("ratings__rating")
            )
    if "collections" in selected_fields:
        if current_user.is_authenticated:
            queryset = queryset.prefetch_related(
                Prefetch(
                    "collections",
                    queryset=Collection.objects.filter(created_by=current_user),
                )
            )
    return queryset


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
        # TODO(dcramer): fix optimize_queryset so it handles the OneToOne join automatically
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
        qs = optimize_queryset(qs, info, "games", fix_games_queryset)
        return qs.order_by("name")
