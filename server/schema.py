import graphene

import server.accounts.mutations
import server.accounts.schema
import server.activity.mutations
import server.activity.schema
import server.games.mutations
import server.games.schema


class RootQuery(
    server.accounts.schema.Query,
    server.activity.schema.Query,
    server.games.schema.Query,
    graphene.ObjectType,
):
    pass


class RootMutation(
    server.accounts.mutations.Mutation,
    server.activity.mutations.Mutation,
    server.games.mutations.Mutation,
):
    pass


schema = graphene.Schema(query=RootQuery, mutation=RootMutation)
