import graphene
from . import checkins, games, me, publishers, tags, users


class RootQuery(
    checkins.Query,
    games.Query,
    publishers.Query,
    tags.Query,
    me.Query,
    users.Query,
    graphene.ObjectType,
):
    pass
