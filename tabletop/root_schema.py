import graphene

import tabletop.mutations
import tabletop.queries

schema = graphene.Schema(
    query=tabletop.queries.RootQuery, mutation=tabletop.mutations.RootMutation
)
