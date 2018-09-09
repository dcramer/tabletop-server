from graphene_django.types import DjangoObjectType

from tabletop.models import Comment


class CommentNode(DjangoObjectType):
    class Meta:
        model = Comment
        name = "Comment"
