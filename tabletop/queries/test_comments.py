from tabletop.models import Comment


def test_comments_for_checkin(gql_client, default_user, default_checkin):
    comment = Comment.objects.create(
        created_by=default_user, checkin=default_checkin, text="Hi :)"
    )

    executed = gql_client.execute(
        """{ comments(checkin:"%s") { id } }""" % (default_checkin.id,),
        user=default_user,
    )
    assert not executed.get("errors")
    assert executed["data"]["comments"] == [{"id": str(comment.id)}]
