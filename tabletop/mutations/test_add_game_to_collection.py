from tabletop import factories


def test_add_game_to_collection(gql_client, default_collection, default_user):
    new_game = factories.GameFactory.create()

    executed = gql_client.execute(
        """
    mutation {
        addGameToCollection(collection:"%s", game:"%s") {
            ok
            errors
        }
    }"""
        % (str(default_collection.id), str(new_game.id)),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addGameToCollection"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    assert new_game in list(default_collection.games.all())
