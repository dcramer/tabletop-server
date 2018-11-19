from tabletop.models import Collection


def test_add_collection(gql_client, default_user):
    executed = gql_client.execute(
        """
    mutation {
        addCollection(name:"My Games") {
            ok
            errors
            collection {id}
        }
    }""",
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addCollection"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    collection = Collection.objects.get(id=resp["collection"]["id"])
    assert collection.name == "My Games"
    assert collection.created_by_id == default_user.id

    assert list(collection.games.all()) == []


def test_add_collection_with_games(gql_client, default_user, default_game):
    executed = gql_client.execute(
        """
    mutation {
        addCollection(name:"My Games", games:["%s"]) {
            ok
            errors
            collection {id}
        }
    }"""
        % (str(default_game.id),),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addCollection"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    collection = Collection.objects.get(id=resp["collection"]["id"])
    assert collection.name == "My Games"
    assert collection.created_by_id == default_user.id

    assert list(collection.games.all()) == [default_game]
