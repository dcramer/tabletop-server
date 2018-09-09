from graphene_django.types import DjangoObjectType

from tabletop.models import Like


class LikeNode(DjangoObjectType):
    class Meta:
        model = Like
        name = "Like"
