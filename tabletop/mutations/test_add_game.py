from tabletop.models import Game


def test_add_game(gql_client, default_user, default_publisher):
    executed = gql_client.execute(
        """
    mutation {
        addGame(name:"Fight Club XI", publisher:"%s") {
            ok
            errors
            game {id}
        }
    }"""
        % (default_publisher.id,),
        user=default_user,
    )
    resp = executed["data"]["addGame"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    game = Game.objects.get(id=resp["game"]["id"])
    assert game.name == "Fight Club XI"
    assert game.publisher_id == default_publisher.id
    assert game.created_by_id == default_user.id
