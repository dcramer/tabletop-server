import graphene

from .add_checkin import AddCheckin
from .add_entity import AddEntity
from .add_game import AddGame
from .add_player import AddPlayer
from .add_tag import AddTag
from .follow import Follow
from .login import Login
from .unfollow import Unfollow
from .update_checkin import UpdateCheckin


class RootMutation(graphene.ObjectType):
    addCheckin = AddCheckin.Field()
    addEntity = AddEntity.Field()
    addGame = AddGame.Field()
    addPlayer = AddPlayer.Field()
    addTag = AddTag.Field()
    follow = Follow.Field()
    login = Login.Field()
    unfollow = Unfollow.Field()
    updateCheckin = UpdateCheckin.Field()
