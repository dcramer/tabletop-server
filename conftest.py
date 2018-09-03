from uuid import UUID

import graphene.test
import pytest
from django.contrib.auth.models import AnonymousUser

from server.accounts.models import User
from server.games.models import Game, Publisher
from server.schema import schema


class Context(object):
    user = AnonymousUser()


class GqlClient(graphene.test.Client):
    def execute(self, query, user=None):
        context = Context()
        if user:
            context.user = user
        return super().execute(query, context=context)


@pytest.fixture
def gql_client(db):
    return GqlClient(schema)


@pytest.fixture
def default_user(db):
    user = User(
        id=UUID("449c76aa-ad6a-46a8-b32b-91d965e3f462"),
        name="Reel Big Phish",
        email="reel.big.phish@example.com",
    )
    user.set_password("phish.reel.big")
    user.save()
    return user


@pytest.fixture
def default_publisher(db, default_user):
    return Publisher.objects.create(
        id=UUID("74451c13-2a97-42a2-b136-03af6cbb4153"),
        name="Guinea Pig Games",
        created_by=default_user,
        confirmed=True,
    )


@pytest.fixture
def default_game(db, default_publisher, default_user):
    return Game.objects.create(
        id=UUID("76111b88-301b-4620-9c93-7c6d28f0987b"),
        publisher=default_publisher,
        name="Unsettlers of Qatan",
        created_by=default_user,
        confirmed=True,
    )
