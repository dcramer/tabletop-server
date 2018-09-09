from tabletop.models import Entity, EntityType


def test_add_entity(gql_client, default_user):
    executed = gql_client.execute(
        """
    mutation {
        addEntity(name:"Pirahna Games", type:publisher) {
            ok
            errors
            entity {id}
        }
    }""",
        user=default_user,
    )
    resp = executed["data"]["addEntity"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    entity = Entity.objects.get(id=resp["entity"]["id"])
    assert entity.name == "Pirahna Games"
    assert entity.type == EntityType.publisher
    assert entity.created_by_id == default_user.id
    assert not entity.confirmed
