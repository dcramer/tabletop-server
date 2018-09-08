from graphene_django.types import DjangoObjectType

from tabletop.models import Checkin


class CheckinNode(DjangoObjectType):
    class Meta:
        model = Checkin
        name = "Checkin"
