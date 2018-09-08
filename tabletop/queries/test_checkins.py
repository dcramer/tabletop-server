import pytest

from tabletop.models import Checkin, Follower, Player, User


@pytest.fixture
def other_user():
    return User.objects.create(name="Fizz Buzz", email="fizz.buzz@example.com")


def test_get_checkin(gql_client, default_game, default_user, other_user):
    checkin = Checkin.objects.create(game=default_game, created_by=other_user)
    Player.objects.create(checkin=checkin, user=other_user)
    executed = gql_client.execute(
        """{checkins(id:"%s") {id}}""" % (str(checkin.id),), user=default_user
    )
    assert executed["data"]["checkins"] == [{"id": str(checkin.id)}]


def test_activity_from_friends_no_relation(
    gql_client, default_game, default_user, other_user
):
    checkin = Checkin.objects.create(game=default_game, created_by=other_user)
    Player.objects.create(checkin=checkin, user=other_user)
    executed = gql_client.execute(
        """{checkins(scope:friends) {id}}""", user=default_user
    )
    assert executed["data"]["checkins"] == []


def test_activity_from_friends(gql_client, default_game, default_user, other_user):
    Follower.objects.create(from_user=default_user, to_user=other_user)
    checkin = Checkin.objects.create(game=default_game, created_by=default_user)
    Player.objects.create(checkin=checkin, user=other_user)
    executed = gql_client.execute(
        """{checkins(scope:friends) {id}}""", user=default_user
    )
    assert executed["data"]["checkins"] == [{"id": str(checkin.id)}]


def test_activity_from_friends_includes_self(
    gql_client, default_game, default_user, other_user
):
    checkin = Checkin.objects.create(game=default_game, created_by=default_user)
    Player.objects.create(checkin=checkin, user=default_user)
    executed = gql_client.execute(
        """{checkins(scope:public) {id}}""", user=default_user
    )
    assert executed["data"]["checkins"] == [{"id": str(checkin.id)}]


def test_activity_from_public(gql_client, default_game, default_user, other_user):
    checkin = Checkin.objects.create(game=default_game, created_by=other_user)
    Player.objects.create(checkin=checkin, user=other_user)
    executed = gql_client.execute(
        """{checkins(scope:public) {id}}""", user=default_user
    )
    assert executed["data"]["checkins"] == [{"id": str(checkin.id)}]


def test_activity_from_public_includes_self(
    gql_client, default_game, default_user, other_user
):
    checkin = Checkin.objects.create(game=default_game, created_by=default_user)
    Player.objects.create(checkin=checkin, user=default_user)
    executed = gql_client.execute(
        """{checkins(scope:public) {id}}""", user=default_user
    )
    assert executed["data"]["checkins"] == [{"id": str(checkin.id)}]
