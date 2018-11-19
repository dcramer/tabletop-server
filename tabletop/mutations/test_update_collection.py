from tabletop import factories
from tabletop.models import Collection


def test_update_collection(gql_client, default_collection, default_user):
    existing_games = list(default_collection.games.all())

    executed = gql_client.execute(
        """
    mutation {
        updateCollection(collection:"%s", name:"Updated Collection") {
            ok
            errors
            collection { id }
        }
    }"""
        % (str(default_collection.id),),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["updateCollection"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    collection = Collection.objects.get(id=resp["collection"]["id"])
    assert collection.name == "Updated Collection"

    assert list(collection.games.all()) == existing_games


def test_update_collection_with_description(
    gql_client, default_collection, default_user
):
    existing_games = list(default_collection.games.all())

    executed = gql_client.execute(
        """
    mutation {
        updateCollection(collection:"%s", description:"Test") {
            ok
            errors
            collection { id }
        }
    }"""
        % (str(default_collection.id),),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["updateCollection"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    collection = Collection.objects.get(id=resp["collection"]["id"])
    assert collection.description == "Test"

    assert list(collection.games.all()) == existing_games


def test_update_collection_with_games(gql_client, default_collection, default_user):
    new_game = factories.GameFactory.create()
    executed = gql_client.execute(
        """
    mutation {
        updateCollection(collection:"%s", games:["%s"]) {
            ok
            errors
            collection { id }
        }
    }"""
        % (str(default_collection.id), str(new_game.id)),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["updateCollection"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    collection = Collection.objects.get(id=resp["collection"]["id"])
    assert list(collection.games.all()) == [new_game]
