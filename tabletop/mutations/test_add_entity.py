from tabletop.models import Entity


def test_add_entity(gql_client, default_user):
    executed = gql_client.execute(
        """
    mutation {
        addEntity(name:"Pirahna Games") {
            ok
            errors
            entity {id}
        }
    }""",
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addEntity"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    entity = Entity.objects.get(id=resp["entity"]["id"])
    assert entity.name == "Pirahna Games"
    assert entity.created_by_id == default_user.id
    assert not entity.confirmed
