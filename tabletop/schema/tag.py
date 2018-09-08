from graphene_django.types import DjangoObjectType

from tabletop.models import Tag


class TagNode(DjangoObjectType):
    class Meta:
        name = "Tag"
        model = Tag
