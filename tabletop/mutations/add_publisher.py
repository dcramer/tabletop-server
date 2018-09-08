import graphene
from django.db import IntegrityError, transaction

from tabletop.models import Publisher
from tabletop.schema import PublisherNode


class AddPublisher(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    publisher = graphene.Field(PublisherNode)

    def mutate(self, info, name: str = None, country: str = None, region: str = None):
        if not info.context.user.is_authenticated:
            return AddPublisher(ok=False, errors=["Authentication required"])

        try:
            with transaction.atomic():
                result = Publisher.objects.create(
                    name=name, created_by=info.context.user
                )
        except IntegrityError as exc:
            if "duplicate key" in str(exc):
                return AddPublisher(ok=False, errors=["Publisher already exists."])
            raise
        return AddPublisher(ok=True, publisher=result)
