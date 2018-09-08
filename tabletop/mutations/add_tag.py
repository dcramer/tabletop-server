import graphene
from django.db import IntegrityError, transaction

from tabletop.models import Tag
from tabletop.schema import TagNode


class AddTag(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    tag = graphene.Field(TagNode)

    def mutate(self, info, name: str = None, country: str = None, region: str = None):
        if not info.context.user.is_authenticated:
            return AddTag(ok=False, errors=["Authentication required"])

        try:
            with transaction.atomic():
                result = Tag.objects.create(name=name, created_by=info.context.user)
        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                return AddTag(ok=False, errors=["Tag already exists."])
            raise
        return AddTag(ok=True, tag=result)
