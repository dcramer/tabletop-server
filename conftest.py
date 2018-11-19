from uuid import UUID

import graphene.test
import pytest
from django.contrib.auth.models import AnonymousUser
from django.db import transaction

from tabletop import factories
from tabletop.models import Checkin, CollectionGame, Player
from tabletop.root_schema import schema


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
    user = factories.UserFactory(
        id=UUID("449c76aa-ad6a-46a8-b32b-91d965e3f462"),
        name="Reel Big Phish",
        email="reel.big.phish@example.com",
    )
    user.set_password("phish.reel.big")
    user.save()
    return user


@pytest.fixture
def default_publisher(db, default_user):
    return factories.EntityFactory.create(
        id=UUID("74451c13-2a97-42a2-b136-03af6cbb4153"),
        name="Guinea Pig Games",
        created_by=default_user,
        confirmed=True,
    )


@pytest.fixture
def default_artist(db, default_user):
    return factories.EntityFactory.create(
        id=UUID("449c76aa-2a97-42a2-b136-03af6cbb4153"),
        name="John Cusoe",
        created_by=default_user,
        confirmed=True,
    )


@pytest.fixture
def default_designer(db, default_user):
    return factories.EntityFactory.create(
        id=UUID("449c76aa-2a97-42a2-b136-91d965e3f462"),
        name="John Cusoe",
        created_by=default_user,
        confirmed=True,
    )


@pytest.fixture
def default_game(db, default_publisher, default_user):
    return factories.GameFactory.create(
        id=UUID("76111b88-301b-4620-9c93-7c6d28f0987b"),
        name="Unsettlers of Qatan",
        created_by=default_user,
        confirmed=True,
    )


@pytest.fixture
def default_checkin(db, default_game, default_user):
    checkin = Checkin.objects.create(
        id=UUID("4b2a619c-40a8-4f58-96a5-c2f74795bfa7"),
        game=default_game,
        created_by=default_user,
    )
    Player.objects.create(checkin=checkin, user=default_user)
    return checkin


@pytest.fixture
def default_collection(db, default_game, default_user):
    with transaction.atomic():
        collection = factories.CollectionFactory.create(
            id=UUID("6960436f-53cd-4d00-bd5b-a293349e7d1f"),
            name="My Games",
            created_by=default_user,
        )
        CollectionGame.objects.create(game=default_game, collection=collection)
    return collection
