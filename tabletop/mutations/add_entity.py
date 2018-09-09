import graphene
from django.db import IntegrityError, transaction

from tabletop.models import Entity
from tabletop.schema import EntityNode


class AddEntity(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    entity = graphene.Field(EntityNode)

    def mutate(self, info, name: str = None):
        if not info.context.user.is_authenticated:
            return AddEntity(ok=False, errors=["Authentication required"])

        try:
            with transaction.atomic():
                result = Entity.objects.create(name=name, created_by=info.context.user)
        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                return AddEntity(ok=False, errors=["Entity already exists."])
            raise
        return AddEntity(ok=True, entity=result)
