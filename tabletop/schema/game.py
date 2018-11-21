from decimal import Decimal

import graphene
from django.db.models import Avg, Count, Prefetch
from graphene_django.types import DjangoObjectType

from dataclasses import dataclass
from tabletop.models import Collection, Game, GameImage, GameRating
from tabletop.utils.query import WilsonScore

from .collection import CollectionNode
from .decimal import DecimalField


@dataclass
class Rating:
    parent: Game = None
    average_score: Decimal = None
    total_votes: int = 0
    wilson_lower_bound: float = None


class GameImageNode(DjangoObjectType):
    url = graphene.String()

    class Meta:
        name = "GameImage"
        model = GameImage
        only_fields = ("width", "height")

    def resolve_url(self, args):
        if not self.file:
            return None
        url = self.file.url
        if not url.startswith(("http:", "https:")):
            if not url.startswith("/"):
                url = "/" + url
            url = args.context.build_absolute_uri(url)
        return url


class RatingNode(graphene.ObjectType):
    wilson_lower_bound = graphene.Float()
    average_score = DecimalField()
    total_votes = graphene.Int()

    def resolve_average_score(self, info):
        if self.average_score:
            return self.average_score
        if not self.parent:
            return None
        return GameRating.objects.filter(game=self.parent.id).aggregate(
            t=Avg("rating")
        )["t"]

    def resolve_total_votes(self, info):
        if self.total_votes:
            return self.total_votes
        if not self.parent:
            return None
        return (
            GameRating.objects.filter(game=self.parent.id).aggregate(t=Count("*"))["t"]
            or 0
        )

    def resolve_wilson_lower_bound(self, info):
        if self.wilson_lower_bound:
            return self.wilson_lower_bound
        if not self.parent:
            return None
        return (
            GameRating.objects.filter(game=self.parent.id).aggregate(
                t=WilsonScore("rating")
            )["t"]
            or 0.0
        )


class GameNode(DjangoObjectType):
    image = GameImageNode()
    collections = graphene.List(CollectionNode)
    rating = graphene.Field(RatingNode)

    class Meta:
        name = "Game"
        model = Game

    def resolve_rating(self, info):
        result = {}
        if hasattr(self, "rating_average_score"):
            result["average_score"] = self.rating_average_score
        if hasattr(self, "rating_total_votes"):
            result["total_votes"] = self.rating_total_votes
        if hasattr(self, "rating_wilson_lower_bound"):
            result["wilson_lower_bound"] = self.rating_wilson_lower_bound
        return Rating(parent=self, **result)

    def resolve_collections(self, info):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return []
        if not hasattr(self, "collections"):
            return list(
                Collection.objects.filter(created_by=current_user, game=self.id)
            )
        # TODO(dcramer): need to confirm this is always pre-filtered
        return list(self.collections.all())

    @staticmethod
    def fix_queryset(queryset, selected_fields, info):
        current_user = info.context.user
        if "rating" in selected_fields:
            if "rating.averageScore" in selected_fields:
                queryset = queryset.annotate(
                    rating_average_score=Avg("ratings__rating")
                )
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
