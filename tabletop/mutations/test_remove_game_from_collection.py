def test_remove_game_from_collection(
    gql_client, default_collection, default_game, default_user
):
    executed = gql_client.execute(
        """
    mutation {
        removeGameFromCollection(collection:"%s", game:"%s") {
            ok
            errors
        }
    }"""
        % (str(default_collection.id), str(default_game.id)),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["removeGameFromCollection"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    assert list(default_collection.games.all()) == []
