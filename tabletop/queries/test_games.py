from tabletop.models import Game


def test_empty_results(gql_client):
    executed = gql_client.execute("""{ games { id } }""")
    assert executed == {"data": {"games": []}}


def test_single_result(gql_client, default_game):
    executed = gql_client.execute("""{ games { id, name } }""")
    assert executed == {
        "data": {"games": [{"id": str(default_game.id), "name": default_game.name}]}
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
