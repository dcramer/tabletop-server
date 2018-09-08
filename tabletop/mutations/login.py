from typing import Optional

import facebook
import graphene
from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction

from tabletop.models import Identity, User
from tabletop.schema import UserNode
from tabletop.utils.auth import generate_token


def get_user_from_facebook_token(token: str = None) -> Optional[User]:
    graph = facebook.GraphAPI(access_token=token)

    try:
        profile = graph.get_object("me", fields="id,name,email")
    except facebook.GraphAPIError as e:
        if "Invalid OAuth access token" in str(e):
            return None
        raise

    external_id = str(profile["id"])
    for i in range(2):
        identity = (
            Identity.objects.filter(provider="facebook", external_id=external_id)
            .select_related("user")
            .first()
        )
        if identity:
            return identity.user
        try:
            with transaction.atomic():
                user = User.objects.create(email=profile["email"], name=profile["name"])
                identity = Identity.objects.create(
                    user=user, provider="facebook", external_id=external_id
                )
                return user
        except IntegrityError:
            pass
    return user


class Login(graphene.Mutation):
    """
    Mutation to login a user
    """

    class Arguments:
        email = graphene.String(required=False)
        password = graphene.String(required=False)
        facebook_token = graphene.String(required=False)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    token = graphene.String()
    user = graphene.Field(UserNode)

    def mutate(
        self, info, email: str = None, password: str = None, facebook_token: str = None
    ):
        if facebook_token:
            user = get_user_from_facebook_token(facebook_token)
        elif email and password:
            user = authenticate(email=email, password=password)
        else:
            user = None

        if not user:
            return Login(
                ok=False, errors=["Unable to login with provided credentials."]
            )
        # we stuff the user into the current request so they can serialize sensitive attributes
        info.context.user = user
        return Login(ok=True, user=user, token=generate_token(user))
