from decimal import Decimal

from tabletop.models import Game, GameRating


def test_empty_results(gql_client):
    executed = gql_client.execute("""{ games { id } }""")
    assert executed == {"data": {"games": []}}


def test_single_result(gql_client, default_game):
    executed = gql_client.execute("""{ games { id, name } }""")
    assert executed == {
        "data": {"games": [{"id": str(default_game.id), "name": default_game.name}]}
    }


def test_single_result_with_collections(
    gql_client, default_collection, default_game, default_user
):
    executed = gql_client.execute("""{ games { id, collections { id } } }""")
    assert executed == {
        "data": {"games": [{"id": str(default_game.id), "collections": []}]}
    }

    executed = gql_client.execute(
        """{ games { id, collections { id } } }""", user=default_user
    )
    assert executed == {
        "data": {
            "games": [
                {
                    "id": str(default_game.id),
                    "collections": [{"id": str(default_collection.id)}],
                }
            ]
        }
    }


def test_single_result_with_ratings(
    gql_client, default_collection, default_game, default_user
):
    executed = gql_client.execute(
        """{ games { id, rating { averageScore, totalVotes, wilsonLowerBound } } }"""
    )
    assert executed == {
        "data": {
            "games": [
                {
                    "id": str(default_game.id),
                    "rating": {
                        "averageScore": None,
                        "totalVotes": 0,
                        "wilsonLowerBound": 0.0,
                    },
                }
            ]
        }
    }

    GameRating.objects.create(game=default_game, user=default_user, rating=4)

    executed = gql_client.execute(
        """{ games { id, rating { averageScore, totalVotes, wilsonLowerBound } } }"""
    )
    assert executed == {
        "data": {
            "games": [
                {
                    "id": str(default_game.id),
                    "rating": {
                        "averageScore": Decimal("4.0"),
                        "totalVotes": 1,
                        "wilsonLowerBound": 0.036459024761289004,
                    },
                }
            ]
        }
    }


def test_query_with_result(gql_client, default_game):
    executed = gql_client.execute("""{ games(query:"Unsettlers") { id, name } }""")
    assert executed == {
        "data": {"games": [{"id": str(default_game.id), "name": default_game.name}]}
    }


def test_query_with_no_result(gql_client, default_game):
    executed = gql_client.execute("""{ games(query:"Qatan") { id, name } }""")
    assert executed == {"data": {"games": []}}


def test_id_with_result(gql_client, default_game):
    executed = gql_client.execute(
        """{ games(id:"%s") { id, name } }""" % (str(default_game.id),)
    )
    assert executed == {
        "data": {"games": [{"id": str(default_game.id), "name": default_game.name}]}
    }


def test_id_with_no_result(gql_client, default_game):
    executed = gql_client.execute(
        """{ games(id:"74451c13-2a97-42a2-b136-03af6cbb4153") { id, name } }"""
    )
    assert executed == {"data": {"games": []}}


def test_parent_with_result(gql_client, default_game):
    other_game = Game.objects.create(parent=default_game, name="An Expansion")

    executed = gql_client.execute(
        """{ games(parent:"%s") { id, name } }""" % (str(default_game.id),)
    )
    assert executed == {
        "data": {"games": [{"id": str(other_game.id), "name": other_game.name}]}
    }


def test_parent_with_no_result(gql_client, default_game):
    executed = gql_client.execute(
        """{ games(parent:"74451c13-2a97-42a2-b136-03af6cbb4153") { id, name } }"""
    )
    assert executed == {"data": {"games": []}}
