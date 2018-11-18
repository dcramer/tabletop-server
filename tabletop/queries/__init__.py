import graphene

from . import checkins, collections, comments, entities, games, likes, me, tags, users


class RootQuery(
    checkins.Query,
    collections.Query,
    comments.Query,
    entities.Query,
    games.Query,
    likes.Query,
    tags.Query,
    me.Query,
    users.Query,
    graphene.ObjectType,
):
    pass
