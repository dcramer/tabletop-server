import graphene

from . import checkins, entities, games, me, tags, users


class RootQuery(
    checkins.Query,
    entities.Query,
    games.Query,
    tags.Query,
    me.Query,
    users.Query,
    graphene.ObjectType,
):
    pass
