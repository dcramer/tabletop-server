from server.games.models import Game, Publisher, Tag


def test_add_publisher(gql_client, default_user):
    executed = gql_client.execute(
        """
    mutation {
        addPublisher(name:"Pirahna Games") {
            ok
            errors
            publisher {id}
        }
    }""",
        user=default_user,
    )
    resp = executed["data"]["addPublisher"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    publisher = Publisher.objects.get(id=resp["publisher"]["id"])
    assert publisher.name == "Pirahna Games"
    assert publisher.created_by_id == default_user.id
    assert not publisher.confirmed


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
    assert not game.confirmed


def test_add_tag(gql_client, default_user):
    executed = gql_client.execute(
        """
    mutation {
        addTag(name:"Party") {
            ok
            errors
            tag {id}
        }
    }""",
        user=default_user,
    )
    resp = executed["data"]["addTag"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    tag = Tag.objects.get(id=resp["tag"]["id"])
    assert tag.name == "Party"
    assert tag.created_by_id == default_user.id
    assert not tag.confirmed
