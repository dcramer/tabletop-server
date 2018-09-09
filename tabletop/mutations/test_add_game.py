from tabletop.models import EntityType, Game, GameEntity


def test_add_game(gql_client, default_user, default_publisher):
    executed = gql_client.execute(
        """
    mutation {
        addGame(name:"Fight Club XI", entities:[{name:"%s", type:publisher}]) {
            ok
            errors
            game {id}
        }
    }"""
        % (default_publisher.name,),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addGame"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    game = Game.objects.get(id=resp["game"]["id"])
    assert game.name == "Fight Club XI"
    assert game.created_by_id == default_user.id

    entities = list(GameEntity.objects.filter(game=game))
    assert len(entities) == 1
    assert entities[0].entity_id == default_publisher.id
    assert entities[0].game_id == game.id
    assert entities[0].type == EntityType.publisher
