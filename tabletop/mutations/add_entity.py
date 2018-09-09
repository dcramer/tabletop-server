import graphene
from django.db import IntegrityError, transaction

from tabletop.models import Entity, EntityType
from tabletop.schema import EntityNode, EntityTypeEnum


class AddEntity(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        _type = graphene.Argument(EntityTypeEnum, name="type")

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    entity = graphene.Field(EntityNode)

    def mutate(self, info, name: str = None, _type: EntityType = None):
        if not info.context.user.is_authenticated:
            return AddEntity(ok=False, errors=["Authentication required"])

        try:
            with transaction.atomic():
                result = Entity.objects.create(
                    name=name, type=_type, created_by=info.context.user
                )
        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                return AddEntity(ok=False, errors=["Entity already exists."])
            raise
        return AddEntity(ok=True, entity=result)
