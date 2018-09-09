from tabletop.models import Comment


def test_add_comment_as_player(gql_client, default_user, default_checkin):
    executed = gql_client.execute(
        """
    mutation {
        addComment(text:"Hi :)", checkin:"%s") {
            ok
            errors
            comment {id}
        }
    }"""
        % (default_checkin.id,),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["addComment"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    comment = Comment.objects.get(id=resp["comment"]["id"])
    assert comment.text == "Hi :)"
    assert comment.checkin_id == default_checkin.id
    assert comment.created_by_id == default_user.id
