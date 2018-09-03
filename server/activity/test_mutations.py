from decimal import Decimal

import pytest

from server.accounts.models import Follower, User
from server.activity.models import CheckIn, Player


@pytest.fixture
def other_user():
    return User.objects.create(name="Fizz Buzz", email="fizz.buzz@example.com")


def test_add_checkin_minimum_requirements(gql_client, default_user, default_game):
    executed = gql_client.execute(
        """
    mutation {
        addCheckIn(game:"%s") {
            ok
            errors
            checkIn {id}
        }
    }"""
        % (default_game.id,),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addCheckIn"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    checkin = CheckIn.objects.get(id=resp["checkIn"]["id"])
    assert checkin.game_id == default_game.id
    assert checkin.created_by_id == default_user.id

    players = list(Player.objects.filter(checkin=checkin))
    assert len(players) == 1

    player = players[0]
    assert player.user_id == default_user.id
    assert player.confirmed
    assert player.notes is None
    assert player.winner is None
    assert player.rating is None


def test_add_checkin_notes(gql_client, default_user, default_game):
    executed = gql_client.execute(
        """
    mutation {
        addCheckIn(game:"%s", notes:"I liked it") {
            ok
            errors
            checkIn {id}
        }
    }"""
        % (default_game.id,),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addCheckIn"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    checkin = CheckIn.objects.get(id=resp["checkIn"]["id"])
    assert checkin.game_id == default_game.id
    assert checkin.created_by_id == default_user.id

    players = list(Player.objects.filter(checkin=checkin))
    assert len(players) == 1

    player = players[0]
    assert player.user_id == default_user.id
    assert player.confirmed
    assert player.notes == "I liked it"
    assert player.winner is None
    assert player.rating is None


def test_add_checkin_rating(gql_client, default_user, default_game):
    executed = gql_client.execute(
        """
    mutation {
        addCheckIn(game:"%s", rating:4.5) {
            ok
            errors
            checkIn {id}
        }
    }"""
        % (default_game.id,),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addCheckIn"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    checkin = CheckIn.objects.get(id=resp["checkIn"]["id"])
    assert checkin.game_id == default_game.id
    assert checkin.created_by_id == default_user.id

    players = list(Player.objects.filter(checkin=checkin))
    assert len(players) == 1

    player = players[0]
    assert player.user_id == default_user.id
    assert player.confirmed
    assert player.notes is None
    assert player.winner is None
    assert player.rating == Decimal("4.5")


def test_add_checkin_only_winners(gql_client, default_user, default_game):
    executed = gql_client.execute(
        """
    mutation {
        addCheckIn(game:"%s", winners:["%s"]) {
            ok
            errors
            checkIn {id}
        }
    }"""
        % (default_game.id, default_user.id),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addCheckIn"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    checkin = CheckIn.objects.get(id=resp["checkIn"]["id"])
    assert checkin.game_id == default_game.id
    assert checkin.created_by_id == default_user.id

    players = list(Player.objects.filter(checkin=checkin))
    assert len(players) == 1

    player = players[0]
    assert player.user_id == default_user.id
    assert player.confirmed
    assert player.notes is None
    assert player.winner is True
    assert player.rating is None


def test_add_checkin_multiple_players(
    gql_client, default_user, default_game, other_user
):
    # friendship required to add player to checkin
    Follower.objects.create(from_user=other_user, to_user=default_user)

    executed = gql_client.execute(
        """
    mutation {
        addCheckIn(game:"%s", players:["%s", "%s"], winners:["%s"], notes:"It was good", rating:5.0) {
            ok
            errors
            checkIn {id}
        }
    }"""
        % (default_game.id, default_user.id, other_user.id, default_user.id),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addCheckIn"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    checkin = CheckIn.objects.get(id=resp["checkIn"]["id"])
    assert checkin.game_id == default_game.id
    assert checkin.created_by_id == default_user.id

    players = sorted(
        Player.objects.filter(checkin=checkin), key=lambda x: x.id == default_user.id
    )
    assert len(players) == 2

    player = players[0]
    assert player.user_id == default_user.id
    assert player.confirmed
    assert player.notes == "It was good"
    assert player.winner is True
    assert player.rating == Decimal("5.0")

    player = players[1]
    assert player.user_id == other_user.id
    assert player.confirmed
    assert player.notes is None
    assert player.winner is False
    assert player.rating is None
