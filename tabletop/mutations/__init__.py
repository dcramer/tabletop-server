import graphene

from .add_checkin import AddCheckin
from .add_game import AddGame
from .add_player import AddPlayer
from .add_publisher import AddPublisher
from .add_tag import AddTag
from .follow import Follow
from .login import Login
from .unfollow import Unfollow
from .update_checkin import UpdateCheckin


class RootMutation(graphene.ObjectType):
    addCheckin = AddCheckin.Field()
    addGame = AddGame.Field()
    addPlayer = AddPlayer.Field()
    addPublisher = AddPublisher.Field()
    addTag = AddTag.Field()
    follow = Follow.Field()
    login = Login.Field()
    unfollow = Unfollow.Field()
    updateCheckin = UpdateCheckin.Field()
