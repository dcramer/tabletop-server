from tabletop.models import Like


def test_likes_for_checkin(gql_client, default_user, default_checkin):
    like = Like.objects.create(created_by=default_user, checkin=default_checkin)

    executed = gql_client.execute(
        """{ likes(checkin:"%s") { id } }""" % (default_checkin.id,), user=default_user
    )
    assert not executed.get("errors")
    assert executed["data"]["likes"] == [{"id": str(like.id)}]
