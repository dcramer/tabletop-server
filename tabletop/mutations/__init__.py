import graphene

from .add_checkin import AddCheckin
from .add_collection import AddCollection
from .add_comment import AddComment
from .add_entity import AddEntity
from .add_game import AddGame
from .add_game_to_collection import AddGameToCollection
from .add_like import AddLike
from .add_player import AddPlayer
from .add_tag import AddTag
from .follow import Follow
from .login import Login
from .remove_comment import RemoveComment
from .remove_game_from_collection import RemoveGameFromCollection
from .remove_like import RemoveLike
from .unfollow import Unfollow
from .update_checkin import UpdateCheckin
from .update_collection import UpdateCollection


class RootMutation(graphene.ObjectType):
    addCheckin = AddCheckin.Field()
    addCollection = AddCollection.Field()
    addComment = AddComment.Field()
    addLike = AddLike.Field()
    addEntity = AddEntity.Field()
    addGame = AddGame.Field()
    addGameToCollection = AddGameToCollection.Field()
    addPlayer = AddPlayer.Field()
    addTag = AddTag.Field()
    follow = Follow.Field()
    login = Login.Field()
    removeComment = RemoveComment.Field()
    removeGameFromCollection = RemoveGameFromCollection.Field()
    removeLike = RemoveLike.Field()
    unfollow = Unfollow.Field()
    updateCheckin = UpdateCheckin.Field()
    updateCollection = UpdateCollection.Field()
