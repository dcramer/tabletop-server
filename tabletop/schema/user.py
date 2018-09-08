import graphene
from graphene_django.types import DjangoObjectType

from tabletop.models import User


# TODO(dcramer): how do we return following/follower status efficiently here?
class UserNode(DjangoObjectType):
    email = graphene.String(required=False)
    following = graphene.Boolean()
    follower = graphene.Boolean()

    class Meta:
        model = User
        name = "User"
        only_fields = ("id", "email", "name")

    def resolve_email(self, info):
        user = info.context.user
        if user.is_authenticated and user.id == self.id:
            return self.email
        return None
