from tabletop.models import Publisher


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
