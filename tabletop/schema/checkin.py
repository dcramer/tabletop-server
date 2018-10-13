import graphene
from graphene_django.types import DjangoObjectType

from tabletop.models import Checkin, Like


class CheckinNode(DjangoObjectType):
    total_comments = graphene.Int(required=False)
    total_likes = graphene.Int(required=False)
    is_liked = graphene.Boolean(required=False)

    class Meta:
        model = Checkin
        name = "Checkin"

    def resolve_is_liked(self, info):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return False
        if not hasattr(self, "is_liked"):
            return Like.objects.filter(
                created_by=current_user, checkin=self.id
            ).exists()
        return self.is_liked
