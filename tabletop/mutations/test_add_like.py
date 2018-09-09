from tabletop.models import Like


def test_add_like_as_player(gql_client, default_user, default_checkin):
    executed = gql_client.execute(
        """
    mutation {
        addLike(checkin:"%s") {
            ok
            errors
            like {id}
        }
    }"""
        % (default_checkin.id,),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addLike"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    like = Like.objects.get(id=resp["like"]["id"])
    assert like.checkin_id == default_checkin.id
    assert like.created_by_id == default_user.id
