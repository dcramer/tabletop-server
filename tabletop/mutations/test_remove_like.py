from tabletop.models import Like


def test_remove_like_as_author(gql_client, default_user, default_checkin):
    Like.objects.create(created_by=default_user, checkin=default_checkin)

    executed = gql_client.execute(
        """
    mutation {
        removeLike(checkin:"%s") {
            ok
            errors
        }
    }"""
        % (default_checkin.id,),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["removeLike"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    assert not Like.objects.filter(
        created_by=default_user, checkin=default_checkin
    ).exists()


def test_remove_like_as_author_noop(gql_client, default_user, default_checkin):
    Like.objects.create(created_by=default_user, checkin=default_checkin)

    executed = gql_client.execute(
        """
    mutation {
        removeLike(checkin:"%s") {
            ok
            errors
        }
    }"""
        % (default_checkin.id,),
        user=default_user,
    )
    assert not executed.get("errors")
    resp = executed["data"]["removeLike"]
    assert resp["errors"] is None
    assert resp["ok"] is True

    assert not Like.objects.filter(
        created_by=default_user, checkin=default_checkin
    ).exists()
