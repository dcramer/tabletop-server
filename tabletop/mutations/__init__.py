import graphene

from .add_checkin import AddCheckin
from .add_collection import AddCollection
from .add_comment import AddComment
from .add_entity import AddEntity
from .add_game import AddGame
from .add_like import AddLike
from .add_player import AddPlayer
from .add_tag import AddTag
from .follow import Follow
from .login import Login
from .remove_comment import RemoveComment
from .remove_like import RemoveLike
from .unfollow import Unfollow
from .update_checkin import UpdateCheckin


class RootMutation(graphene.ObjectType):
    addCheckin = AddCheckin.Field()
    addCollection = AddCollection.Field()
    addComment = AddComment.Field()
    addLike = AddLike.Field()
    addEntity = AddEntity.Field()
    addGame = AddGame.Field()
    addPlayer = AddPlayer.Field()
    addTag = AddTag.Field()
    follow = Follow.Field()
    login = Login.Field()
    removeComment = RemoveComment.Field()
    removeLike = RemoveLike.Field()
    unfollow = Unfollow.Field()
    updateCheckin = UpdateCheckin.Field()
