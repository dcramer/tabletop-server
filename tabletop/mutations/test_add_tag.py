from tabletop.models import Tag


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
