import graphene
from graphene_django.types import DjangoObjectType

from tabletop.models import Checkin


class CheckinNode(DjangoObjectType):
    total_comments = graphene.Int(required=False)
    total_likes = graphene.Int(required=False)
    is_liked = graphene.Boolean(required=False)

    class Meta:
        model = Checkin
        name = "Checkin"

    def resolve_is_liked(self, info):
        return getattr(self, "is_liked", False)
