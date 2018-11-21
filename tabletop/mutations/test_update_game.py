from decimal import Decimal

from tabletop import factories


def test_update_game_with_collections(
    gql_client, default_collection, default_game, default_user
):
    new_game = factories.GameFactory.create()
    executed = gql_client.execute(
        """
    mutation {
        updateGame(game:"%s", collections:["%s"]) {
            ok
            errors
            game { id }
        }
    }"""
        % (str(new_game.id), str(default_collection.id)),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["updateGame"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    assert new_game in list(default_collection.games.all())
    assert default_game in list(default_collection.games.all())

    executed = gql_client.execute(
        """
    mutation {
        updateGame(game:"%s", collections:[]) {
            ok
            errors
            game { id }
        }
    }"""
        % (str(new_game.id),),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["updateGame"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    assert list(default_collection.games.all()) == [default_game]


def test_update_game_with_rating(gql_client, default_game, default_user):
    new_game = factories.GameFactory.create()
    executed = gql_client.execute(
        """
    mutation {
        updateGame(game:"%s", rating:5.0) {
            ok
            errors
            game { id, rating { totalVotes, averageScore, wilsonLowerBound } }
        }
    }"""
        % (str(new_game.id),),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["updateGame"]
    assert resp["errors"] is None
    assert resp["ok"] is True
    assert resp["game"]["rating"] == {
        "totalVotes": 1,
        "averageScore": Decimal("5.0"),
        "wilsonLowerBound": 0.036459024761289004,
    }
