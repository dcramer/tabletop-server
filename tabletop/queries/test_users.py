import pytest

from tabletop.models import Follower, User


@pytest.fixture
def other_user():
    return User.objects.create(name="Fizz Buzz", email="fizz.buzz@example.com")


def test_users_shows_self_email(gql_client, default_user):
    executed = gql_client.execute(
        """{users(query:"Reel Big", includeSelf:true) {id, email}}""", user=default_user
    )
    assert executed["data"]["users"] == [
        {"id": str(default_user.id), "email": default_user.email}
    ]


def test_users_hides_others_email(gql_client, default_user, other_user):
    executed = gql_client.execute(
        """{users(query:"Fizz", includeSelf:true) {id, email}}""", user=default_user
    )
    assert executed["data"]["users"] == [{"id": str(other_user.id), "email": None}]


def test_users_query_with_results(gql_client, default_user):
    executed = gql_client.execute(
        """{users(query:"Reel Big", includeSelf:true) {id}}""", user=default_user
    )
    assert executed["data"]["users"] == [{"id": str(default_user.id)}]


def test_users_query_nbo_results(gql_client, default_user):
    executed = gql_client.execute(
        """{users(query:"Phish", includeSelf:true) {id}}""", user=default_user
    )
    assert executed["data"]["users"] == []


def test_users_following_no_results(gql_client, default_user, other_user):
    Follower.objects.create(from_user=other_user, to_user=default_user)
    executed = gql_client.execute(
        """{users(scope:following) {id}}""", user=default_user
    )
    assert executed["data"]["users"] == []


def test_users_following_with_results(gql_client, default_user, other_user):
    Follower.objects.create(from_user=default_user, to_user=other_user)
    executed = gql_client.execute(
        """{users(scope:following) {id}}""", user=default_user
    )
    assert executed["data"]["users"] == [{"id": str(other_user.id)}]


def test_users_following_unauthenticated(gql_client, default_user, other_user):
    Follower.objects.create(from_user=default_user, to_user=other_user)
    executed = gql_client.execute("""{users(scope:following) {id}}""")
    assert executed["data"]["users"] == []


def test_users_followers_no_results(gql_client, default_user, other_user):
    Follower.objects.create(from_user=default_user, to_user=other_user)
    executed = gql_client.execute(
        """{users(scope:followers) {id}}""", user=default_user
    )
    assert executed["data"]["users"] == []


def test_users_followers_with_results(gql_client, default_user, other_user):
    Follower.objects.create(from_user=other_user, to_user=default_user)
    executed = gql_client.execute(
        """{users(scope:followers) {id}}""", user=default_user
    )
    assert executed["data"]["users"] == [{"id": str(other_user.id)}]


def test_users_followers_unauthenticated(gql_client, default_user, other_user):
    Follower.objects.create(from_user=other_user, to_user=default_user)
    executed = gql_client.execute("""{users(scope:followers) {id}}""")
    assert executed["data"]["users"] == []
